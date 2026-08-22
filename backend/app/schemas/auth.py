import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    """Request schema for email/password login."""

    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """Request schema for Google OAuth authentication."""

    id_token: str = Field(..., min_length=1)


class UserProfileResponse(BaseModel):
    """Public profile response payload for a user."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    avatar_url: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    """Authentication token response payload."""

    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
