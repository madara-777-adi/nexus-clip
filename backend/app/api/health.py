from fastapi import APIRouter

from app.core.config import settings
from app.schemas.response import APIResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=APIResponse[dict])
async def health_check() -> APIResponse[dict]:
    """Health check endpoint for monitoring and load balancers."""
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={
            "status": "healthy",
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "environment": settings.environment,
        },
    )
