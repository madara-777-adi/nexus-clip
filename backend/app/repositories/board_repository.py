import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.clip import Clip
from app.repositories.base import BaseRepository


class BoardRepository(BaseRepository):
    """Repository for Board domain entities."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, board: Board) -> Board:
        """Create and persist a new board."""
        self.db.add(board)
        await self.db.flush()
        await self.db.refresh(board)
        return board

    async def get_by_id(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Board | None:
        """Fetch a board owned by user."""
        stmt = select(Board).where(
            Board.id == board_id,
            Board.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[tuple[Board, int]]:
        """List user boards along with clip count."""
        stmt = (
            select(Board, func.count(Clip.id).label("clip_count"))
            .outerjoin(Clip, Clip.board_id == Board.id)
            .where(Board.user_id == user_id)
            .group_by(Board.id)
            .order_by(Board.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_default_board(self, user_id: uuid.UUID) -> Board | None:
        """Fetch user's default board."""
        stmt = select(Board).where(
            Board.user_id == user_id,
            Board.is_default.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, board: Board) -> None:
        """Delete a board entity."""
        await self.db.delete(board)
