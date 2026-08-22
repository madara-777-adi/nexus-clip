import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.clip import Clip, ClipType
from app.models.user import User
from app.repositories.board_repository import BoardRepository
from app.repositories.clip_repository import ClipRepository


class ClipService:
    """Service handling business logic for Clip entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.clip_repository = ClipRepository(db)
        self.board_repository = BoardRepository(db)

    async def create_clip(
        self,
        user: User,
        board_id: uuid.UUID,
        clip_type: ClipType = ClipType.TEXT,
        title: str = "Untitled Clip",
        content: str | None = None,
        file_url: str | None = None,
        file_name: str | None = None,
        file_size: int | None = None,
        tags: list[str] | None = None,
        is_pinned: bool = False,
    ) -> Clip:
        """Create a clip inside a user board."""
        # Verify board ownership
        board = await self.board_repository.get_by_id(board_id, user.id)
        if board is None:
            raise NotFoundError(f"Board with ID '{board_id}' not found.")

        clip = Clip(
            board_id=board.id,
            user_id=user.id,
            type=clip_type,
            title=title or "Untitled Clip",
            content=content,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            tags=tags or [],
            is_pinned=is_pinned,
        )

        created = await self.clip_repository.create(clip)
        await self.db.commit()
        await self.db.refresh(created)
        return created

    async def get_clip(self, clip_id: uuid.UUID, user: User) -> Clip:
        """Get clip by ID for authenticated user."""
        clip = await self.clip_repository.get_by_id(clip_id, user.id)
        if clip is None:
            raise NotFoundError(f"Clip with ID '{clip_id}' not found.")
        return clip

    async def list_board_clips(
        self,
        board_id: uuid.UUID,
        user: User,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Clip], int]:
        """List clips for a board."""
        board = await self.board_repository.get_by_id(board_id, user.id)
        if board is None:
            raise NotFoundError(f"Board with ID '{board_id}' not found.")
        return await self.clip_repository.list_by_board(
            board_id=board_id,
            user_id=user.id,
            offset=offset,
            limit=limit,
        )

    async def update_clip(
        self,
        clip_id: uuid.UUID,
        user: User,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        is_pinned: bool | None = None,
    ) -> Clip:
        """Update clip fields."""
        clip = await self.get_clip(clip_id, user)

        if title is not None:
            clip.title = title
        if content is not None:
            clip.content = content
        if tags is not None:
            clip.tags = tags
        if is_pinned is not None:
            clip.is_pinned = is_pinned

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(clip)
        return clip

    async def toggle_pin(self, clip_id: uuid.UUID, user: User) -> Clip:
        """Toggle pin state of clip."""
        clip = await self.get_clip(clip_id, user)
        clip.is_pinned = not clip.is_pinned
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(clip)
        return clip

    async def delete_clip(self, clip_id: uuid.UUID, user: User) -> None:
        """Delete clip."""
        clip = await self.get_clip(clip_id, user)
        await self.clip_repository.delete(clip)
        await self.db.commit()
