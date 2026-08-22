import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.clip import Clip
    from app.models.user import User


class Board(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing a user board/workspace."""

    __tablename__ = "boards"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="boards",
    )

    clips: Mapped[list["Clip"]] = relationship(
        "Clip",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
