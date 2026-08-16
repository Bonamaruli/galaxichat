"""Hashing password dan pembuatan token JWT."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings



def hash_password(password: str) -> str:
    """Mengubah password menjadi hash yang tidak dapat dibalik."""
    # bcrypt hanya memproses 72 byte pertama; dipotong eksplisit
    # agar perilakunya jelas dan tidak memicu error.
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Memeriksa apakah password cocok dengan hash tersimpan."""
    raw = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, email: str) -> str:
    """Membuat token yang menandai sesi login pengguna."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict | None:
    """Memverifikasi token. Mengembalikan None bila tidak sah atau kedaluwarsa."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None