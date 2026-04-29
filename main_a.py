import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from search_agent import search_and_answer

app = FastAPI(title="AI Web Search Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: QueryRequest):
    try:
        result = search_and_answer(request.query)
        return result
    except Exception as e:
        # Never let unhandled exceptions become 500s with no message
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h2 style='font-family:sans-serif;padding:2rem'>index.html not found at: " + html_path + "</h2>")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/health")
async def health():
    return {"status": "running"}