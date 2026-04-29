# Challenge A — AI Web Search Agent

An AI-powered agent that answers natural language queries using real-time web search data, powered by **Groq (Llama 3.3 70B)** and **Tavily Search API**.

---

##  Architecture Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              FastAPI Server (main_a.py)      │
│                                             │
│  POST /search  ──►  search_agent.py         │
│                         │                  │
│               ┌─────────▼──────────┐       │
│               │  1. Tavily Search  │       │
│               │  (Top 5 web pages) │       │
│               └─────────┬──────────┘       │
│                         │                  │
│               ┌─────────▼──────────┐       │
│               │  2. Extract + Parse│       │
│               │  (Title, URL,      │       │
│               │   Content ~3000ch) │       │
│               └─────────┬──────────┘       │
│                         │                  │
│               ┌─────────▼──────────┐       │
│               │  3. Groq LLM       │       │
│               │  (Summarize +      │       │
│               │   Ground Answer)   │       │
│               └─────────┬──────────┘       │
│                         │                  │
│            { answer, sources[] }           │
└─────────────────────────────────────────────┘
    │
    ▼
  index.html (3D Glass UI served at /)
```

---

##  Folder Structure

```
ai-web-search-agent/
├── .env                  ← API keys (never commit this)
├── .gitignore
├── requirements.txt      ← Python dependencies
├── search_agent.py       ← Core agent logic (Tavily + Groq)
├── main_a.py             ← FastAPI server
└── index.html            ← 3D glassmorphism frontend UI
```

---

##  Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | latest | Web server framework |
| `uvicorn` | latest | ASGI server to run FastAPI |
| `groq` | latest | Groq LLM client (Llama 3.3 70B) |
| `tavily-python` | latest | Real-time web search API |
| `python-dotenv` | latest | Load `.env` API keys |

---

##  Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A free [Groq API key](https://console.groq.com) — create account → API Keys
- A free [Tavily API key](https://tavily.com) — 1000 free searches/month

### 2. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-web-search-agent.git
cd ai-web-search-agent
```

### 3. Create a virtual environment

```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Mac / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure API keys

Create a `.env` file in the root folder:

```
GROQ_API_KEY=gsk_your_groq_key_here
TAVILY_API_KEY=tvly_your_tavily_key_here
```

### 6. Run the server

```bash
python -m uvicorn main_a:app --reload --port 8000
```

### 7. Open the UI

Visit **http://127.0.0.1:8000** in your browser.

---

##  How to Run

```bash
# Start server
python -m uvicorn main_a:app --reload --port 8000

# Test via curl
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI news today"}'

# Expected response
{
  "answer": "...",
  "sources": [
    { "title": "Article title", "url": "https://..." }
  ]
}
```

---

##  Example Input / Output

**Input:**
```
What are the latest specs of MacBook this year?
```

**Output:**
```json
{
  "answer": "The latest MacBook Pro models feature Apple's M4 family chips...",
  "sources": [
    { "title": "Apple MacBook Pro", "url": "https://apple.com/..." },
    { "title": "MacBook Review 2025", "url": "https://theverge.com/..." }
  ]
}
```

---

##  Design Decisions & Trade-offs

| Decision | Reason | Trade-off |
|---|---|---|
| **Groq over OpenAI** | Free tier, very fast inference (Llama 3.3 70B) | Rate limits on free plan (100K tokens/day) |
| **Tavily over SerpAPI** | Purpose-built for LLMs, returns clean structured data | 1000 free searches/month limit |
| **Truncate content to 3000 chars** | Prevents exceeding Groq context window | May miss info from very long articles |
| **FastAPI over Flask** | Async support, auto-generated docs at `/docs` | Slightly more setup than Flask |
| **Serve UI from FastAPI** | Single port, no CORS issues | Not a separate frontend deployment |

---

##  API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend UI |
| `POST` | `/search` | Main search + answer endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Auto-generated Swagger UI |

---

##  .gitignore

Make sure your `.env` is never committed:

```
.env
venv/
__pycache__/
*.pyc
```
