from sqlalchemy import text

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import engine

logger = get_logger(__name__)


async def init_db() -> None:
    """Verify connectivity and initialize database connection pool."""
    logger.info("Initializing database connection...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception:
        logger.exception("Database initialization failed")
        raise


async def create_tables() -> None:
    """Create database tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_health() -> bool:
    """Perform health check query against the database internally."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        logger.exception("Database health check failed")
        return False
