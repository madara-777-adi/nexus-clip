import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.board import Board
from app.models.user import User
from app.repositories.board_repository import BoardRepository


class BoardService:
    """Service handling multi-board operations for authenticated users."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = BoardRepository(db)

    async def create_board(self, user: User, name: str) -> Board:
        """Create a new user board."""
        board = Board(
            user_id=user.id,
            name=name,
            is_default=False,
        )
        created = await self.repository.create(board)
        await self.db.commit()
        await self.db.refresh(created)
        return created

    async def list_user_boards(self, user: User) -> list[tuple[Board, int]]:
        """List all boards belonging to user with clip counts."""
        boards = await self.repository.list_by_user(user.id)
        if not boards:
            # Create default board if none exists
            default_board = Board(
                user_id=user.id,
                name="Main Board",
                is_default=True,
            )
            created = await self.repository.create(default_board)
            await self.db.commit()
            return [(created, 0)]
        return boards

    async def get_board(self, board_id: uuid.UUID, user: User) -> Board:
        """Get board by ID for authenticated user."""
        board = await self.repository.get_by_id(board_id, user.id)
        if board is None:
            raise NotFoundError(f"Board with ID '{board_id}' not found.")
        return board

    async def update_board(
        self,
        board_id: uuid.UUID,
        user: User,
        name: str,
    ) -> Board:
        """Rename user board."""
        board = await self.get_board(board_id, user)
        board.name = name
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def delete_board(self, board_id: uuid.UUID, user: User) -> None:
        """Delete user board (prevent deleting default board if it's the only one)."""
        board = await self.get_board(board_id, user)
        all_boards = await self.repository.list_by_user(user.id)

        if len(all_boards) <= 1:
            raise ValidationError("Cannot delete your only board.")

        await self.repository.delete(board)
        await self.db.commit()
