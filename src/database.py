"""Async Database Engine and Session Management using SQLAlchemy 2.x."""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def create_engine_and_session(db_url: str | None = None):
    """Factory to create an async engine and sessionmaker."""
    url = db_url or settings.DATABASE_URL

    # Normalize Render and Cloud provider PostgreSQL URLs to use asyncpg driver
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_async_engine(
        url,
        echo=settings.DB_ECHO,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return engine, session_maker


_engine, _session_maker = create_engine_and_session()
engine = _engine


class SessionMakerProxy:
    """Proxy ensuring callers always get the active sessionmaker even after fallback."""
    def __call__(self, *args, **kwargs):
        return _session_maker(*args, **kwargs)


AsyncSessionLocal = SessionMakerProxy()


def get_session_factory():
    """Return the active sessionmaker."""
    return _session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency helper to yield an async database session with automatic rollback on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables, with seamless local SQLite fallback if PostgreSQL is unreachable."""
    global engine, _engine, _session_maker
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            from sqlalchemy import text
            for col in ["contact_phone", "contact_telegram"]:
                try:
                    await conn.execute(text(f"ALTER TABLE listings ADD COLUMN {col} VARCHAR(128)"))
                except Exception:
                    pass
            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN photo_url VARCHAR(512)"))
            except Exception:
                pass
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        if not str(engine.url).startswith("sqlite"):
            logger.warning(
                "Configured database connection failed (%s). Falling back to local SQLite database 'uyda.db'.",
                exc,
            )
            _engine, _session_maker = create_engine_and_session("sqlite+aiosqlite:///uyda.db")
            engine = _engine
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                from sqlalchemy import text
                for col in ["contact_phone", "contact_telegram"]:
                    try:
                        await conn.execute(text(f"ALTER TABLE listings ADD COLUMN {col} VARCHAR(128)"))
                    except Exception:
                        pass
                try:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN photo_url VARCHAR(512)"))
                except Exception:
                    pass
            logger.info("Local SQLite database 'uyda.db' initialized successfully.")
        else:
            raise

