import json
import random
import string
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.cache.redis import get_redis_client
from app.core.exceptions import InternalServerError, NotFoundError
from app.models.clip import ClipType
from app.models.user import User
from app.services.board_service import BoardService
from app.services.clip_service import ClipService

GUEST_BOARD_TTL_SECONDS = 86400  # 24 Hours


class GuestService:
    """Service handling temporary Guest Sessions, 24-hr Redis TTL, Board Codes, and Promotion."""

    @staticmethod
    def generate_board_code() -> str:
        """Generate a board code with an 8-char random suffix (e.g. NEXUS-A1B2C3D4).

        The ``NEXUS-`` prefix is fixed and adds zero entropy.  The suffix
        uses uppercase letters + digits (36 symbols), so k=8 yields
        36^8 ≈ 2.82 × 10¹² possible codes — infeasible to brute-force
        even without rate-limiting.
        """
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"NEXUS-{suffix}"

    async def get_or_create_session(
        self,
        guest_session_id: str | None = None,
    ) -> dict[str, Any]:
        """Fetch existing guest session or initialize a new one in Redis."""
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable. Cannot process guest sessions.")

        if guest_session_id:
            key = f"guest_session:{guest_session_id}"
            data_bytes = await redis.get(key)
            if data_bytes:
                raw = data_bytes.decode("utf-8") if isinstance(data_bytes, bytes) else data_bytes
                data = json.loads(raw)
                return data

        # Create new session
        new_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=GUEST_BOARD_TTL_SECONDS)

        session_data: dict[str, Any] = {
            "guest_session_id": new_id,
            "board_code": None,  # Hidden until first clip is created
            "board_name": "Guest Board",
            "expires_at": expires_at.isoformat(),
            "clips": [],
        }

        key = f"guest_session:{new_id}"
        await redis.setex(
            key,
            GUEST_BOARD_TTL_SECONDS,
            json.dumps(session_data),
        )

        return session_data

    async def add_guest_clip(
        self,
        guest_session_id: str,
        clip_type: str = "text",
        title: str = "Untitled Clip",
        content: str | None = None,
        file_url: str | None = None,
        file_name: str | None = None,
        file_size: int | None = None,
        tags: list[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Add a clip to guest session in Redis. Generates Board Code on 1st clip."""
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        session = await self.get_or_create_session(guest_session_id)

        # Per PRODUCT_SPEC.md §4: Board Code appears after first Clip is created
        if session["board_code"] is None:
            board_code = self.generate_board_code()
            session["board_code"] = board_code
            # Also store a reverse index for board_code -> session_id
            await redis.setex(
                f"guest_code:{board_code}",
                GUEST_BOARD_TTL_SECONDS,
                session["guest_session_id"],
            )

        new_clip = {
            "id": str(uuid.uuid4()),
            "board_id": None,
            "type": clip_type,
            "title": title or "Untitled Clip",
            "content": content,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "tags": tags or [],
            "is_pinned": False,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

        session["clips"].insert(0, new_clip)

        key = f"guest_session:{session['guest_session_id']}"
        await redis.setex(
            key,
            GUEST_BOARD_TTL_SECONDS,
            json.dumps(session),
        )

        return session, new_clip

    async def continue_guest_board(self, board_code: str) -> dict[str, Any]:
        """Find guest session by board code for cross-device continuation."""
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        clean_code = board_code.strip().upper()
        session_id = await redis.get(f"guest_code:{clean_code}")

        if not session_id:
            raise NotFoundError(f"Guest Board with code '{board_code}' not found or expired.")

        session_id_str = session_id.decode("utf-8") if isinstance(session_id, bytes) else session_id
        return await self.get_or_create_session(session_id_str)

    async def promote_guest_board(
        self,
        guest_session_id: str,
        user: User,
        clip_service: ClipService,
        board_service: BoardService,
    ) -> tuple[uuid.UUID, str, int]:
        """Promote guest board clips into a permanent User Board upon login."""
        redis = get_redis_client()
        if redis is None:
            raise InternalServerError("Redis is currently unavailable.")
        session = await self.get_or_create_session(guest_session_id)

        clips_data = session.get("clips", [])
        if not clips_data:
            # Nothing to promote, get default board
            boards = await board_service.list_user_boards(user)
            return boards[0][0].id, boards[0][0].name, 0

        # Create new permanent board for promoted guest content
        new_board = await board_service.create_board(
            user=user,
            name="Imported Guest Board",
        )

        count = 0
        for clip_item in clips_data:
            c_type = clip_item.get("type", "text")
            try:
                enum_type = ClipType(c_type)
            except ValueError:
                enum_type = ClipType.TEXT

            await clip_service.create_clip(
                user=user,
                board_id=new_board.id,
                clip_type=enum_type,
                title=clip_item.get("title", "Untitled Clip"),
                content=clip_item.get("content"),
                file_url=clip_item.get("file_url"),
                file_name=clip_item.get("file_name"),
                file_size=clip_item.get("file_size"),
                tags=clip_item.get("tags", []),
                is_pinned=clip_item.get("is_pinned", False),
            )
            count += 1

        # Cleanup guest session from Redis after promotion
        await redis.delete(f"guest_session:{guest_session_id}")
        if session.get("board_code"):
            await redis.delete(f"guest_code:{session['board_code']}")

        return new_board.id, new_board.name, count
