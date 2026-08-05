from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router
from app.cache.redis import connect_redis, disconnect_redis
from app.core.config import settings
from app.core.exceptions import APIException
from app.core.logging import configure_logging, get_logger
from app.db.init_db import init_db
from app.db.session import close_db_engine
from app.schemas.response import ErrorResponse

# Configure logging before acquiring logger instances
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        await init_db()
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

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
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
            field = ".".join(str(x) for x in error["loc"][1:])
            errors.append(
                {
                    "field": field or "unknown",
                    "detail": error["msg"],
                    "type": error["type"],
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
        logger.error(
            f"Unexpected exception: {str(exc)}",
            exc_info=True,
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

    # Router
    app.include_router(router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_config=None,
    )