from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.settings import UserSettings
from app.repositories.clip_repository import ClipRepository

logger = get_logger(__name__)


async def run_auto_cleanup_job(db: AsyncSession) -> int:
    """Run auto-cleanup job for all users based on their retention settings."""
    logger.info("Starting auto-cleanup background job...")
    clip_repo = ClipRepository(db)

    # Fetch all user settings with non-never retention policies
    stmt = select(UserSettings).where(UserSettings.auto_cleanup_days != "never")
    result = await db.execute(stmt)
    settings_list = result.scalars().all()

    total_deleted = 0
    now = datetime.now(UTC)

    for settings in settings_list:
        try:
            days = int(settings.auto_cleanup_days)
            cutoff = now - timedelta(days=days)
            deleted_count = await clip_repo.delete_expired_unpinned(
                user_id=settings.user_id,
                cutoff_time=cutoff,
            )
            total_deleted += deleted_count
        except (ValueError, TypeError):
            continue

    await db.commit()
    logger.info(f"Auto-cleanup job completed. Total unpinned clips pruned: {total_deleted}")
    return total_deleted
