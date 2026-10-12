"""Company Brain API.   uvicorn api.main:app --port 8000

  POST /ask      Authorization: Bearer <token>   {"question": "..."}
  GET  /ledger   Authorization: Bearer <admin token>
  GET  /         the asker-switcher page

Ingest is a command, not a route:  python -m ingest.run_sf <path>
"""
import os, pathlib, threading
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from core import gate, ledger
from core.ask import ask

ADMIN_TOKEN = os.environ.get("BRAIN_ADMIN_TOKEN", "demo-admin")
UI = pathlib.Path(__file__).resolve().parent.parent / "ui" / "index.html"
app = FastAPI(title="Company Brain")

class Ask(BaseModel):
    question: str

def bearer(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Bearer token required")
    return authorization[7:].strip()

@app.on_event("startup")
def startup():
    threading.Thread(target=gate.warm, daemon=True).start()     # open the per-role sessions ahead of the first question

@app.post("/ask")
def ask_route(body: Ask, authorization: Optional[str] = Header(None)):
    if not body.question.strip():
        raise HTTPException(400, "Empty question")
    out = ask(bearer(authorization), body.question.strip())
    if out["outcome"] == "unauthorized":
        raise HTTPException(401, "Unknown token")
    return out

@app.get("/ledger")
def ledger_route(authorization: Optional[str] = Header(None), limit: int = 30):
    if bearer(authorization) != ADMIN_TOKEN:
        raise HTTPException(403, "Admin token required")
    return ledger.read(min(limit, 200))

@app.get("/", response_class=HTMLResponse)
def index():
    return UI.read_text()
