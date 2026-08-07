from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.clip import Clip


class User(Base, UUIDMixin, TimestampMixin):
    """Domain entity representing an application user."""

    __tablename__ = "users"

    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

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

    avatar_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
        default=None,
    )

    clips: Mapped[list["Clip"]] = relationship(
        "Clip",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )