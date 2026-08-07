from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import verify_access_token
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/google",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts Bearer token, verifies JWT, and retrieves current user."""
    user_id = verify_access_token(token)

    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError("Authenticated user no longer exists.")

    return user