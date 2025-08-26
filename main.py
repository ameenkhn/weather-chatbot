# main.py
import os
from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.weather_agent import WeatherAgent

load_dotenv()

# app
app = FastAPI(title="Weather Chatbot (local)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# static folder
STATIC_DIR = Path(__file__).parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# serve index.html at root
@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found in /static")
    return FileResponse(index_file)

# chat models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

# in-memory conversations
conversations: Dict[str, List[Dict[str, str]]] = {}

# agent
weather_agent = WeatherAgent()

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"
    history = conversations.setdefault(session_id, [])
    # keep last 10 turns
    history = history[-10:]
    conversations[session_id] = history

    # add user message
    history.append({"role": "user", "content": req.message})

    # get response (OpenWeather + Gemini)
    result = await weather_agent.get_response(req.message, history)

    # append assistant's reply to history if present
    response_text = result.get("response", "")
    history.append({"role": "assistant", "content": response_text})
    # update stored history
    conversations[session_id] = history

    # ensure return contains expected keys for the frontend
    return {
        "response": result.get("response", ""),
        "tools_used": result.get("tools_used", [])
    }

@app.delete("/chat/history/{session_id}")
async def clear_history(session_id: str):
    conversations.pop(session_id, None)
    return {"status": "cleared"}