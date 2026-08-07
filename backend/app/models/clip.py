import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    UUID,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Platform(StrEnum):
    """Supported clip source platforms."""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"


class ClipStatus(StrEnum):
    """Lifecycle status states for a clip."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Clip(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing a web media clip."""

    __tablename__ = "clips"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "original_url",
            name="uq_owner_original_url",
        ),
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    original_url: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    platform: Mapped[Platform] = mapped_column(
        SQLEnum(
            Platform,
            native_enum=True,
            name="platform_enum",
        ),
        nullable=False,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )

    uploader: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None,
    )

    status: Mapped[ClipStatus] = mapped_column(
        SQLEnum(
            ClipStatus,
            native_enum=True,
            name="clip_status_enum",
        ),
        nullable=False,
        default=ClipStatus.PENDING,
        server_default=ClipStatus.PENDING.value,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="clips",
    )