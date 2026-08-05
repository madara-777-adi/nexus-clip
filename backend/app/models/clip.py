from enum import StrEnum

from sqlalchemy import Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


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

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    original_url: Mapped[str] = mapped_column(
        String(2048),
        unique=True,
        nullable=False,
        index=True,
    )

    platform: Mapped[Platform] = mapped_column(
        SQLEnum(
            Platform,
            name="platform_enum",
            native_enum=True,
        ),
        nullable=False,
        index=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[ClipStatus] = mapped_column(
        SQLEnum(
            ClipStatus,
            name="clip_status_enum",
            native_enum=True,
        ),
        nullable=False,
        default=ClipStatus.PENDING,
        server_default=ClipStatus.PENDING.value,
        index=True,
    )