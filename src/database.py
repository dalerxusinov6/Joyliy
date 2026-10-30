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

__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "AsyncSession",
    "get_db_session",
    "init_db",
    "create_engine_and_session",
    "get_session_factory",
]

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


def _sync_schema_migration(connection) -> None:
    """Synchronously verify and migrate missing columns across both PostgreSQL and SQLite."""
    from sqlalchemy import inspect, text

    insp = inspect(connection)
    tables = set(insp.get_table_names())

    if "listings" in tables:
        cols = {c["name"] for c in insp.get_columns("listings")}
        for col, ctype in [
            ("contact_phone", "VARCHAR(128)"),
            ("contact_telegram", "VARCHAR(128)"),
            ("content_hash", "VARCHAR(64)"),
            ("image_fingerprint", "VARCHAR(64)"),
            ("target_audience", "VARCHAR(32) DEFAULT 'any'"),
            ("posted_to_channel_at", "TIMESTAMP"),
            ("coordinates_lat", "FLOAT"),
            ("coordinates_lon", "FLOAT"),
            ("metro_station", "VARCHAR(128)"),
            ("metro_distance_m", "INTEGER"),
            ("is_furnished", "BOOLEAN DEFAULT TRUE"),
            ("renovation_type", "VARCHAR(64)"),
            ("fair_price_category", "VARCHAR(32) DEFAULT 'fair_price'"),
            ("estimated_market_price", "BIGINT"),
            ("price_diff_percent", "FLOAT"),
            ("scam_risk_score", "INTEGER DEFAULT 10"),
            ("scam_risk_level", "VARCHAR(32) DEFAULT 'low'"),
            ("scam_risk_reasons", "TEXT DEFAULT '[]'"),
        ]:
            if col not in cols:
                try:
                    connection.execute(text(f"ALTER TABLE listings ADD COLUMN {col} {ctype}"))
                except Exception as e:
                    logger.debug("Could not add column %s to listings: %s", col, e)

    if "users" in tables:
        cols = {c["name"] for c in insp.get_columns("users")}
        if "photo_url" not in cols:
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN photo_url VARCHAR(512)"))
            except Exception as e:
                logger.debug("Could not add column photo_url to users: %s", e)

    if "channel_posts" in tables:
        cols = {c["name"] for c in insp.get_columns("channel_posts")}
        for col, ctype in [
            ("content_hash", "VARCHAR(64)"),
            ("image_fingerprint", "VARCHAR(64)"),
            ("telegram_message_id", "BIGINT"),
        ]:
            if col not in cols:
                try:
                    connection.execute(text(f"ALTER TABLE channel_posts ADD COLUMN {col} {ctype}"))
                except Exception as e:
                    logger.debug("Could not add column %s to channel_posts: %s", col, e)


async def init_db() -> None:
    """Initialize database tables, with seamless local SQLite fallback if PostgreSQL is unreachable."""
    global engine, _engine, _session_maker
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(_sync_schema_migration)
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
                await conn.run_sync(_sync_schema_migration)
            logger.info("Local SQLite database 'uyda.db' initialized successfully.")
        else:
            raise

    # Seed initial authentic listings if database is newly initialized
    await seed_initial_listings_if_empty()


async def seed_initial_listings_if_empty() -> None:
    """Pre-populate database with authentic OLX listings on first run (especially in cloud containers)."""
    import json
    import os
    from sqlalchemy import select, func
    from src.models.listing import Listing, ListingClassification

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(base_dir, "src", "data", "initial_listings.json")
    if not os.path.exists(seed_file):
        return

    try:
        async with AsyncSessionLocal() as session:
            count = (await session.execute(select(func.count(Listing.id)))).scalar() or 0
            if count > 0:
                return

            logger.info("Database is empty. Seeding initial OLX listings from %s...", seed_file)
            with open(seed_file, "r", encoding="utf-8") as f:
                items = json.load(f)

            for row in items:
                img_urls = (
                    json.loads(row["image_urls"])
                    if isinstance(row.get("image_urls"), str)
                    else (row.get("image_urls") or [])
                )
                from src.classification.audience import detect_target_audience
                aud = row.get("target_audience") or detect_target_audience(row.get("title", ""), row.get("description"))

                listing = Listing(
                    source=row.get("source", "olx_uz"),
                    source_id=str(row.get("source_id")),
                    canonical_url=row.get("canonical_url"),
                    title=row.get("title", ""),
                    price_raw=row.get("price_raw"),
                    price_uzs=row.get("price_uzs"),
                    currency=row.get("currency", "UZS"),
                    district=row.get("district"),
                    rooms=row.get("rooms"),
                    area=row.get("area"),
                    floor=row.get("floor"),
                    description=row.get("description"),
                    contact_phone=row.get("contact_phone"),
                    contact_telegram=row.get("contact_telegram"),
                    target_audience=aud,
                    image_urls=img_urls,
                    is_active=True,
                )
                session.add(listing)
                await session.flush()

                cls = ListingClassification(
                    listing_id=listing.id,
                    label=row.get("cls_label") or "NEEDS_REVIEW",
                    confidence_score=row.get("cls_score") or 0.5,
                    reasons=[],
                )
                session.add(cls)

            await session.commit()
            logger.info("Successfully seeded %d initial OLX listings into database.", len(items))
    except Exception as e:
        logger.warning("Could not seed initial listings: %s", e)

