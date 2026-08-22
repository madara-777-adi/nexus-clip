from fastapi import APIRouter

from app.api import auth, boards, clips, guest, health, search, settings, upload

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(guest.router)
router.include_router(boards.router)
router.include_router(clips.router)
router.include_router(upload.router)
router.include_router(search.router)
router.include_router(settings.router)
