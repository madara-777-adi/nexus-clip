from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.settings import UpdateSettingsRequest, UserSettingsResponse
from app.services.settings_service import SettingsService

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


@router.get(
    "",
    response_model=APIResponse[UserSettingsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[UserSettingsResponse]:
    """Get user settings and retention policy."""
    service = SettingsService(db)
    settings = await service.get_user_settings(current_user)
    return APIResponse(
        success=True,
        message="User settings retrieved.",
        data=UserSettingsResponse.model_validate(settings),
    )


@router.patch(
    "",
    response_model=APIResponse[UserSettingsResponse],
    status_code=status.HTTP_200_OK,
)
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[UserSettingsResponse]:
    """Update user settings and retention policy."""
    service = SettingsService(db)
    settings = await service.update_user_settings(
        user=current_user,
        auto_cleanup_days=request.auto_cleanup_days,
        theme=request.theme,
        default_board_id=request.default_board_id,
    )
    return APIResponse(
        success=True,
        message="User settings updated.",
        data=UserSettingsResponse.model_validate(settings),
    )
