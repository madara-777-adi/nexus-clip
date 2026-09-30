import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.auth.jwt import is_access_token_revoked, verify_access_token
from app.cache.cache_manager import publish_board_event, websocket_manager
from app.core.exceptions import APIException
from app.db.session import AsyncSessionLocal, get_db
from app.models.user import User
from app.repositories.board_repository import BoardRepository
from app.repositories.user_repository import UserRepository
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


@router.websocket("/ws/boards/{board_id}")
async def board_websocket(websocket: WebSocket, board_id: uuid.UUID) -> None:
    """Subscribe this worker's clients to events for one board."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        user_id = verify_access_token(token)
        if await is_access_token_revoked(token):
            await websocket.close(code=1008)
            return
        async with AsyncSessionLocal() as db:
            user = await UserRepository(db).get_by_id(user_id)
            board = await BoardRepository(db).get_by_id(board_id, user_id) if user else None
            if board is None:
                await websocket.close(code=1008)
                return
    except APIException:
        await websocket.close(code=1008)
        return

    board_id_text = str(board_id)
    await websocket_manager.connect(board_id_text, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message == '{"type":"ping"}':
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        await websocket_manager.disconnect(board_id_text, websocket)


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
    clip_response = ClipResponse.model_validate(clip)
    await publish_board_event(
        str(board_id),
        {"type": "CLIP_CREATED", "data": {"clip": clip_response}},
    )
    return APIResponse(
        success=True,
        message="Clip created successfully.",
        data=clip_response,
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
    clip_response = ClipResponse.model_validate(clip)
    await publish_board_event(
        str(clip.board_id),
        {"type": "CLIP_UPDATED", "data": {"clip": clip_response}},
    )
    return APIResponse(
        success=True,
        message="Clip updated successfully.",
        data=clip_response,
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
    clip_response = ClipResponse.model_validate(clip)
    await publish_board_event(
        str(clip.board_id),
        {"type": "CLIP_UPDATED", "data": {"clip": clip_response}},
    )
    return APIResponse(
        success=True,
        message="Clip pin state toggled.",
        data=clip_response,
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
    clip = await service.get_clip(clip_id, current_user)
    await service.delete_clip(clip_id, current_user)
    await publish_board_event(
        str(clip.board_id),
        {"type": "CLIP_DELETED", "data": {"clip_id": str(clip_id)}},
    )
    return APIResponse(
        success=True,
        message="Clip deleted successfully.",
        data=None,
    )
