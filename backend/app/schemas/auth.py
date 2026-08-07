import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict


class GoogleLoginRequest(BaseModel):
    """Request payload for Google OAuth authentication."""

    id_token: str


class TokenResponse(BaseModel):
    """Response payload containing backend JWT access token."""

    access_token: str
    token_type: Literal["Bearer"] = "Bearer"


class AuthenticatedUserResponse(BaseModel):
    """Public response payload for an authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    avatar_url: str | None = None