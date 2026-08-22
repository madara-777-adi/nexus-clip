import uuid
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clip import Clip, ClipType
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
        user_id: uuid.UUID | None = None,
    ) -> Clip | None:
        """Fetch a Clip by ID."""
        stmt = select(Clip).where(Clip.id == clip_id)
        if user_id is not None:
            stmt = stmt.where(Clip.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_board(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Clip], int]:
        """Retrieve paginated clips for a board, pinned first."""
        base_stmt = select(Clip).where(
            Clip.board_id == board_id,
            Clip.user_id == user_id,
        )

        # Count total
        count_stmt = select(Clip.id).where(
            Clip.board_id == board_id,
            Clip.user_id == user_id,
        )
        total_result = await self.db.execute(count_stmt)
        total = len(total_result.all())

        stmt = (
            base_stmt.order_by(Clip.is_pinned.desc(), Clip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def search(
        self,
        user_id: uuid.UUID,
        query: str | None = None,
        clip_type: ClipType | None = None,
        board_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Clip], int]:
        """Search clips by query string, type, or board."""
        stmt = select(Clip).where(Clip.user_id == user_id)

        if board_id is not None:
            stmt = stmt.where(Clip.board_id == board_id)

        if clip_type is not None:
            stmt = stmt.where(Clip.type == clip_type)

        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Clip.title.ilike(search_pattern),
                    Clip.content.ilike(search_pattern),
                    Clip.file_name.ilike(search_pattern),
                )
            )

        # Total count
        total_res = await self.db.execute(stmt)
        total = len(total_res.all())

        stmt = (
            stmt.order_by(Clip.is_pinned.desc(), Clip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def delete_expired_unpinned(
        self,
        user_id: uuid.UUID,
        cutoff_time: datetime,
    ) -> int:
        """Delete unpinned clips older than cutoff_time for a specific user."""
        stmt = select(Clip).where(
            Clip.user_id == user_id,
            Clip.is_pinned.is_(False),
            Clip.created_at < cutoff_time,
        )
        result = await self.db.execute(stmt)
        expired_clips = result.scalars().all()
        count = len(expired_clips)
        for clip in expired_clips:
            await self.db.delete(clip)
        await self.db.flush()
        return count

    async def delete(self, clip: Clip) -> None:
        """Delete a Clip entity."""
        await self.db.delete(clip)
