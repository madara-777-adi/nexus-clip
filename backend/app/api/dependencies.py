from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import is_access_token_revoked, verify_access_token
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/google",
)
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/google",
    auto_error=False,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts Bearer token, verifies JWT, and retrieves current user."""
    user_id = verify_access_token(token)
    if await is_access_token_revoked(token):
        raise UnauthorizedError("Access token has been revoked.")

    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError("Authenticated user no longer exists.")

    return user


async def get_optional_current_user(
    token: str | None = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Return the authenticated user when a bearer token is supplied."""
    if token is None:
        return None
    return await get_current_user(token=token, db=db)
