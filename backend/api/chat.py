from pydantic import BaseModel, Field

from fastapi import APIRouter

from backend.ai.vectorizer import model

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


@router.post("/chat")
def chat(body: ChatRequest) -> dict:
    result = model.predict(body.message.strip())
    return {
        "reply": result["answer"],
        "confidence": round(result["confidence"], 4),
        "matched_question": result["matched_question"],
    }


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "model_ready": model.is_ready()}
