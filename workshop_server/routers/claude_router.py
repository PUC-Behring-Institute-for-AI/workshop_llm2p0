"""
Claude Router
-------------
Proxies requests to the Anthropic API.
The API key lives in .env — participants never see it.

Exposes:
  POST /api/claude/chat         — single-turn or multi-turn chat
  POST /api/claude/chat/stream  — streaming chat (SSE)
  GET  /api/claude/models       — available Claude models for this workshop
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import httpx
import json
import os

router = APIRouter()

CLAUDE_MODEL_DEFAULT = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-6",
]

CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))


def _anthropic_headers() -> dict:
    """Build headers fresh each call so the key is read after load_dotenv() runs."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    return {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def _check_api_key():
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key or key == "sk-ant-your-key-here":
        raise HTTPException(
            status_code=503,
            detail="Anthropic API key not configured. Add ANTHROPIC_API_KEY to your .env file."
        )


# ── Request models ───────────────────────────────────────────────────────────

class ClaudeMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ClaudeChatRequest(BaseModel):
    messages: list[ClaudeMessage]
    model: Optional[str] = None            # if None, falls back to CLAUDE_MODEL_DEFAULT
    system: Optional[str] = None
    temperature: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: Optional[int] = None


def _build_payload(req: ClaudeChatRequest) -> dict:
    max_tok = min(req.max_tokens or CLAUDE_MAX_TOKENS, CLAUDE_MAX_TOKENS)
    model = req.model if req.model in CLAUDE_MODELS else CLAUDE_MODEL_DEFAULT
    payload = {
        "model": model,
        "max_tokens": max_tok,
        "temperature": req.temperature,
        "messages": [m.model_dump() for m in req.messages],
    }
    if req.system:
        payload["system"] = req.system
    return payload


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/health")
async def claude_health():
    """
    Diagnose the Claude API connection step by step.
    Returns a structured status so the UI can show exactly what's wrong.
    """
    key = os.getenv("ANTHROPIC_API_KEY", "")

    # Step 1 — is the key present at all?
    if not key or key == "sk-ant-your-key-here":
        return {
            "ok": False,
            "step": "api_key",
            "message": "ANTHROPIC_API_KEY not set in .env — the server cannot authenticate.",
        }

    # Step 2 — does the key look plausible?
    if not key.startswith("sk-ant-"):
        return {
            "ok": False,
            "step": "api_key_format",
            "message": f"Key loaded but looks wrong (starts with '{key[:10]}...'). Expected 'sk-ant-...'.",
        }

    # Step 3 — can we reach the Anthropic API at all?
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=_anthropic_headers(),
                json={
                    "model": CLAUDE_MODEL_DEFAULT,
                    "max_tokens": 16,
                    "messages": [{"role": "user", "content": "reply with the word ok"}],
                },
            )
    except httpx.ConnectError:
        return {
            "ok": False,
            "step": "network",
            "message": "Cannot reach api.anthropic.com — check internet connection.",
        }
    except httpx.TimeoutException:
        return {
            "ok": False,
            "step": "network",
            "message": "Request to api.anthropic.com timed out after 8s.",
        }

    # Step 4 — did Anthropic accept the key?
    if r.status_code == 401:
        return {
            "ok": False,
            "step": "auth",
            "message": "Anthropic rejected the key (401 Unauthorized). Check ANTHROPIC_API_KEY in .env.",
        }

    if r.status_code == 403:
        return {
            "ok": False,
            "step": "auth",
            "message": "Anthropic returned 403 Forbidden. The key may lack permissions.",
        }

    if r.status_code != 200:
        try:
            detail = r.json().get("error", {}).get("message", r.text)
        except Exception:
            detail = r.text
        return {
            "ok": False,
            "step": "api_error",
            "message": f"Anthropic returned HTTP {r.status_code}: {detail}",
        }

    # All good
    data = r.json()
    return {
        "ok": True,
        "step": "ok",
        "message": "Connected successfully.",
        "model": data.get("model", CLAUDE_MODEL_DEFAULT),
        "key_hint": f"{key[:8]}...{key[-4:]}",
    }


@router.get("/models")
async def list_models():
    """Return all available Claude models for this workshop."""
    return {"models": CLAUDE_MODELS, "default": CLAUDE_MODEL_DEFAULT}


@router.post("/chat")
async def claude_chat(req: ClaudeChatRequest):
    """
    Single or multi-turn chat with Claude.
    System prompt is accepted from the client but the API key never leaves the server.
    """
    _check_api_key()
    payload = _build_payload(req)

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=_anthropic_headers(),
            json=payload,
        )
        if r.status_code != 200:
            # Surface the Anthropic error message but never the key
            detail = r.json().get("error", {}).get("message", r.text)
            raise HTTPException(status_code=r.status_code, detail=detail)
        data = r.json()

    return {
        "text": data["content"][0]["text"],
        "model": data["model"],
        "input_tokens": data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
        "stop_reason": data["stop_reason"],
    }


@router.post("/chat/stream")
async def claude_chat_stream(req: ClaudeChatRequest):
    """Streaming chat with Claude (Server-Sent Events)."""
    _check_api_key()
    payload = _build_payload(req)
    payload["stream"] = True

    async def generate():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=_anthropic_headers(),
                json=payload,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        raw = line[6:]
                        if raw == "[DONE]":
                            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                            break
                        try:
                            event = json.loads(raw)
                            etype = event.get("type")

                            if etype == "content_block_delta":
                                token = event.get("delta", {}).get("text", "")
                                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

                            elif etype == "message_delta":
                                usage = event.get("usage", {})
                                stop_reason = event.get("delta", {}).get("stop_reason", "")
                                yield f"data: {json.dumps({'token': '', 'done': True, 'usage': usage, 'stop_reason': stop_reason})}\n\n"

                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")
