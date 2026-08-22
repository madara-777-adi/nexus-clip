import asyncio
from urllib.parse import parse_qs, urlparse

import yt_dlp
from pydantic import BaseModel, ConfigDict

from app.core.exceptions import ValidationError
from app.models.clip import Platform


class MetadataExtractionError(Exception):
    """Raised when metadata extraction fails."""


class ExtractedMetadata(BaseModel):
    """Normalized metadata extracted from supported platforms."""

    model_config = ConfigDict(frozen=True)

    title: str
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    uploader: str | None = None
    webpage_url: str


class MetadataService:
    """Service responsible for URL normalization, platform detection, and metadata extraction."""

    def normalize_url(self, url: str) -> str:
        """Normalize supported URLs into a canonical form."""

        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if host in (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
        ):
            query = parse_qs(parsed.query)

            if "v" in query:
                return (
                    f"https://www.youtube.com/watch?v={query['v'][0]}"
                )

            if parsed.path.startswith("/shorts/"):
                video_id = parsed.path.split("/")[2]
                return (
                    f"https://www.youtube.com/watch?v={video_id}"
                )

            if parsed.path.startswith("/embed/"):
                video_id = parsed.path.split("/")[2]
                return (
                    f"https://www.youtube.com/watch?v={video_id}"
                )

        if host == "youtu.be":
            video_id = parsed.path.strip("/")
            return f"https://www.youtube.com/watch?v={video_id}"

        return url

    def detect_platform(self, url: str) -> Platform:
        """Detect the source platform from a normalized URL."""

        host = urlparse(url).netloc.lower()

        if host in (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
        ):
            return Platform.YOUTUBE

        raise ValidationError(
            f"Unsupported platform: {url}"
        )

    def _fetch_metadata_sync(
        self,
        url: str,
    ) -> ExtractedMetadata:
        """Fetch metadata synchronously using yt-dlp."""

        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    url,
                    download=False,
                )

            if info is None:
                raise MetadataExtractionError(
                    "yt-dlp returned no metadata."
                )

            return ExtractedMetadata(
                title=info.get("title", "Unknown Title"),
                thumbnail_url=info.get("thumbnail"),
                duration_seconds=info.get("duration"),
                uploader=info.get("uploader"),
                webpage_url=info.get(
                    "webpage_url",
                    url,
                ),
            )

        except Exception as exc:
            raise MetadataExtractionError(
                f"Failed to extract metadata: {exc}"
            ) from exc

    async def fetch_metadata(
        self,
        url: str,
    ) -> ExtractedMetadata:
        """Fetch metadata asynchronously."""

        return await asyncio.to_thread(
            self._fetch_metadata_sync,
            url,
        )
