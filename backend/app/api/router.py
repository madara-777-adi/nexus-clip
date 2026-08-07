from fastapi import APIRouter

from app.api import clips,health

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(clips.router)