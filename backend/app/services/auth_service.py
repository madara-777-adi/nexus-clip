import hashlib
import os
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.core.exceptions import ConflictError, UnauthorizedError
from app.models.board import Board
from app.models.user import User
from app.repositories.board_repository import BoardRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service handling business logic for authentication and user management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.board_repository = BoardRepository(db)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash plain text password using PBKDF2-HMAC-SHA256."""
        salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()
        return f"{salt}${key}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against PBKDF2 hash string."""
        try:
            salt, stored_key = hashed_password.split("$", 1)
            calculated_key = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                100_000,
            ).hex()
            return secrets.compare_digest(stored_key, calculated_key)
        except (ValueError, AttributeError):
            return False

    async def register_user(
        self,
        name: str,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        """Register a new user, create default board, and return user with access token."""
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user is not None:
            raise ConflictError(f"User with email '{email}' already exists.")

        user = User(
            email=email,
            full_name=name,
            hashed_password=self.hash_password(password),
        )
        created_user = await self.user_repository.create(user)

        # Create default board for user per PRODUCT_SPEC.md
        default_board = Board(
            user_id=created_user.id,
            name="Main Board",
            is_default=True,
        )
        await self.board_repository.create(default_board)
        await self.db.commit()
        await self.db.refresh(created_user)

        token = create_access_token(user_id=created_user.id)
        return created_user, token

    async def login_user(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        """Authenticate email/password user and return access token."""
        user = await self.user_repository.get_by_email(email)
        if user is None or not user.hashed_password:
            raise UnauthorizedError("Invalid email or password.")

        if not self.verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")

        token = create_access_token(user_id=user.id)
        return user, token

    async def get_or_create_google_user(
        self,
        google_id: str,
        email: str,
        full_name: str,
        avatar_url: str | None,
    ) -> tuple[User, str]:
        """Retrieve existing Google user or create a new user and token."""
        user = await self.user_repository.get_by_google_id(google_id)

        if user is None:
            user = await self.user_repository.get_by_email(email)

        if user is not None:
            user.google_id = google_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            await self.db.flush()
        else:
            user = User(
                google_id=google_id,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
            )
            user = await self.user_repository.create(user)
            default_board = Board(
                user_id=user.id,
                name="Main Board",
                is_default=True,
            )
            await self.board_repository.create(default_board)

        await self.db.commit()
        await self.db.refresh(user)

        token = create_access_token(user_id=user.id)
        return user, token
