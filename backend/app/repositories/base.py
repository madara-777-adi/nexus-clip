from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository providing shared database session management."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository with an active database session."""
        self.db: AsyncSession = db
