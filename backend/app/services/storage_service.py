"""Backward-compatible imports for the storage service."""

from app.storage.service import (
    ALLOWED_EXTENSIONS,
    UPLOAD_DIR,
    CloudflareR2StorageDriver,
    StorageService,
    get_redis_client,
)

__all__ = [
    "ALLOWED_EXTENSIONS",
    "UPLOAD_DIR",
    "CloudflareR2StorageDriver",
    "StorageService",
    "get_redis_client",
]
