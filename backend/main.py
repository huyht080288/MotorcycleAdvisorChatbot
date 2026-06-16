import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import admin, chat, site
from backend.ai.vectorizer import model

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(title="Motorcycle Advisor Chatbot", version="1.0.0")
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(site.router)

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.on_event("startup")
def startup() -> None:
    threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    model.threshold = threshold
    model.load()
