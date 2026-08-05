from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy ORM models."""
    pass


# Import all models so they are registered with SQLAlchemy metadata.
import app.models  # noqa: E402,F401