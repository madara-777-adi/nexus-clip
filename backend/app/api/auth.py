from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import get_db
from app.schemas.auth import GoogleLoginRequest, TokenResponse
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/google",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def login_with_google(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Authenticate a user using a Google ID Token."""

    google_payload = verify_google_id_token(request.id_token)

    auth_service = AuthService(db)

    user = await auth_service.get_or_create_user(
        google_id=google_payload.google_id,
        email=google_payload.email,
        full_name=google_payload.full_name,
        avatar_url=google_payload.avatar_url,
    )

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(user)

    access_token = create_access_token(user.id)

    return APIResponse(
        success=True,
        message="Authentication successful.",
        data=TokenResponse(
            access_token=access_token,
            token_type="Bearer",
        ),
    )