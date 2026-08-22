import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.board import Board
    from app.models.user import User


class ClipType(StrEnum):
    """Supported clip types in Nexus Clip."""

    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    IMAGE = "image"
    FILE = "file"
    URL = "url"


class Clip(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing a clipboard clip."""

    __tablename__ = "clips"

    board_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        default=None,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        default=None,
    )

    type: Mapped[ClipType] = mapped_column(
        SQLEnum(
            ClipType,
            native_enum=False,
            name="clip_type_enum",
        ),
        nullable=False,
        default=ClipType.TEXT,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Untitled Clip",
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    file_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
        default=None,
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )

    tags: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    board: Mapped["Board | None"] = relationship(
        "Board",
        back_populates="clips",
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="clips",
    )
