from redis.asyncio import Redis, RedisError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client: Redis | None = None


async def connect_redis() -> None:
    """Initialize and connect the async Redis client."""
    global redis_client
    if not settings.redis_enabled:
        logger.info("Redis is disabled in configuration. Skipping connection.")
        return

    logger.info("Connecting to Redis...")
    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully.")
    except RedisError:
        logger.exception("Failed to connect to Redis")
        redis_client = None
        raise


async def disconnect_redis() -> None:
    """Gracefully close active Redis connection."""
    global redis_client
    if redis_client is not None:
        logger.info("Closing Redis client connection...")
        try:
            await redis_client.aclose()
            logger.info("Redis connection closed successfully.")
        except RedisError:
            logger.exception("Failed to close Redis connection")
        finally:
            redis_client = None


async def check_redis_health() -> bool:
    """Verify Redis server connectivity internally."""
    if not settings.redis_enabled or redis_client is None:
        return False
    try:
        return bool(await redis_client.ping())
    except RedisError:
        logger.exception("Redis health check failed")
        return False


def get_redis_client() -> Redis | None:
    """Return the current global Redis client instance."""
    return redis_client