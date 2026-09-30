from collections.abc import AsyncGenerator
from typing import ClassVar

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class MockRedis:
    """In-memory Redis mock for guest session tests."""

    def __init__(self):
        self.store = {}

    async def get(self, name: str):
        return self.store.get(name)

    async def setex(self, name: str, time: int, value: str):
        self.store[name] = value.encode("utf-8") if isinstance(value, str) else value

    async def set(self, name: str, value: str):
        self.store[name] = value.encode("utf-8") if isinstance(value, str) else value

    async def delete(self, *names: str):
        for name in names:
            self.store.pop(name, None)

    async def publish(self, channel: str, message: str):
        return 0


class MockR2StorageDriver:
    """In-memory R2 replacement for upload tests."""

    objects: ClassVar[dict[str, bytes]] = {}

    async def save(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = content

    async def read(self, key: str) -> bytes:
        return self.objects[key]

    async def delete(self, key: str) -> None:
        self.objects.pop(key, None)


mock_redis_instance = MockRedis()


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Create all tables before each test and drop them afterwards."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    # Override DB dependency
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override

    # Patch redis
    def _mock_get_redis():
        return mock_redis_instance

    monkeypatch.setattr("app.cache.redis.get_redis_client", _mock_get_redis)
    monkeypatch.setattr("app.services.guest_service.get_redis_client", _mock_get_redis)
    monkeypatch.setattr("app.services.storage_service.get_redis_client", _mock_get_redis)
    monkeypatch.setattr("app.storage.service.get_redis_client", _mock_get_redis)
    MockR2StorageDriver.objects.clear()
    monkeypatch.setattr("app.storage.service.CloudflareR2StorageDriver", MockR2StorageDriver)
    mock_redis_instance.store.clear()
    await mock_redis_instance.set("guest_session:guest-upload-test", "{}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
