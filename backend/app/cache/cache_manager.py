import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from redis.asyncio import RedisError

from app.cache.redis import get_redis_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get(key: str) -> Any | None:
    """Retrieve a value from cache, automatically deserializing JSON if applicable."""
    if not settings.redis_enabled:
        return None

    client = get_redis_client()
    if client is None:
        logger.warning("Cache read attempted while Redis client is unavailable.")
        return None

    try:
        value = await client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    except RedisError:
        logger.exception("Cache GET failed for key '%s'", key)
        return None


async def set(key: str, value: Any, ttl: int | None = None) -> bool:
    """Set a value in cache with optional TTL after encoding with jsonable_encoder."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache write attempted while Redis client is unavailable.")
        return False

    effective_ttl = ttl if ttl is not None else settings.cache_default_ttl

    try:
        encoded_value = jsonable_encoder(value)
        serialized_value = json.dumps(encoded_value)

        if effective_ttl > 0:
            await client.setex(key, effective_ttl, serialized_value)
        else:
            await client.set(key, serialized_value)

        return True

    except (RedisError, TypeError, ValueError):
        logger.exception("Cache SET failed for key '%s'", key)
        return False


async def delete(key: str) -> bool:
    """Delete a key from cache."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache delete attempted while Redis client is unavailable.")
        return False

    try:
        deleted_count = await client.delete(key)
        return deleted_count > 0

    except RedisError:
        logger.exception("Cache DELETE failed for key '%s'", key)
        return False


async def exists(key: str) -> bool:
    """Check if a key exists in cache."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache exists check attempted while Redis client is unavailable.")
        return False

    try:
        return bool(await client.exists(key))

    except RedisError:
        logger.exception("Cache EXISTS failed for key '%s'", key)
        return False


async def expire(key: str, ttl: int) -> bool:
    """Set expiration TTL in seconds for an existing key."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache EXPIRE attempted while Redis client is unavailable.")
        return False

    try:
        return bool(await client.expire(key, ttl))

    except RedisError:
        logger.exception("Cache EXPIRE failed for key '%s'", key)
        return False


async def ttl(key: str) -> int:
    """Return the remaining TTL for a key in seconds (-2 if not found, -1 if no TTL)."""
    if not settings.redis_enabled:
        return -2

    client = get_redis_client()
    if client is None:
        logger.warning("Cache TTL query attempted while Redis client is unavailable.")
        return -2

    try:
        return await client.ttl(key)

    except RedisError:
        logger.exception("Cache TTL failed for key '%s'", key)
        return -2