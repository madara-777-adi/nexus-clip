import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clip import Clip, ClipStatus
from app.repositories.base import BaseRepository


class ClipRepository(BaseRepository):
    """Repository handling persistence operations for Clip entities."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, clip: Clip) -> Clip:
        self.db.add(clip)
        await self.db.flush()
        return clip

    async def get_by_id(self, clip_id: uuid.UUID) -> Clip | None:
        stmt = select(Clip).where(Clip.id == clip_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_original_url(self, original_url: str) -> Clip | None:
        stmt = select(Clip).where(Clip.original_url == original_url)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        clip: Clip,
        status: ClipStatus,
    ) -> Clip:
        clip.status = status
        await self.db.flush()
        return clip

    async def delete(self, clip: Clip) -> None:
        await self.db.delete(clip)

    async def list(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Clip]:
        stmt = select(Clip).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())