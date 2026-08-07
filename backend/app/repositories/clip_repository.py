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
        """Persist a new Clip entity."""
        self.db.add(clip)
        await self.db.flush()
        await self.db.refresh(clip)
        return clip

    async def get_by_id(
        self,
        clip_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> Clip | None:
        """Fetch a Clip by ID belonging to a specific owner."""
        stmt = select(Clip).where(
            Clip.id == clip_id,
            Clip.owner_id == owner_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_original_url(
        self,
        owner_id: uuid.UUID,
        original_url: str,
    ) -> Clip | None:
        """Fetch a Clip by original URL for a specific owner."""
        stmt = select(Clip).where(
            Clip.owner_id == owner_id,
            Clip.original_url == original_url,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        owner_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Clip]:
        """Retrieve paginated clips for a specific owner."""
        stmt = (
            select(Clip)
            .where(Clip.owner_id == owner_id)
            .order_by(Clip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        clip: Clip,
        status: ClipStatus,
    ) -> Clip:
        """Update clip processing status."""
        clip.status = status
        await self.db.flush()
        await self.db.refresh(clip)
        return clip

    async def delete(
        self,
        clip: Clip,
    ) -> None:
        """Delete a Clip entity."""
        await self.db.delete(clip)