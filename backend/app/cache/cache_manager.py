import asyncio
import json
from collections import defaultdict
from contextlib import suppress
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from redis.asyncio import RedisError

from app.cache.redis import get_redis_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

BOARD_CHANNEL_PREFIX = "nexus:board:"


class WebSocketConnectionManager:
    """Manage worker-local WebSocket clients backed by Redis Pub/Sub."""

    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.subscription_tasks: dict[str, asyncio.Task[None]] = {}

    async def connect(self, board_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[board_id].add(websocket)
        if board_id not in self.subscription_tasks:
            self.subscription_tasks[board_id] = asyncio.create_task(
                self._subscribe_to_board(board_id)
            )

    async def disconnect(self, board_id: str, websocket: WebSocket) -> None:
        board_connections = self.connections.get(board_id)
        if board_connections is None:
            return

        board_connections.discard(websocket)
        if board_connections:
            return

        self.connections.pop(board_id, None)
        task = self.subscription_tasks.pop(board_id, None)
        if task is not None and task is not asyncio.current_task():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def _subscribe_to_board(self, board_id: str) -> None:
        client = get_redis_client()
        if client is None:
            logger.warning("Cannot subscribe WebSocket clients: Redis is unavailable.")
            return

        pubsub = client.pubsub()
        channel = f"{BOARD_CHANNEL_PREFIX}{board_id}"
        try:
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                await self.broadcast(board_id, message["data"])
        except asyncio.CancelledError:
            raise
        except RedisError:
            logger.exception("Redis Pub/Sub subscription failed for board '%s'.", board_id)
        finally:
            with suppress(RedisError):
                await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            if self.subscription_tasks.get(board_id) is asyncio.current_task():
                self.subscription_tasks.pop(board_id, None)

    async def broadcast(self, board_id: str, message: str) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.connections.get(board_id, set()).copy():
            try:
                await websocket.send_text(message)
            except (OSError, RuntimeError, WebSocketDisconnect):
                disconnected.append(websocket)

        for websocket in disconnected:
            await self.disconnect(board_id, websocket)

    async def shutdown(self) -> None:
        tasks = list(self.subscription_tasks.values())
        self.subscription_tasks.clear()
        for task in tasks:
            task.cancel()
        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task
        self.connections.clear()


websocket_manager = WebSocketConnectionManager()


async def publish_board_event(board_id: str, event: dict[str, Any]) -> bool:
    """Publish a JSON clip event for every worker serving the board."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cannot publish board event: Redis is unavailable.")
        return False

    channel = f"{BOARD_CHANNEL_PREFIX}{board_id}"
    try:
        await client.publish(channel, json.dumps(jsonable_encoder(event)))
        return True
    except (AttributeError, RedisError, TypeError, ValueError):
        logger.exception("Redis Pub/Sub publish failed for board '%s'.", board_id)
        return False


async def get(key: str) -> Any | None:
    """Retrieve a value from cache, automatically deserializing JSON if applicable."""
    if not settings.redis_enabled:
        return None

    client = get_redis_client()
    if client is None:
        logger.warning("Cache read attempted while Redis client is unavailable.")
        return None

    try:
        value = await client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    except RedisError:
        logger.exception("Cache GET failed for key '%s'", key)
        return None


async def set(key: str, value: Any, ttl: int | None = None) -> bool:
    """Set a value in cache with optional TTL after encoding with jsonable_encoder."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache write attempted while Redis client is unavailable.")
        return False

    effective_ttl = ttl if ttl is not None else settings.cache_default_ttl

    try:
        encoded_value = jsonable_encoder(value)
        serialized_value = json.dumps(encoded_value)

        if effective_ttl > 0:
            await client.setex(key, effective_ttl, serialized_value)
        else:
            await client.set(key, serialized_value)

        return True

    except (RedisError, TypeError, ValueError):
        logger.exception("Cache SET failed for key '%s'", key)
        return False


async def delete(key: str) -> bool:
    """Delete a key from cache."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache delete attempted while Redis client is unavailable.")
        return False

    try:
        deleted_count = await client.delete(key)
        return deleted_count > 0

    except RedisError:
        logger.exception("Cache DELETE failed for key '%s'", key)
        return False


async def exists(key: str) -> bool:
    """Check if a key exists in cache."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache exists check attempted while Redis client is unavailable.")
        return False

    try:
        return bool(await client.exists(key))

    except RedisError:
        logger.exception("Cache EXISTS failed for key '%s'", key)
        return False


async def expire(key: str, ttl: int) -> bool:
    """Set expiration TTL in seconds for an existing key."""
    if not settings.redis_enabled:
        return False

    client = get_redis_client()
    if client is None:
        logger.warning("Cache EXPIRE attempted while Redis client is unavailable.")
        return False

    try:
        return bool(await client.expire(key, ttl))

    except RedisError:
        logger.exception("Cache EXPIRE failed for key '%s'", key)
        return False


async def ttl(key: str) -> int:
    """Return the remaining TTL for a key in seconds (-2 if not found, -1 if no TTL)."""
    if not settings.redis_enabled:
        return -2

    client = get_redis_client()
    if client is None:
        logger.warning("Cache TTL query attempted while Redis client is unavailable.")
        return -2

    try:
        return await client.ttl(key)

    except RedisError:
        logger.exception("Cache TTL failed for key '%s'", key)
        return -2
