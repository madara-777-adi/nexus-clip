import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.clip import ClipType


class CreateClipRequest(BaseModel):
    """Payload for creating a new clip."""

    type: ClipType = Field(default=ClipType.TEXT)
    title: str = Field(default="Untitled Clip", max_length=255)
    content: str | None = Field(default=None)
    file_url: str | None = Field(default=None)
    file_name: str | None = Field(default=None)
    file_size: int | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    is_pinned: bool = Field(default=False)


class UpdateClipRequest(BaseModel):
    """Payload for updating editable clip fields."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    is_pinned: bool | None = Field(default=None)


class ClipResponse(BaseModel):
    """Public schema for a clip."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    board_id: uuid.UUID | None = None
    type: ClipType
    title: str
    content: str | None = None
    file_url: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    tags: list[str] = Field(default_factory=list)
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime


class ClipListResponse(BaseModel):
    """Paginated listing of clips."""

    items: list[ClipResponse]
    total: int = Field(ge=0)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, gt=0)
