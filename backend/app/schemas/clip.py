from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.clip import ClipStatus, Platform


class CreateClipRequest(BaseModel):
    """Request payload for creating a new clip."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Introduction to FastAPI"],
    )
    original_url: HttpUrl
    platform: Platform
    thumbnail_url: HttpUrl | None = None
    duration_seconds: int | None = Field(default=None, ge=0)


class UpdateClipRequest(BaseModel):
    """Request payload for updating clip metadata."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["Updated Clip Title"],
    )
    thumbnail_url: HttpUrl | None = None
    duration_seconds: int | None = Field(default=None, ge=0)


class ClipResponse(BaseModel):
    """Public response payload for a single clip."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    platform: Platform
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    status: ClipStatus
    created_at: datetime
    updated_at: datetime


class ClipListResponse(BaseModel):
    """Paginated response payload for clip listings."""

    items: list[ClipResponse]
    total: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)