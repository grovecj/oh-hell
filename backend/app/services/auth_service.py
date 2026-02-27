from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings


def create_token(user_id: str, user_type: str = "anon", name: str = "Anonymous") -> str:
    payload = {
        "sub": user_id,
        "type": user_type,
        "name": name,
        "exp": datetime.now(UTC) + timedelta(hours=settings.jwt_expiration_hours),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def create_anonymous_user() -> tuple[str, str]:
    """Create an anonymous user and return (user_id, token)."""
    user_id = str(uuid.uuid4())
    token = create_token(user_id, "anon", f"Player-{user_id[:6].upper()}")
    return user_id, token
