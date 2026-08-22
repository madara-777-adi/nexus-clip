import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clip import Clip, ClipType
from app.models.user import User
from app.repositories.clip_repository import ClipRepository


class SearchService:
    """Service handling clip search across title, content, filename, and tags."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.clip_repository = ClipRepository(db)

    async def search_clips(
        self,
        user: User,
        query: str | None = None,
        clip_type: ClipType | None = None,
        board_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Clip], int]:
        """Search user clips with filters."""
        return await self.clip_repository.search(
            user_id=user.id,
            query=query,
            clip_type=clip_type,
            board_id=board_id,
            offset=offset,
            limit=limit,
        )
