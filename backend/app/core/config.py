import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Settings:
    """Menyimpan semua konfigurasi aplikasi di satu tempat."""

    APP_NAME: str = "Galaxichat"
    APP_VERSION: str = "0.1.0"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Mengatur seberapa "kreatif" jawaban model.
    TEMPERATURE: float = 0.3

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "galaxichat_docs")
    CHROMA_DIR: str = str(Path(__file__).resolve().parents[2] / "data" / "vectordb")

    SYSTEM_PROMPT: str = (
        "Kamu adalah Galaxichat, asisten yang menjelaskan ilmu astronomi "
        "dan alam semesta dalam bahasa Indonesia yang jelas dan mudah dipahami. "
        "Jawab dengan ringkas namun akurat. "
        "Jika kamu tidak yakin akan suatu informasi, katakan terus terang "
        "bahwa kamu tidak yakin, jangan mengarang."
    )

    def validate(self) -> None:
        """Memastikan konfigurasi wajib sudah terisi sebelum aplikasi jalan."""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY kosong. Pastikan file .env ada di folder backend."
            )


settings = Settings()
settings.validate()