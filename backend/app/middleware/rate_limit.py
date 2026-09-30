"""Redis-backed rate-limiting middleware using slowapi.

The limiter is keyed on client IP and requires Redis. Requests fail closed
with HTTP 503 when Redis is disabled, unavailable, or unreachable.

Usage in endpoint modules::

    from app.middleware.rate_limit import limiter

    @router.post("/example")
    @limiter.limit("10/minute")
    async def example(request: Request):
        ...
"""

from fastapi import HTTPException, Request, status
from redis.asyncio import RedisError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.cache import redis as redis_cache
from app.core.config import settings


class RedisRequiredLimiter(Limiter):
    """Limiter that refuses to process requests without a Redis backend."""

    def _check_request_limit(
        self,
        request: Request,
        endpoint_func,
        in_middleware: bool = True,
    ) -> None:
        if not settings.redis_enabled or redis_cache.get_redis_client() is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiting service is unavailable.",
            )

        try:
            super()._check_request_limit(request, endpoint_func, in_middleware)
        except RedisError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiting service is unavailable.",
            ) from exc


limiter = RedisRequiredLimiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    # Return clean JSON 429 errors rather than raw text.
    default_limits=[],
    in_memory_fallback_enabled=False,
    swallow_errors=False,
)
