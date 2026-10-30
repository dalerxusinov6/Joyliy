"""Pytest fixtures and test environment configuration."""

import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.database import Base
from src.api.app import create_app
from src.config import settings
from src.services.listing_service import ListingService
from src.services.notification_service import NotificationService
from src.classification.engine import ClassificationEngine


# Test database in memory
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean isolated in-memory database session for each test."""
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def classifier() -> ClassificationEngine:
    return ClassificationEngine()


@pytest.fixture
def listing_service_test(classifier) -> ListingService:
    return ListingService(classifier=classifier)


class MockTelegramBot:
    """Mock aiogram Bot capturing sent messages without making network calls."""

    def __init__(self):
        self.sent_messages = []
        self.sent_photos = []
        self.force_retry_after: int = 0
        self.force_forbidden: bool = False

    async def send_message(self, chat_id: int, text: str, reply_markup=None, **kwargs):
        if self.force_forbidden:
            from aiogram.exceptions import TelegramForbiddenError
            raise TelegramForbiddenError(method="sendMessage", message="Bot blocked by user")
        if self.force_retry_after > 0:
            from aiogram.exceptions import TelegramRetryAfter
            wait = self.force_retry_after
            self.force_retry_after = 0  # clear so retry succeeds
            raise TelegramRetryAfter(method="sendMessage", message="Flood control", retry_after=wait)

        msg = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup, **kwargs}
        self.sent_messages.append(msg)
        return type("MockMsg", (), {"message_id": len(self.sent_messages)})()

    async def send_photo(self, chat_id: int, photo: str, caption: str, reply_markup=None, **kwargs):
        if self.force_forbidden:
            from aiogram.exceptions import TelegramForbiddenError
            raise TelegramForbiddenError(method="sendPhoto", message="Bot blocked by user")
        if self.force_retry_after > 0:
            from aiogram.exceptions import TelegramRetryAfter
            wait = self.force_retry_after
            self.force_retry_after = 0
            raise TelegramRetryAfter(method="sendPhoto", message="Flood control", retry_after=wait)

        msg = {"chat_id": chat_id, "photo": photo, "caption": caption, "reply_markup": reply_markup, **kwargs}
        self.sent_photos.append(msg)
        return type("MockMsg", (), {"message_id": len(self.sent_photos)})()

    async def send_media_group(self, chat_id: int, media: list, **kwargs):
        if self.force_forbidden:
            from aiogram.exceptions import TelegramForbiddenError
            raise TelegramForbiddenError(method="sendMediaGroup", message="Bot blocked")
        self.sent_photos.append({"chat_id": chat_id, "media": media, **kwargs})
        return [type("MockMsg", (), {"message_id": 777})()]


@pytest.fixture
def mock_bot() -> MockTelegramBot:
    return MockTelegramBot()


@pytest_asyncio.fixture
async def api_client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing REST API endpoints."""
    app = create_app()

    # Override get_db_session dependency to use test_session
    from src.database import get_db_session
    async def override_get_db_session():
        yield test_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
