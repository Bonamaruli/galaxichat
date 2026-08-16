"""Endpoint riwayat percakapan."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas import ConversationDetail, ConversationSummary, MessageResponse
from app.core.database import get_db
from app.models.user import User
from app.services import history

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
def list_all(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationSummary]:
    return [ConversationSummary(**row) for row in history.list_conversations(db, user.id)]


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_one(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationDetail:
    conversation = history.get_conversation(db, user.id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")

    messages = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=json.loads(m.sources_json) if m.sources_json else [],
            created_at=m.created_at,
        )
        for m in conversation.messages
    ]

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=messages,
    )


@router.delete("/{conversation_id}", status_code=204)
def delete_one(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    conversation = history.get_conversation(db, user.id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan.")

    db.delete(conversation)
    db.commit()