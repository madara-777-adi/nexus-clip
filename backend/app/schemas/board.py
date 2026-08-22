import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateBoardRequest(BaseModel):
    """Payload for creating a new board."""

    name: str = Field(..., min_length=1, max_length=255, examples=["Project Alpha"])


class UpdateBoardRequest(BaseModel):
    """Payload for updating/renaming a board."""

    name: str = Field(..., min_length=1, max_length=255, examples=["Renamed Board"])


class BoardResponse(BaseModel):
    """Public representation of a board."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    is_default: bool = False
    clip_count: int = 0
    created_at: datetime
    updated_at: datetime
