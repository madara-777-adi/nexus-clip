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
    prefix="/clips",
    tags=["clips"],
)


@router.post(
    "/",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_clip(
    request: CreateClipRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Create a new clip for the authenticated user."""

    service = ClipService(db)

    clip = await service.create_clip(
        original_url=str(request.original_url),
        owner=current_user,
    )

    return APIResponse(
        success=True,
        message="Clip created successfully.",
        data=ClipResponse.model_validate(clip),
    )


@router.get(
    "/",
    response_model=APIResponse[ClipListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_clips(
    offset: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipListResponse]:
    """List clips owned by the authenticated user."""

    service = ClipService(db)

    clips = await service.list_clips(
        owner=current_user,
        offset=offset,
        limit=limit,
    )

    items = [ClipResponse.model_validate(clip) for clip in clips]

    return APIResponse(
        success=True,
        message="Clips retrieved successfully.",
        data=ClipListResponse(
            items=items,
            total=len(items),
            offset=offset,
            limit=limit,
        ),
    )


@router.get(
    "/{clip_id}",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_200_OK,
)
async def get_clip(
    clip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    """Retrieve a clip owned by the authenticated user."""

    service = ClipService(db)

    clip = await service.get_clip(
        clip_id=clip_id,
        owner=current_user,
    )

    return APIResponse(
        success=True,
        message="Clip retrieved successfully.",
        data=ClipResponse.model_validate(clip),
    )


@router.patch(
    "/{clip_id}",
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

    update_data = request.model_dump(exclude_unset=True)

    clip = await service.update_clip(
        clip_id=clip_id,
        owner=current_user,
        **update_data,
    )

    return APIResponse(
        success=True,
        message="Clip updated successfully.",
        data=ClipResponse.model_validate(clip),
    )


@router.delete(
    "/{clip_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_clip(
    clip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """Delete a clip owned by the authenticated user."""

    service = ClipService(db)

    await service.delete_clip(
        clip_id=clip_id,
        owner=current_user,
    )

    return APIResponse(
        success=True,
        message="Clip deleted successfully.",
        data=None,
    )