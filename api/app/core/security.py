"""Auth-utilities: password-hashing + JWT-tokens."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# I produktion: læs JWT_SECRET fra env. For lokal dev bruger vi en konstant.
JWT_SECRET = "dev-orbisx-secret-change-in-production-please-do"
JWT_ALG = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # 7 dage


def hash_password(plain: str) -> str:
    # bcrypt har 72-byte grænse — vi truncerer eksplicit
    plain_bytes = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(plain_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(plain_bytes, hashed.encode("utf-8"))


def create_token(user_id: int, tenant_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "tid": tenant_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None
