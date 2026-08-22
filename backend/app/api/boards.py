import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.board import BoardResponse, CreateBoardRequest, UpdateBoardRequest
from app.schemas.response import APIResponse
from app.services.board_service import BoardService

router = APIRouter(
    prefix="/boards",
    tags=["boards"],
)


@router.get(
    "",
    response_model=APIResponse[list[BoardResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_boards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list[BoardResponse]]:
    """List all boards owned by current user."""
    service = BoardService(db)
    boards_with_counts = await service.list_user_boards(current_user)

    items = []
    for board, clip_count in boards_with_counts:
        item = BoardResponse.model_validate(board)
        item.clip_count = clip_count
        items.append(item)

    return APIResponse(
        success=True,
        message="Boards retrieved successfully.",
        data=items,
    )


@router.post(
    "",
    response_model=APIResponse[BoardResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_board(
    request: CreateBoardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BoardResponse]:
    """Create a new board."""
    service = BoardService(db)
    board = await service.create_board(current_user, request.name)
    return APIResponse(
        success=True,
        message="Board created successfully.",
        data=BoardResponse.model_validate(board),
    )


@router.patch(
    "/{board_id}",
    response_model=APIResponse[BoardResponse],
    status_code=status.HTTP_200_OK,
)
async def update_board(
    board_id: uuid.UUID,
    request: UpdateBoardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BoardResponse]:
    """Rename a board."""
    service = BoardService(db)
    board = await service.update_board(board_id, current_user, request.name)
    return APIResponse(
        success=True,
        message="Board updated successfully.",
        data=BoardResponse.model_validate(board),
    )


@router.delete(
    "/{board_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_board(
    board_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete a board."""
    service = BoardService(db)
    await service.delete_board(board_id, current_user)
    return APIResponse(
        success=True,
        message="Board deleted successfully.",
        data=None,
    )
