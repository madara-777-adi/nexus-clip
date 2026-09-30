import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt

from app.cache import redis as redis_cache
from app.core.config import settings
from app.core.exceptions import InternalServerError, UnauthorizedError

REVOKED_TOKEN_PREFIX = "revoked_access_token:"


def create_access_token(user_id: uuid.UUID) -> str:
    """Generate a signed JWT access token for an internal user ID."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {
        "sub": str(user_id),
        "typ": "access",
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_access_token(token: str) -> uuid.UUID:
    """Verify a signed JWT access token and return the extracted internal user ID."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Access token has expired.") from exc

    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid access token.") from exc
    
    if payload.get("typ") != "access":
        raise UnauthorizedError("Invalid token type.")

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Token subject is missing.")

    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise UnauthorizedError("Invalid user ID format in token subject.") from exc


def _token_key(token: str) -> str:
    return f"{REVOKED_TOKEN_PREFIX}{sha256(token.encode('utf-8')).hexdigest()}"


def _token_expiry(token: str) -> int:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        raise UnauthorizedError("Token expiry is missing.")
    return max(1, int(exp - datetime.now(UTC).timestamp()))


async def is_access_token_revoked(token: str) -> bool:
    """Check Redis revocation state for a validated access token."""
    redis = redis_cache.get_redis_client()
    if redis is None:
        raise InternalServerError("Redis is currently unavailable.")
    return bool(await redis.get(_token_key(token)))


async def revoke_access_token(token: str) -> None:
    """Revoke an access token until its original expiry."""
    redis = redis_cache.get_redis_client()
    if redis is None:
        raise InternalServerError("Redis is currently unavailable.")
    await redis.setex(_token_key(token), _token_expiry(token), "1")
