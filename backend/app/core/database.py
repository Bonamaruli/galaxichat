"""Koneksi database dan sesi SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# check_same_thread=False diperlukan karena SQLite secara default
# melarang satu koneksi dipakai lintas thread, sementara FastAPI
# menangani permintaan di thread yang berbeda-beda.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Kelas dasar untuk semua model tabel."""


def get_db():
    """Menyediakan sesi database per permintaan, lalu menutupnya."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()