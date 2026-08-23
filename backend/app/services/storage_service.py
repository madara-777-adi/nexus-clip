import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, ValidationError

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


class StorageService:
    """Service handling file storage (local disk).

    Cloudflare R2 integration is intentionally deferred; the application
    currently uses local /tmp storage.  R2 credentials have been removed
    from .env.example — add them and implement the boto3 S3 upload path
    in a future PR when persistent object storage is required.
    """

    async def save_file(self, file: UploadFile) -> dict[str, str | int]:
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
        destination = UPLOAD_DIR / safe_filename

        import anyio
        async with await anyio.open_file(destination, "wb") as f:
            await f.write(content)

        file_url = f"/static/uploads/{safe_filename}"

        return {
            "file_id": file_id,
            "file_url": file_url,
            "file_name": file.filename,
            "file_size": file_size,
        }

    async def delete_file(self, file_url: str) -> None:
        """Remove file from local storage."""
        if not file_url.startswith("/static/uploads/"):
            return
        filename = file_url.replace("/static/uploads/", "")
        try:
            file_path = (UPLOAD_DIR / filename).resolve()
            if file_path.is_relative_to(UPLOAD_DIR.resolve()) and file_path.is_file():
                os.remove(file_path)
        except (OSError, ValueError):
            pass
