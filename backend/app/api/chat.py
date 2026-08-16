from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.core.database import get_db
from app.models.user import User
from app.services import history
from app.services.rag import rag_service

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int | None = None


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
    conversation_id: int | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        result = rag_service.answer(request.message)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Gagal memproses pertanyaan: {error}",
        )

    conversation_id = None

    # Riwayat hanya disimpan bila pengguna sudah masuk.
    if user is not None:
        conversation = history.get_or_create_conversation(
            db, user.id, request.conversation_id, request.message
        )
        history.save_exchange(
            db,
            conversation,
            question=request.message,
            answer=result["answer"],
            sources=result["sources"],
        )
        conversation_id = conversation.id

    return ChatResponse(**result, conversation_id=conversation_id)