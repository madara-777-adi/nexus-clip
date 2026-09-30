import json
from app.cache.redis import get_redis_client
from app.core.exceptions import InternalServerError

class FileAccessRepository:
    """Repository handling file access token persistence in Redis."""

    async def save_access_token(self, token: str, metadata: dict, ttl: int = 0) -> None:
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        if ttl > 0:
            await redis.setex(f"file_access:{token}", ttl, json.dumps(metadata))
        else:
            await redis.set(f"file_access:{token}", json.dumps(metadata))

    async def get_access_token(self, token: str) -> dict | None:
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        raw = await redis.get(f"file_access:{token}")
        if not raw:
            return None
        return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)

    async def delete_access_token(self, token: str) -> None:
        redis = get_redis_client()
        if redis is None:
            return
        await redis.delete(f"file_access:{token}")
