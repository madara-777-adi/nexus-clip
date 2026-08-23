"""Rate-limiting middleware using slowapi.

The limiter is keyed on client IP and uses an in-memory backend by default.
When Redis is available (production), the ``REDIS_URL`` will be used
automatically via the storage URI passed at initialisation.

Usage in endpoint modules::

    from app.middleware.rate_limit import limiter

    @router.post("/example")
    @limiter.limit("10/minute")
    async def example(request: Request):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Use Redis as the rate-limit storage backend when available, falling
# back to in-memory for tests and local development without Redis.
_storage_uri = settings.redis_url if settings.redis_enabled else "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
    # Return clean JSON 429 errors rather than raw text.
    default_limits=[],
)
