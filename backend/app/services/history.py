"""Penyimpanan dan pengambilan riwayat percakapan."""

import json

from sqlalchemy.orm import Session

from app.models.user import Conversation, Message

TITLE_MAX_CHARS = 60
PREVIEW_MAX_CHARS = 90


def make_title(first_question: str) -> str:
    """Judul percakapan diambil dari pertanyaan pertama."""
    clean = first_question.strip().replace("\n", " ")
    if len(clean) <= TITLE_MAX_CHARS:
        return clean
    return clean[:TITLE_MAX_CHARS].rsplit(" ", 1)[0] + "..."


def get_or_create_conversation(
    db: Session, user_id: int, conversation_id: int | None, question: str
) -> Conversation:
    """Mengambil percakapan milik pengguna, atau membuat yang baru."""
    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,   # cegah akses milik orang lain
            )
            .first()
        )
        if conversation is not None:
            return conversation

    conversation = Conversation(user_id=user_id, title=make_title(question))
    db.add(conversation)
    db.flush()
    return conversation


def save_exchange(
    db: Session,
    conversation: Conversation,
    question: str,
    answer: str,
    sources: list[dict],
) -> None:
    """Menyimpan sepasang pesan pengguna dan jawaban asisten."""
    db.add(Message(
        conversation_id=conversation.id,
        role="user",
        content=question,
    ))
    db.add(Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        sources_json=json.dumps(sources, ensure_ascii=False) if sources else None,
    ))
    db.commit()


def list_conversations(db: Session, user_id: int) -> list[dict]:
    """Daftar percakapan pengguna, terbaru di atas."""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    result = []
    for conversation in conversations:
        messages = conversation.messages
        last = messages[-1].content if messages else ""
        preview = last[:PREVIEW_MAX_CHARS] + ("..." if len(last) > PREVIEW_MAX_CHARS else "")

        result.append({
            "id": conversation.id,
            "title": conversation.title,
            "preview": preview,
            "message_count": len(messages),
            "updated_at": conversation.updated_at,
        })

    return result


def get_conversation(db: Session, user_id: int, conversation_id: int) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )