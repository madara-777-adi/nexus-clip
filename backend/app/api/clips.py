import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.clip import (
    ClipListResponse,
    ClipResponse,
    CreateClipRequest,
    UpdateClipRequest,
)
from app.schemas.response import APIResponse
from app.services.clip_service import ClipService

router = APIRouter(prefix="/clips", tags=["clips"])


@router.post(
    "/",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_clip(
    request: CreateClipRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    service = ClipService(db)

    clip = await service.create_clip(
        title=request.title,
        original_url=str(request.original_url),
        platform=request.platform,
        thumbnail_url=str(request.thumbnail_url)
        if request.thumbnail_url
        else None,
        duration_seconds=request.duration_seconds,
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
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipListResponse]:
    service = ClipService(db)

    clips = await service.list_clips(
        offset=offset,
        limit=limit,
    )

    items = [ClipResponse.model_validate(clip) for clip in clips]

    return APIResponse(
        success=True,
        message="Clips retrieved successfully.",
        data=ClipListResponse(
            items=items,
            total=len(items),  # TODO: Replace with repository.count() when pagination is enhanced.
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
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    service = ClipService(db)

    clip = await service.get_clip(clip_id)

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
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipResponse]:
    service = ClipService(db)

    update_data = request.model_dump(exclude_unset=True)

    if (
        "thumbnail_url" in update_data
        and update_data["thumbnail_url"] is not None
    ):
        update_data["thumbnail_url"] = str(update_data["thumbnail_url"])

    clip = await service.update_clip(
        clip_id,
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
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    service = ClipService(db)

    await service.delete_clip(clip_id)

    return APIResponse(
        success=True,
        message="Clip deleted successfully.",
        data=None,
    )