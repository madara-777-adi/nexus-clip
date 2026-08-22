import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.clip import (
    ClipListResponse,
    ClipResponse,
    CreateClipRequest,
    UpdateClipRequest,
)
from app.schemas.response import APIResponse
from app.services.clip_service import ClipService

router = APIRouter(
    tags=["clips"],
)


@router.get(
    "/boards/{board_id}/clips",
    response_model=APIResponse[ClipListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_board_clips(
    board_id: uuid.UUID,
    offset: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipListResponse]:
    """Retrieve all clips in a specific board."""
    service = ClipService(db)
    clips, total = await service.list_board_clips(
        board_id=board_id,
        user=current_user,
        offset=offset,
        limit=limit,
    )
    items = [ClipResponse.model_validate(c) for c in clips]
    return APIResponse(
        success=True,
        message="Board clips retrieved.",
        data=ClipListResponse(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        ),
    )


@router.post(
    "/boards/{board_id}/clips",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_clip(
    board_id: uuid.UUID,
    request: CreateClipRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Create a new clip in a board."""
    service = ClipService(db)
    clip = await service.create_clip(
        user=current_user,
        board_id=board_id,
        clip_type=request.type,
        title=request.title,
        content=request.content,
        file_url=request.file_url,
        file_name=request.file_name,
        file_size=request.file_size,
        tags=request.tags,
        is_pinned=request.is_pinned,
    )
    return APIResponse(
        success=True,
        message="Clip created successfully.",
        data=ClipResponse.model_validate(clip),
    )


@router.get(
    "/clips/{clip_id}",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_200_OK,
)
async def get_clip(
    clip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Retrieve a single clip by ID."""
    service = ClipService(db)
    clip = await service.get_clip(clip_id, current_user)
    return APIResponse(
        success=True,
        message="Clip retrieved.",
        data=ClipResponse.model_validate(clip),
    )


@router.patch(
    "/clips/{clip_id}",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_200_OK,
)
async def update_clip(
    clip_id: uuid.UUID,
    request: UpdateClipRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Update editable clip fields."""
    service = ClipService(db)
    clip = await service.update_clip(
        clip_id=clip_id,
        user=current_user,
        title=request.title,
        content=request.content,
        tags=request.tags,
        is_pinned=request.is_pinned,
    )
    return APIResponse(
        success=True,
        message="Clip updated successfully.",
        data=ClipResponse.model_validate(clip),
    )


@router.patch(
    "/clips/{clip_id}/pin",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_200_OK,
)
async def toggle_pin(
    clip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Toggle clip pin state."""
    service = ClipService(db)
    clip = await service.toggle_pin(clip_id, current_user)
    return APIResponse(
        success=True,
        message="Clip pin state toggled.",
        data=ClipResponse.model_validate(clip),
    )


@router.delete(
    "/clips/{clip_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_clip(
    clip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete a clip."""
    service = ClipService(db)
    await service.delete_clip(clip_id, current_user)
    return APIResponse(
        success=True,
        message="Clip deleted successfully.",
        data=None,
    )
