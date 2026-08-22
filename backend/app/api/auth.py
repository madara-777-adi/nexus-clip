from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Register a new user account."""
    service = AuthService(db)
    user, token = await service.register_user(
        name=request.name,
        email=request.email,
        password=request.password,
    )
    profile = UserProfileResponse.model_validate(user)
    return APIResponse(
        success=True,
        message="Account registered successfully.",
        data=TokenResponse(
            access_token=token,
            user=profile,
        ),
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Authenticate email/password user."""
    service = AuthService(db)
    user, token = await service.login_user(
        email=request.email,
        password=request.password,
    )
    profile = UserProfileResponse.model_validate(user)
    return APIResponse(
        success=True,
        message="Authentication successful.",
        data=TokenResponse(
            access_token=token,
            user=profile,
        ),
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> APIResponse[None]:
    """Invalidate active session."""
    return APIResponse(
        success=True,
        message="Logged out successfully.",
        data=None,
    )


@router.get(
    "/me",
    response_model=APIResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserProfileResponse]:
    """Get profile of current authenticated user."""
    return APIResponse(
        success=True,
        message="User profile retrieved.",
        data=UserProfileResponse.model_validate(current_user),
    )
