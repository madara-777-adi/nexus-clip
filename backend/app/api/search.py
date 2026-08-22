import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.clip import ClipType
from app.models.user import User
from app.schemas.clip import ClipListResponse, ClipResponse
from app.schemas.response import APIResponse
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get(
    "",
    response_model=APIResponse[ClipListResponse],
    status_code=status.HTTP_200_OK,
)
async def search_clips(
    q: str | None = Query(default=None, description="Search query string"),
    type: ClipType | None = Query(default=None, description="Clip type filter"),
    board: uuid.UUID | None = Query(default=None, description="Filter by board ID"),
    offset: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ClipListResponse]:
    """Search user clips by keyword, type, or board."""
    service = SearchService(db)
    clips, total = await service.search_clips(
        user=current_user,
        query=q,
        clip_type=type,
        board_id=board,
        offset=offset,
        limit=limit,
    )
    items = [ClipResponse.model_validate(c) for c in clips]
    return APIResponse(
        success=True,
        message="Search results retrieved.",
        data=ClipListResponse(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        ),
    )
