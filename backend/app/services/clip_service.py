import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.clip import Clip, ClipStatus, Platform
from app.repositories.clip_repository import ClipRepository


class ClipService:
    """Service handling business logic for Clip entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ClipRepository(db)

    async def create_clip(
        self,
        title: str,
        original_url: str,
        platform: Platform,
        thumbnail_url: str | None = None,
        duration_seconds: int | None = None,
    ) -> Clip:
        """Create a new clip after validating URL uniqueness."""
        existing_clip = await self.repository.get_by_original_url(original_url)
        if existing_clip is not None:
            raise ConflictError(f"Clip with URL '{original_url}' already exists.")

        clip = Clip(
            title=title,
            original_url=original_url,
            platform=platform,
            thumbnail_url=thumbnail_url,
            duration_seconds=duration_seconds,
        )

        try:
            created_clip = await self.repository.create(clip)
            await self.db.commit()
            await self.db.refresh(created_clip)
            return created_clip
        except Exception:
            await self.db.rollback()
            raise

    async def get_clip(self, clip_id: uuid.UUID) -> Clip:
        """Retrieve a clip by ID or raise NotFoundError."""
        clip = await self.repository.get_by_id(clip_id)
        if clip is None:
            raise NotFoundError(f"Clip with ID '{clip_id}' not found.")
        return clip

    async def list_clips(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Clip]:
        """Retrieve a paginated list of clips."""
        return await self.repository.list(offset=offset, limit=limit)

    async def update_clip(
        self,
        clip_id: uuid.UUID,
        title: str | None = None,
        thumbnail_url: str | None = None,
        duration_seconds: int | None = None,
    ) -> Clip:
        """Update optional metadata fields of a clip."""
        clip = await self.get_clip(clip_id)

        if title is not None:
            clip.title = title

        if thumbnail_url is not None:
            clip.thumbnail_url = thumbnail_url

        if duration_seconds is not None:
            clip.duration_seconds = duration_seconds

        try:
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(clip)
            return clip
        except Exception:
            await self.db.rollback()
            raise

    async def update_clip_status(
        self,
        clip_id: uuid.UUID,
        status: ClipStatus,
    ) -> Clip:
        """Update the processing status of a clip."""
        clip = await self.get_clip(clip_id)

        try:
            updated_clip = await self.repository.update_status(clip, status)
            await self.db.commit()
            await self.db.refresh(updated_clip)
            return updated_clip
        except Exception:
            await self.db.rollback()
            raise

    async def delete_clip(self, clip_id: uuid.UUID) -> None:
        """Delete a clip by ID or raise NotFoundError."""
        clip = await self.get_clip(clip_id)

        try:
            await self.repository.delete(clip)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise