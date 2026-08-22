import uuid

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsResponse(BaseModel):
    """Schema for user settings and retention preferences."""

    model_config = ConfigDict(from_attributes=True)

    auto_cleanup_days: str = Field(default="never", examples=["7", "30", "90", "never"])
    theme: str = Field(default="dark")
    default_board_id: uuid.UUID | None = None


class UpdateSettingsRequest(BaseModel):
    """Payload for updating user settings."""

    auto_cleanup_days: str | None = Field(default=None)
    theme: str | None = Field(default=None)
    default_board_id: uuid.UUID | None = Field(default=None)
