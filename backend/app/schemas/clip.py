from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.clip import ClipStatus, Platform


class CreateClipRequest(BaseModel):
    """Request payload for creating a clip."""

    original_url: HttpUrl


class UpdateClipRequest(BaseModel):
    """Request payload for updating editable clip metadata."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["Updated Clip Title"],
    )


class ClipResponse(BaseModel):
    """Public response payload for a single clip."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    platform: Platform
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    uploader: str | None = None
    status: ClipStatus
    created_at: datetime
    updated_at: datetime


class ClipListResponse(BaseModel):
    """Paginated response payload for clip listings."""

    items: list[ClipResponse]
    total: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)