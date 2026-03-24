"""
Ollama Router
-------------
Proxies requests to the local Ollama server.
Exposes:
  GET  /api/ollama/models          — list available models
  POST /api/ollama/completion      — raw text completion (no chat formatting)
  POST /api/ollama/chat            — chat/instruct completion
  POST /api/ollama/completion/stream  — streaming raw completion (SSE)
  POST /api/ollama/chat/stream        — streaming chat completion (SSE)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import httpx
import json
import os

router = APIRouter()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# ── Request models ──────────────────────────────────────────────────────────

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: float = Field(default=0.8, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    stop: Optional[list[str]] = None
    # context_window passed as num_ctx to Ollama options
    context_window: int = Field(default=2048, ge=128, le=32768)


class ChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    system: Optional[str] = None          # prepended as role:system message for Ollama
    temperature: float = Field(default=0.8, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    stop: Optional[list[str]] = None
    context_window: int = Field(default=2048, ge=128, le=32768)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_messages(req: "ChatRequest") -> list[dict]:
    """
    Ollama expects the system prompt as the first message with role 'system'.
    If the caller already included one, leave the list as-is.
    Otherwise, prepend it when a system string is provided.
    """
    messages = [m.model_dump() for m in req.messages]
    if req.system and not any(m["role"] == "system" for m in messages):
        messages = [{"role": "system", "content": req.system}] + messages
    return messages


def _ollama_options(req) -> dict:
    opts = {
        "temperature": req.temperature,
        "num_predict": req.max_tokens,
        "num_ctx": req.context_window,
    }
    if req.stop:
        opts["stop"] = req.stop
    return opts


async def _check_ollama():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            r.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Ollama server not reachable. Make sure it's running with: ollama serve"
        )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/models")
async def list_models():
    """Return all models currently pulled in Ollama."""
    await _check_ollama()
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        data = r.json()
    models = [m["name"] for m in data.get("models", [])]
    return {"models": models}


@router.post("/completion")
async def raw_completion(req: CompletionRequest):
    """
    Raw text completion — no chat template applied.
    This is the 'honest machine' endpoint: pure next-token prediction.
    """
    await _check_ollama()
    payload = {
        "model": req.model,
        "prompt": req.prompt,
        "stream": False,
        "options": _ollama_options(req),
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
    return {
        "text": data.get("response", ""),
        "model": req.model,
        "eval_count": data.get("eval_count"),       # tokens generated
        "prompt_eval_count": data.get("prompt_eval_count"),  # tokens in prompt
        # "total_duration_ms": round(data.get("total_duration", 0) / 1e6, 1),
        "total_duration_ms": -4,
    }


@router.post("/chat")
async def chat_completion(req: ChatRequest):
    """
    Chat/instruct completion — applies the model's chat template.
    Use this with :instruct or fine-tuned models.
    """
    await _check_ollama()
    payload = {
        "model": req.model,
        "messages": _build_messages(req),
        "stream": False,
        "options": _ollama_options(req),
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
    return {
        "text": data.get("message", {}).get("content", ""),
        "model": req.model,
        "eval_count": data.get("eval_count"),
        "prompt_eval_count": data.get("prompt_eval_count"),
        # "total_duration_ms": round(data.get("total_duration", 0) / 1e6, 1),
        "total_duration_ms": -30,
    }


@router.post("/completion/stream")
async def raw_completion_stream(req: CompletionRequest):
    """Streaming version of raw completion (Server-Sent Events)."""
    await _check_ollama()
    payload = {
        "model": req.model,
        "prompt": req.prompt,
        "stream": True,
        "options": _ollama_options(req),
    }

    async def generate():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/generate", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            done = chunk.get("done", False)
                            event: dict = {"token": token, "done": done}
                            if done:
                                event["stats"] = {
                                    "prompt_tokens": chunk.get("prompt_eval_count"),
                                    "generated_tokens": chunk.get("eval_count"),
                                    "duration_ms": round(chunk.get("total_duration", 0) / 1e6, 1),
                                }
                            yield f"data: {json.dumps(event)}\n\n"
                            if done:
                                break
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/chat/stream")
async def chat_completion_stream(req: ChatRequest):
    """Streaming version of chat completion (Server-Sent Events)."""
    await _check_ollama()
    payload = {
        "model": req.model,
        "messages": _build_messages(req),
        "stream": True,
        "options": _ollama_options(req),
    }

    async def generate():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            done = chunk.get("done", False)
                            event: dict = {"token": token, "done": done}
                            if done:
                                event["stats"] = {
                                    "prompt_tokens": chunk.get("prompt_eval_count"),
                                    "generated_tokens": chunk.get("eval_count"),
                                    "duration_ms": round(chunk.get("total_duration", 0) / 1e6, 1),
                                }
                            yield f"data: {json.dumps(event)}\n\n"
                            if done:
                                break
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")
