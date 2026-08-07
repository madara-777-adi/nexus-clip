from fastapi import APIRouter

from app.api import auth,clips,health

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(clips.router)
router.include_router(auth.router)