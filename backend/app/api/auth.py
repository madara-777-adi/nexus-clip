from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, oauth2_scheme
from app.auth.google import verify_google_id_token
from app.auth.jwt import revoke_access_token
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import (
    GoogleLoginRequest,
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
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Authenticate email/password user."""
    service = AuthService(db)
    user, token = await service.login_user(
        email=body.email,
        password=body.password,
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
    "/google",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def google_login(
    request: Request,
    body: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Verify a Google ID token and authenticate or create the user."""
    google_user = verify_google_id_token(body.id_token)
    service = AuthService(db)
    user, token = await service.get_or_create_google_user(
        google_id=google_user.google_id,
        email=google_user.email,
        full_name=google_user.full_name,
        avatar_url=google_user.avatar_url,
    )
    return APIResponse(
        success=True,
        message="Authentication successful.",
        data=TokenResponse(
            access_token=token,
            user=UserProfileResponse.model_validate(user),
        ),
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
) -> APIResponse[None]:
    """Invalidate active session."""
    await revoke_access_token(token)
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
