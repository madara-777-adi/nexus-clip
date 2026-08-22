from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.board import Board
    from app.models.clip import Clip
    from app.models.settings import UserSettings


class User(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing an application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        default=None,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
        default=None,
    )

    boards: Mapped[list["Board"]] = relationship(
        "Board",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    clips: Mapped[list["Clip"]] = relationship(
        "Clip",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    settings: Mapped["UserSettings | None"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
