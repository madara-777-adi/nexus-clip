import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing user settings and retention preferences."""

    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    auto_cleanup_days: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="never",
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="dark",
    )

    default_board_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
    )
