# LLM Workshop Server

A local workshop server with two tools for hands-on LLM exploration.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- An Anthropic API key (for Tool B)

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Pull models into Ollama

```bash
# Base/completion models (the "honest machine")
ollama pull llama3.2:1b          # fast, good for live demo
ollama pull llama3.2:3b          # better quality, still fast on M-series
ollama pull falcon:7b            # raw text completion model

# Instruct-tuned versions (RLHF applied)
ollama pull llama3.2:1b-instruct
ollama pull llama3.2:3b-instruct
```

> **Workshop tip**: pull models *before* the event. Each is 1–4GB.

### 4. Start Ollama

```bash
ollama serve
```

### 5. Start the workshop server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Participants connect via: `http://<your-local-ip>:8000`

To find your local IP on macOS:
```bash
ipconfig getifaddr en0   # wifi
ipconfig getifaddr en1   # ethernet
```

---

## Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Landing page | `/` | Participants choose their tool |
| Raw Explorer | `/explorer` | Ollama — completion vs instruct, all parameters exposed |
| Chatbot Explorer | `/chatbot` | Claude API — system prompt editing, presets, corruption demos |

---

## Recommended models for the workshop

| Model | Type | Purpose |
|-------|------|---------|
| `llama3.2:1b` | Base completion | "The raw machine" — shows pure next-token prediction |
| `llama3.2:1b-instruct` | Chat/instruct | Same architecture, RLHF applied — dramatic difference |
| `llama3.2:3b` | Base completion | Better quality base model for comparison |
| `falcon:7b` | Base completion | Demonstrates a different model family |

---

## Network setup (important!)

Many venue wifi networks block device-to-device traffic.
**Bring a travel router** (e.g. TP-Link TL-WR902AC) or use your phone hotspot.

Test before the session:
- Connect your MacBook to the hotspot/router
- Connect a second device to the same network
- Verify `http://<macbook-ip>:8000` is reachable from the second device

---

## API key safety

The `ANTHROPIC_API_KEY` in `.env` is never sent to the browser.
All Claude API calls are proxied through the FastAPI backend.
Participants only interact with `/api/claude/...` endpoints which forward
requests server-side.
