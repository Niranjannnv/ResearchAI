"""
Security utilities: JWT tokens, multi-layer compound password hashing, OAuth helpers.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

MULTI_HASH_PREFIX = "$multi$v1$"

# ─── Multi-Layer Compound Password Hashing ───────────────────────────────────
def hash_password(password: str) -> str:
    """
    Multi-Layer Compound Password Hashing (Defense-in-Depth):
      Layer 1: HMAC-SHA512 with server-side secret pepper (protects against rainbow tables & database breaches).
      Layer 2: SHA-256 intermediate state digest (normalizes entropy & eliminates 72-byte truncation limit).
      Layer 3: Adaptive Salted Bcrypt with 12 key-stretching work factor rounds.
    """
    pepper = settings.SECRET_KEY.encode("utf-8")
    pwd_bytes = password.encode("utf-8")

    # Layer 1: HMAC-SHA512
    layer1 = hmac.new(pepper, pwd_bytes, hashlib.sha512).digest()

    # Layer 2: SHA-256 intermediate digest
    layer2 = hashlib.sha256(layer1 + b":researchai_layer2").hexdigest().encode("utf-8")

    # Layer 3: Bcrypt with cryptographic salt
    salt = bcrypt.gensalt(rounds=12)
    layer3 = bcrypt.hashpw(layer2, salt).decode("utf-8")

    return f"{MULTI_HASH_PREFIX}{layer3}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against stored multi-layer hash or legacy bcrypt hash.
    Provides backward compatibility while enforcing multi-layer security.
    """
    if not hashed_password or not plain_password:
        return False

    try:
        if hashed_password.startswith(MULTI_HASH_PREFIX):
            raw_bcrypt = hashed_password[len(MULTI_HASH_PREFIX):]
            pepper = settings.SECRET_KEY.encode("utf-8")
            pwd_bytes = plain_password.encode("utf-8")

            layer1 = hmac.new(pepper, pwd_bytes, hashlib.sha512).digest()
            layer2 = hashlib.sha256(layer1 + b":researchai_layer2").hexdigest().encode("utf-8")
            return bcrypt.checkpw(layer2, raw_bcrypt.encode("utf-8"))
        else:
            # Legacy single bcrypt fallback
            pwd_bytes = plain_password.encode("utf-8")[:72]
            return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


# ─── JWT Tokens ───────────────────────────────────────────────────────────────
def create_access_token(
    subject: str | UUID,
    extra_claims: Optional[dict] = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_access_token(token: str) -> Optional[str]:
    """Returns the subject (user_id) if token is valid access token, else None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[str]:
    """Returns the subject (user_id) if token is valid refresh token, else None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
