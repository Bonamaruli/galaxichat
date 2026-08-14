from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.config import settings
from app.api.classify import router as classify_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Chatbot pengetahuan alam semesta berbasis RAG",
)

app.include_router(chat_router)
app.include_router(classify_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict:
    """Endpoint sederhana untuk memastikan server hidup."""
    return {"status": "ok", "app": settings.APP_NAME}