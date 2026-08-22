import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.clip import ClipResponse


class GuestBoardResponse(BaseModel):
    """Payload returned when creating or retrieving a guest session/board."""

    model_config = ConfigDict(from_attributes=True)

    guest_session_id: str
    board_code: str | None = None  # None until first clip is created per PRODUCT_SPEC.md §4
    expires_at: datetime
    clips: list[ClipResponse] = Field(default_factory=list)


class GuestContinueRequest(BaseModel):
    """Request payload for continuing a guest board via Board Code."""

    boardCode: str = Field(..., min_length=4, max_length=20, examples=["NEXUS-A1B2"])


class GuestPromoteResponse(BaseModel):
    """Payload returned when promoting a guest board into a logged-in user board."""

    board_id: uuid.UUID
    board_name: str
    moved_clips_count: int
