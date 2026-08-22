import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


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
