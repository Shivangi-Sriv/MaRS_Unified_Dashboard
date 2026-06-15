"""
FastAPI backend.

Endpoints:
  POST /chat   -> { message }            => { answer, tools_used }   (AI + MCP)
  GET  /books  -> library catalog        (for the dashboard card)
  GET  /events -> upcoming events        (for the dashboard card)
  GET  /menu   -> today's menu           (for the dashboard card)

The /chat route is the AI path; the GET routes just serve raw data so the
dashboard cards have something to show without invoking the model.

Run with:  uvicorn main:app --reload --port 8000
"""
import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import ask

DATA = Path(__file__).parent / "data"

app = FastAPI(title="Campus Intelligence API")

# Allow the Next.js dev server (localhost:3000) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatIn(BaseModel):
    message: str


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/chat")
async def chat(body: ChatIn):
    return await ask(body.message)


@app.get("/books")
def books():
    return json.loads((DATA / "books.json").read_text())


@app.get("/events")
def events():
    return json.loads((DATA / "events.json").read_text())


# @app.get("/menu")
# def menu():
#     return json.loads((DATA / "menu.json").read_text())
@app.get("/menu")
def menu():
    data = json.loads((DATA / "menu.json").read_text())

    today = datetime.now().strftime("%A")

    return {
        "day": today,
        "breakfast": data[today]["breakfast"],
        "lunch": data[today]["lunch"],
        "dinner": data[today]["dinner"],
    }