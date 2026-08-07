import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.clip import Clip, ClipStatus
from app.models.user import User
from app.repositories.clip_repository import ClipRepository
from app.services.metadata_service import MetadataService


class ClipService:
    """Service handling business logic for Clip entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ClipRepository(db)
        self.metadata_service = MetadataService()

    async def create_clip(
        self,
        original_url: str,
        owner: User,
    ) -> Clip:
        """Create a new clip after extracting metadata."""

        normalized_url = self.metadata_service.normalize_url(
            original_url
        )

        platform = self.metadata_service.detect_platform(
            normalized_url
        )

        existing_clip = await self.repository.get_by_original_url(
            owner_id=owner.id,
            original_url=normalized_url,
        )

        if existing_clip is not None:
            raise ConflictError(
                f"Clip with URL '{normalized_url}' already exists."
            )

        metadata = await self.metadata_service.fetch_metadata(
            normalized_url
        )

        clip = Clip(
            title=metadata.title,
            original_url=normalized_url,
            platform=platform,
            thumbnail_url=metadata.thumbnail_url,
            duration_seconds=metadata.duration_seconds,
            uploader=metadata.uploader,
            status=ClipStatus.COMPLETED,
            owner_id=owner.id,
        )

        created_clip = await self.repository.create(clip)

        await self.db.commit()
        await self.db.refresh(created_clip)

        return created_clip

    async def get_clip(
        self,
        clip_id: uuid.UUID,
        owner: User,
    ) -> Clip:
        clip = await self.repository.get_by_id(
            clip_id=clip_id,
            owner_id=owner.id,
        )

        if clip is None:
            raise NotFoundError(
                f"Clip with ID '{clip_id}' not found."
            )

        return clip

    async def list_clips(
        self,
        owner: User,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Clip]:
        return await self.repository.list(
            owner_id=owner.id,
            offset=offset,
            limit=limit,
        )

    async def update_clip(
        self,
        clip_id: uuid.UUID,
        owner: User,
        title: str | None = None,
    ) -> Clip:
        clip = await self.get_clip(
            clip_id=clip_id,
            owner=owner,
        )

        if title is not None:
            clip.title = title

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(clip)

        return clip

    async def update_clip_status(
        self,
        clip_id: uuid.UUID,
        owner: User,
        status: ClipStatus,
    ) -> Clip:
        clip = await self.get_clip(
            clip_id=clip_id,
            owner=owner,
        )

        updated = await self.repository.update_status(
            clip,
            status,
        )

        await self.db.commit()
        await self.db.refresh(updated)

        return updated

    async def delete_clip(
        self,
        clip_id: uuid.UUID,
        owner: User,
    ) -> None:
        clip = await self.get_clip(
            clip_id=clip_id,
            owner=owner,
        )

        await self.repository.delete(clip)
        await self.db.commit()