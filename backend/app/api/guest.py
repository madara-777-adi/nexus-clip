import uuid

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models.clip import ClipType
from app.models.user import User
from app.schemas.clip import ClipListResponse, ClipResponse, CreateClipRequest
from app.schemas.guest import (
    GuestBoardResponse,
    GuestContinueRequest,
    GuestPromoteResponse,
)
from app.schemas.response import APIResponse
from app.services.board_service import BoardService
from app.services.clip_service import ClipService
from app.services.guest_service import GuestService

router = APIRouter(
    prefix="/guest",
    tags=["guest"],
)


@router.post(
    "/board",
    response_model=APIResponse[GuestBoardResponse],
    status_code=status.HTTP_200_OK,
)
async def get_or_create_guest_board(
    x_guest_session_id: str | None = Header(default=None),
) -> APIResponse[GuestBoardResponse]:
    """Retrieve or create temporary Guest Board session in Redis."""
    service = GuestService()
    session = await service.get_or_create_session(x_guest_session_id)
    return APIResponse(
        success=True,
        message="Guest session retrieved.",
        data=GuestBoardResponse.model_validate(session),
    )


@router.post(
    "/board/clips",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_guest_clip(
    request: CreateClipRequest,
    x_guest_session_id: str = Header(...),
) -> APIResponse[ClipResponse]:
    """Add a clip to a Guest Board. Generates Board Code on 1st clip."""
    service = GuestService()
    _session, clip_dict = await service.add_guest_clip(
        guest_session_id=x_guest_session_id,
        clip_type=request.type.value,
        title=request.title,
        content=request.content,
        file_url=request.file_url,
        file_name=request.file_name,
        file_size=request.file_size,
        tags=request.tags,
    )
    return APIResponse(
        success=True,
        message="Guest clip created.",
        data=ClipResponse.model_validate(clip_dict),
    )


@router.post(
    "/continue",
    response_model=APIResponse[GuestBoardResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def continue_guest_board(
    request: Request,
    body: GuestContinueRequest,
) -> APIResponse[GuestBoardResponse]:
    """Continue an existing Guest Board across devices using Board Code."""
    service = GuestService()
    session = await service.continue_guest_board(body.boardCode)
    return APIResponse(
        success=True,
        message="Guest Board continued successfully.",
        data=GuestBoardResponse.model_validate(session),
    )


@router.get(
    "/search",
    response_model=APIResponse[ClipListResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def search_guest_clips(
    request: Request,
    q: str | None = Query(default=None, description="Search query string"),
    type: ClipType | None = Query(default=None, description="Clip type filter"),
    x_guest_session_id: str = Header(...),
) -> APIResponse[ClipListResponse]:
    """Search clips in the active guest session."""
    clips = await GuestService().search_guest_clips(
        guest_session_id=x_guest_session_id,
        query=q,
        clip_type=type,
    )
    items = [ClipResponse.model_validate(clip) for clip in clips]
    return APIResponse(
        success=True,
        message="Guest search results retrieved.",
        data=ClipListResponse(
            items=items,
            total=len(items),
            offset=0,
            limit=len(items) or 1,
        ),
    )


@router.patch(
    "/clips/{clip_id}/pin",
    response_model=APIResponse[ClipResponse],
    status_code=status.HTTP_200_OK,
)
async def toggle_guest_clip_pin(
    clip_id: uuid.UUID,
    x_guest_session_id: str = Header(...),
) -> APIResponse[ClipResponse]:
    """Toggle a guest clip's pin state and persist it in Redis."""
    clip = await GuestService().toggle_guest_clip_pin(x_guest_session_id, clip_id)
    return APIResponse(
        success=True,
        message="Guest clip pin state toggled.",
        data=ClipResponse.model_validate(clip),
    )


@router.delete(
    "/clips/{clip_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_guest_clip(
    clip_id: uuid.UUID,
    x_guest_session_id: str = Header(...),
) -> APIResponse[None]:
    """Delete a guest clip from Redis."""
    await GuestService().delete_guest_clip(x_guest_session_id, clip_id)
    return APIResponse(
        success=True,
        message="Guest clip deleted.",
        data=None,
    )


@router.post(
    "/promote",
    response_model=APIResponse[GuestPromoteResponse],
    status_code=status.HTTP_200_OK,
)
async def promote_guest_board(
    x_guest_session_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[GuestPromoteResponse]:
    """Promote Guest Board clips into a permanent User Board upon login."""
    guest_service = GuestService()
    clip_service = ClipService(db)
    board_service = BoardService(db)

    board_id, board_name, count = await guest_service.promote_guest_board(
        guest_session_id=x_guest_session_id,
        user=current_user,
        clip_service=clip_service,
        board_service=board_service,
    )

    return APIResponse(
        success=True,
        message="Guest Board promoted to User Board.",
        data=GuestPromoteResponse(
            board_id=board_id,
            board_name=board_name,
            moved_clips_count=count,
        ),
    )
