import json
import os
import secrets
import uuid
from functools import partial
from pathlib import Path

import anyio
import boto3
from fastapi import UploadFile

from app.cache.redis import get_redis_client
from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)

UPLOAD_DIR = Path("/tmp/nexus_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# .html and .svg removed: they can execute as scripts if served inline.
# Content-Disposition: attachment is enforced at the serving layer, but
# we still exclude them here as defence in depth — no legitimate clip
# type requires raw HTML or SVG uploads.
ALLOWED_EXTENSIONS = {
    # Images (raster only — no SVG)
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    # Documents
    ".pdf", ".txt", ".md", ".csv", ".json", ".doc", ".docx",
    # Audio/Video
    ".mp3", ".wav", ".mp4", ".webm",
    # Archives
    ".zip", ".tar", ".gz",
    # Source code
    ".py", ".js", ".ts", ".css", ".java", ".cpp", ".rs", ".go",
}

# Chunk size for streaming reads (64 KB)
_READ_CHUNK_SIZE = 64 * 1024
FILE_ACCESS_TTL_SECONDS = 86400


class CloudflareR2StorageDriver:
    """Persist uploaded objects in Cloudflare R2 through its S3 API."""

    def __init__(self) -> None:
        required = {
            "R2_ENDPOINT_URL": settings.r2_endpoint_url,
            "R2_ACCESS_KEY_ID": settings.r2_access_key_id,
            "R2_SECRET_ACCESS_KEY": settings.r2_secret_access_key,
            "R2_BUCKET_NAME": settings.r2_bucket_name,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise InternalServerError(
                f"Cloudflare R2 storage is not configured: missing {', '.join(missing)}."
            )
        self.bucket_name = settings.r2_bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
        )

    async def save(self, key: str, content: bytes, content_type: str) -> None:
        await anyio.to_thread.run_sync(
            partial(
                self.client.put_object,
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
            ),
        )

    async def read(self, key: str) -> bytes:
        response = await anyio.to_thread.run_sync(
            partial(self.client.get_object, Bucket=self.bucket_name, Key=key),
        )
        return await anyio.to_thread.run_sync(response["Body"].read)

    async def delete(self, key: str) -> None:
        await anyio.to_thread.run_sync(
            partial(self.client.delete_object, Bucket=self.bucket_name, Key=key),
        )


class StorageService:
    """Service handling durable R2 storage and file access authorization."""

    def __init__(self, driver: CloudflareR2StorageDriver | None = None) -> None:
        self.driver = driver

    @property
    def r2_driver(self) -> CloudflareR2StorageDriver:
        if self.driver is None:
            self.driver = CloudflareR2StorageDriver()
        return self.driver

    async def save_file(
        self,
        file: UploadFile,
        *,
        owner_id: str,
        owner_type: str,
    ) -> dict[str, str | int]:
        """Validate and save uploaded file, returning metadata.

        The file is read in chunks so that an oversized payload is rejected
        as soon as the cumulative size exceeds the configured limit, rather
        than buffering the entire body into memory first.
        """
        if not file.filename:
            raise ValidationError("File must have a filename.")

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File type '{ext}' is not allowed. "
                f"Permitted types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        max_bytes = settings.max_upload_size_mb * 1024 * 1024

        # --- Early rejection via Content-Length header (if available) ---
        # Starlette's UploadFile exposes .size from the multipart parser
        # when the client sends a Content-Length header.  Check it first
        # to avoid even starting the chunked read for obviously-too-large
        # uploads.
        if file.size is not None and file.size > max_bytes:
            raise FileTooLargeError(
                f"File size {file.size / (1024 * 1024):.1f} MB exceeds the "
                f"{settings.max_upload_size_mb} MB limit."
            )

        # --- Streaming read with cumulative size guard ---
        chunks: list[bytes] = []
        total_size = 0
        while True:
            chunk = await file.read(_READ_CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_bytes:
                raise FileTooLargeError(
                    f"File size exceeds the {settings.max_upload_size_mb} MB limit."
                )
            chunks.append(chunk)

        content = b"".join(chunks)
        file_size = len(content)

        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{Path(file.filename).name}"
        await self.r2_driver.save(
            safe_filename,
            content,
            file.content_type or "application/octet-stream",
        )

        access_token = secrets.token_urlsafe(32)
        redis = get_redis_client()
        if redis is None:
            await self.r2_driver.delete(safe_filename)
            raise InternalServerError("Redis is currently unavailable. Cannot secure uploaded files.")
        metadata = {
            "file_id": file_id,
            "filename": safe_filename,
            "storage": "r2",
            "owner_id": owner_id,
            "owner_type": owner_type,
        }
        ttl = FILE_ACCESS_TTL_SECONDS if owner_type == "guest" else 0
        if owner_type == "guest":
            guest_session = await redis.get(f"guest_session:{owner_id}")
            if not guest_session:
                await self.r2_driver.delete(safe_filename)
                raise ForbiddenError("Guest session is invalid or expired.")
        if ttl:
            await redis.setex(
                f"file_access:{access_token}",
                ttl,
                json.dumps(metadata),
            )
        else:
            await redis.set(
                f"file_access:{access_token}",
                json.dumps(metadata),
            )
        file_url = f"/static/uploads/{safe_filename}?token={access_token}"

        return {
            "file_id": file_id,
            "file_url": file_url,
            "file_name": file.filename,
            "file_size": file_size,
        }

    async def authorize_file(
        self,
        filename: str,
        access_token: str | None,
        *,
        owner_id: str | None = None,
        owner_type: str | None = None,
    ) -> dict[str, str]:
        """Validate a file token and, when supplied, its ownership."""
        if not access_token:
            raise ForbiddenError("A file access token is required.")
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        raw = await redis.get(f"file_access:{access_token}")
        if not raw:
            raise NotFoundError("File not found or access token expired.")
        metadata = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        if metadata.get("filename") != filename:
            raise ForbiddenError("File access token does not match this file.")
        if owner_id is not None and (
            metadata.get("owner_id") != owner_id or metadata.get("owner_type") != owner_type
        ):
            raise ForbiddenError("You do not own this file.")
        return metadata

    async def read_file(self, metadata: dict[str, str]) -> tuple[bytes, str]:
        """Read an authorized file from R2 or a legacy local record."""
        if metadata.get("storage") == "r2":
            return await self.r2_driver.read(metadata["filename"]), metadata["filename"]

        file_path = (UPLOAD_DIR / metadata["filename"]).resolve()
        if not file_path.is_relative_to(UPLOAD_DIR.resolve()) or not file_path.is_file():
            raise NotFoundError("File not found.")
        return await anyio.to_thread.run_sync(file_path.read_bytes), metadata["filename"]

    async def delete_file(self, file_url: str, access_token: str, *, owner_id: str, owner_type: str) -> None:
        """Remove an owned file from local storage and its access registry."""
        if not file_url.startswith("/static/uploads/"):
            raise ValidationError("Invalid file URL.")
        filename = file_url.removeprefix("/static/uploads/").split("?", 1)[0]
        metadata = await self.authorize_file(
            filename,
            access_token,
            owner_id=owner_id,
            owner_type=owner_type,
        )
        if metadata.get("storage") == "r2":
            await self.r2_driver.delete(filename)
        else:
            file_path = (UPLOAD_DIR / filename).resolve()
            if not file_path.is_relative_to(UPLOAD_DIR.resolve()):
                raise ValidationError("Invalid file path.")
            if not file_path.is_file():
                raise NotFoundError("File not found.")
            os.remove(file_path)
        redis = get_redis_client()
        if redis is not None:
            await redis.delete(f"file_access:{access_token}")
