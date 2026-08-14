from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag import rag_service

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class Source(BaseModel):
    source: str
    url: str
    heading: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    chunks_used: int
    top_similarity: float


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = rag_service.answer(request.message)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Gagal memproses pertanyaan: {error}",
        )

    return ChatResponse(**result)