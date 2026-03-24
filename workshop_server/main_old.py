"""
LLM Workshop Server
-------------------
Run with:  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Participants connect via:  http://<your-local-ip>:8000
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import ollama_router, claude_router
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into os.environ before routers import their config

app = FastAPI(title="LLM Workshop", version="1.0.0")

# Allow all origins on the local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(ollama_router.router, prefix="/api/ollama", tags=["ollama"])
app.include_router(claude_router.router, prefix="/api/claude", tags=["claude"])


@app.get("/", response_class=HTMLResponse)
async def landing():
    """Workshop landing page — participants choose their tool."""
    with open("templates/index.html") as f:
        return f.read()


@app.get("/explorer", response_class=HTMLResponse)
async def tool_a():
    """Tool A: Raw Ollama Explorer."""
    with open("templates/explorer.html") as f:
        return f.read()


@app.get("/chatbot", response_class=HTMLResponse)
async def tool_b():
    """Tool B: Claude Chatbot Explorer."""
    with open("templates/chatbot.html") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "ok"}
