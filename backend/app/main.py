import mimetypes
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import router
from app.cache.redis import connect_redis, disconnect_redis
from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import configure_logging, get_logger
from app.db.init_db import create_tables, init_db
from app.db.session import close_db_engine
from app.middleware.rate_limit import limiter
from app.schemas.response import ErrorResponse

# Configure logging before acquiring logger instances
configure_logging()
logger = get_logger(__name__)

UPLOAD_DIR = Path("/tmp/nexus_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maximum allowed request body size (defence in depth at the HTTP layer).
# This is slightly larger than max_upload_size_mb to allow for multipart
# overhead (boundary markers, headers, form fields).
MAX_BODY_BYTES = (settings.max_upload_size_mb + 2) * 1024 * 1024


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

        yield

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

    # Serve uploaded files as forced downloads to prevent inline script execution.
    # Content-Disposition: attachment is set on every response regardless of file type,
    # so an uploaded .html/.svg can never run as a script in this origin.
    @app.get("/static/uploads/{filename}")
    async def serve_upload(filename: str) -> FileResponse:
        """Force-download any uploaded file — never render inline."""
        file_path = UPLOAD_DIR / filename
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        # Resolve the media type so the browser picks the right icon/app,
        # but the attachment disposition still prevents inline rendering.
        media_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(
            path=str(file_path),
            media_type=media_type or "application/octet-stream",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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
