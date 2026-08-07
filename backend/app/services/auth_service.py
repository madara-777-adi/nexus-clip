from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service handling business logic for authentication and user management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    async def get_or_create_user(
        self,
        google_id: str,
        email: str,
        full_name: str,
        avatar_url: str | None,
    ) -> User:
        """Retrieve an existing user by Google ID and update changed fields, or create a new user."""
        user = await self.user_repository.get_by_google_id(google_id)

        if user is not None:
            updated = False

            if user.email != email:
                user.email = email
                updated = True

            if user.full_name != full_name:
                user.full_name = full_name
                updated = True

            if user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                updated = True

            if updated:
                await self.db.flush()

            return user

        new_user = User(
            google_id=google_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )

        return await self.user_repository.create(new_user)