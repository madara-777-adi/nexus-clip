from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel, ConfigDict

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


class GoogleUserPayload(BaseModel):
    """Frozen Pydantic model representing verified Google user identity payload."""

    model_config = ConfigDict(frozen=True)

    google_id: str
    email: str
    full_name: str
    avatar_url: str | None = None


def verify_google_id_token(token: str) -> GoogleUserPayload:
    """Verify a Google ID Token and extract user identity payload."""
    try:
        request = requests.Request()
        payload = id_token.verify_oauth2_token(
            id_token=token,
            request=request,
            audience=settings.google_client_id,
        )
    except Exception as exc:
        raise UnauthorizedError("Invalid or unverified Google ID token.") from exc

    issuer = payload.get("iss")
    if issuer not in ("accounts.google.com", "https://accounts.google.com"):
        raise UnauthorizedError("Invalid Google token issuer.")

    if not payload.get("email_verified", False):
        raise UnauthorizedError("Google account email is not verified.")

    google_id = payload.get("sub")
    email = payload.get("email")
    if not google_id or not email:
        raise UnauthorizedError("Missing required user claims in Google token payload.")

    full_name = payload.get("name")
    if not full_name:
        raise UnauthorizedError("Missing user name in Google token payload.")
    avatar_url = payload.get("picture")

    return GoogleUserPayload(
        google_id=google_id,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
    )
