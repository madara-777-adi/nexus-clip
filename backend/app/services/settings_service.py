import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.settings import UserSettings
from app.models.user import User
from app.repositories.board_repository import BoardRepository


class SettingsService:
    """Service handling user retention policies and application settings."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_settings(self, user: User) -> UserSettings:
        """Get or initialize user settings."""
        stmt = select(UserSettings).where(UserSettings.user_id == user.id)
        result = await self.db.execute(stmt)
        settings = result.scalar_one_or_none()

        if settings is None:
            settings = UserSettings(
                user_id=user.id,
                auto_cleanup_days="never",
                theme="dark",
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)

        return settings

    async def update_user_settings(
        self,
        user: User,
        auto_cleanup_days: str | None = None,
        theme: str | None = None,
        default_board_id: uuid.UUID | None = None,
    ) -> UserSettings:
        """Update user settings."""
        settings = await self.get_user_settings(user)

        if auto_cleanup_days is not None:
            if auto_cleanup_days not in ("7", "30", "90", "never"):
                raise ValidationError(
                    "Auto-cleanup must be one of: 7, 30, 90, or never."
                )
            settings.auto_cleanup_days = auto_cleanup_days
        if theme is not None:
            if theme not in ("dark", "light"):
                raise ValidationError("Theme must be either dark or light.")
            settings.theme = theme
        if default_board_id is not None:
            board = await BoardRepository(self.db).get_by_id(default_board_id, user.id)
            if board is None:
                raise NotFoundError(f"Board with ID '{default_board_id}' not found.")
            settings.default_board_id = default_board_id

        await self.db.commit()
        await self.db.refresh(settings)
        return settings
