import asyncio
import mimetypes
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import router
from app.cache.redis import connect_redis, disconnect_redis
from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import configure_logging, get_logger
from app.db.init_db import create_tables, init_db
from app.db.session import AsyncSessionLocal, close_db_engine
from app.jobs.cleanup_job import run_auto_cleanup_job
from app.middleware.rate_limit import limiter
from app.schemas.response import ErrorResponse
from app.storage.service import StorageService

# Configure logging before acquiring logger instances
configure_logging()
logger = get_logger(__name__)

# Maximum allowed request body size (defence in depth at the HTTP layer).
# This is slightly larger than max_upload_size_mb to allow for multipart
# overhead (boundary markers, headers, form fields).
MAX_BODY_BYTES = (settings.max_upload_size_mb + 2) * 1024 * 1024
CLEANUP_INTERVAL_SECONDS = 60 * 60


async def _run_cleanup_loop() -> None:
    """Run the database cleanup job immediately and once every hour."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await run_auto_cleanup_job(db)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled auto-cleanup job failed")

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Reject requests whose Content-Length exceeds the configured limit.

    This provides defence in depth at the HTTP layer, before the request
    body is ever read by a handler or the storage service.
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > MAX_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "success": False,
                            "message": (
                                f"Request body too large. "
                                f"Maximum allowed: {settings.max_upload_size_mb} MB."
                            ),
                            "errors": [],
                        },
                    )
            except ValueError:
                pass  # Malformed Content-Length — let downstream handle it
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        await init_db()
        await create_tables()
        await connect_redis()
        cleanup_task = asyncio.create_task(_run_cleanup_loop())

        try:
            yield
        finally:
            cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await cleanup_task

    finally:
        try:
            await disconnect_redis()
        except Exception:
            logger.exception("Redis shutdown failed")

        try:
            await close_db_engine()
        except Exception:
            logger.exception("Database engine shutdown failed")

        logger.info(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # ── Rate Limiter ──────────────────────────────────────────────────
    app.state.limiter = limiter

    # ── Body-size guard (defence in depth) ────────────────────────────
    app.add_middleware(MaxBodySizeMiddleware)

    # ── CORS Middleware ───────────────────────────────────────────────
    # Uses the cors_origins list from settings (env: CORS_ORIGINS).
    # Defaults to ["http://localhost:3000"] for dev; production must
    # override via env var with the actual frontend origin(s).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve authorized raster images inline for previews; force-download every
    # other supported file type so executable content is never rendered.
    @app.get("/static/uploads/{filename}")
    async def serve_upload(
        filename: str,
        token: str = Query(...),
    ) -> Response:
        """Serve an authorized upload with a safe disposition."""
        storage = StorageService()
        metadata = await storage.authorize_file(filename, token)
        content, stored_filename = await storage.read_file(metadata)
        media_type, _ = mimetypes.guess_type(stored_filename)
        disposition = "inline" if media_type and media_type.startswith("image/") else "attachment"
        return Response(
            content=content,
            media_type=media_type or "application/octet-stream",
            headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
        )

    # ── Exception Handlers ────────────────────────────────────────────

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """Return a clean 429 JSON error instead of a raw exception."""
        return JSONResponse(
            status_code=429,
            content=ErrorResponse(
                success=False,
                message="Too many requests. Please slow down.",
                errors=[],
            ).model_dump(),
        )

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions."""
        logger.warning(
            f"API Exception: {exc.message}",
            extra={"status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                message=exc.message,
                errors=exc.errors,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle Pydantic validation errors from request bodies."""
        errors: list[dict[str, str]] = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error.get("loc", [])[1:])
            errors.append(
                {
                    "field": field or "unknown",
                    "detail": str(error.get("msg")),
                    "type": str(error.get("type")),
                }
            )

        logger.warning(f"Validation error on {request.url.path}", extra={"errors": errors})

        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                message="Validation failed",
                errors=errors,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.exception(
            "Unexpected exception: %s",
            exc,
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message="Internal server error",
                errors=[],
            ).model_dump(),
        )

    @app.get("/health")
    async def health_check():
        """Liveness check for deployment platforms."""
        return {"status": "ok"}

    # Router
    app.include_router(router)

    return app


app = create_app()

if __name__ == "__main__":
    import os
    import uvicorn

    # Render and other PaaS providers inject PORT
    port = int(os.environ.get("PORT", settings.port))

    uvicorn.run(
        app,
        host=settings.host,
        port=port,
        log_config=None,
    )
