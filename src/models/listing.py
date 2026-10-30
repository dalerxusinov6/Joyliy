"""Listing, Classification, Favorite, and NotificationHistory ORM Models."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Listing(Base):
    """Normalized apartment rental listing."""

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), default="olx_uz", index=True, nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    canonical_url: Mapped[str] = mapped_column(
        String(1024), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    price_raw: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    price_uzs: Mapped[Optional[int]] = mapped_column(BigInteger, index=True, nullable=True)
    currency: Mapped[str] = mapped_column(String(16), default="UZS", nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
    area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    contact_telegram: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    target_audience: Mapped[str] = mapped_column(
        String(32), default="any", index=True, nullable=False
    )  # 'family', 'female', 'male', 'any'
    image_urls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    image_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # Location & Metro Intelligence
    coordinates_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coordinates_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metro_station: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    metro_distance_m: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Property Characteristics
    is_furnished: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    renovation_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # euro, good, cosmetic, standard

    # Fair Price AI Intelligence
    fair_price_category: Mapped[Optional[str]] = mapped_column(
        String(32), default="fair_price", index=True, nullable=True
    )  # 'below_market', 'fair_price', 'above_market'
    estimated_market_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    price_diff_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Scam Detector & Risk Indicators
    scam_risk_score: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 0 to 100
    scam_risk_level: Mapped[str] = mapped_column(
        String(32), default="low", index=True, nullable=False
    )  # 'low', 'medium', 'high'
    scam_risk_reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Dates: publication_date is recorded only when reliably present; never fabricated
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    posted_to_channel_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Relationships
    classification: Mapped[Optional["ListingClassification"]] = relationship(
        "ListingClassification",
        back_populates="listing",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    favorites = relationship("Favorite", back_populates="listing", cascade="all, delete-orphan")
    notifications = relationship(
        "NotificationHistory", back_populates="listing", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_listings_district_price", "district", "price_uzs"),
        Index("idx_listings_rooms_price", "rooms", "price_uzs"),
    )

    def __repr__(self) -> str:
        return f"<Listing id={self.id} title={self.title[:30]!r} price_uzs={self.price_uzs}>"


class ListingClassification(Base):
    """Maklersiz / Owner vs Agent Classification results."""

    __tablename__ = "listing_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("listings.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    label: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False
    )  # LIKELY_OWNER, NEEDS_REVIEW, LIKELY_AGENT
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    listing: Mapped["Listing"] = relationship("Listing", back_populates="classification")

    def __repr__(self) -> str:
        return f"<ListingClassification listing_id={self.listing_id} label={self.label} score={self.confidence_score}>"


class Favorite(Base):
    """User bookmarked listings."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="favorites")
    listing = relationship("Listing", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_favorite_listing"),
    )


class NotificationHistory(Base):
    """Tracks notifications sent to users to prevent repeated delivery."""

    __tablename__ = "notification_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default="delivered", nullable=False
    )  # delivered, failed, skipped
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
    listing = relationship("Listing", back_populates="notifications")

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing_notification"),
    )


class ChannelPostHistory(Base):
    """Tracks all listings broadcast to Telegram channel to strictly prevent duplicates."""

    __tablename__ = "channel_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    canonical_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    district: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_uzs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    image_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    channel_id: Mapped[str] = mapped_column(String(128), default="@joyliy_uz", nullable=False)


class QueueStatus:
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"


class ChannelPublishQueue(Base):
    """
    Persistent queue for Telegram channel publishing.
    Enforces strict deduplication and state machine:
    pending -> publishing -> published | failed | rejected
    """

    __tablename__ = "channel_publish_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    canonical_url: Mapped[str] = mapped_column(String(1024), unique=True, index=True, nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_uzs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    image_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # State tracking: pending, publishing, published, failed, rejected
    status: Mapped[str] = mapped_column(String(32), default=QueueStatus.PENDING, index=True, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Delivery info
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    scheduled_slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )

    # Relationships
    listing: Mapped["Listing"] = relationship("Listing")

    __table_args__ = (
        Index("idx_queue_status_pubdate", "status", "publication_date"),
        Index("idx_queue_content_hash", "content_hash"),
    )

    def __repr__(self) -> str:
        return f"<ChannelPublishQueue id={self.id} listing_id={self.listing_id} status={self.status}>"


class ChannelPublishSchedule(Base):
    """
    Persistent log of executed 10 daily publication slots (Asia/Tashkent).
    Guarantees idempotency across restarts and eliminates burst postings.
    """

    __tablename__ = "channel_publish_schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slot_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # e.g. "2026-10-30"
    slot_time: Mapped[str] = mapped_column(String(5), index=True, nullable=False)  # e.g. "08:00"
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, published, skipped, missed
    queue_item_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("slot_date", "slot_time", name="uq_channel_slot_date_time"),
    )

    def __repr__(self) -> str:
        return f"<ChannelPublishSchedule {self.slot_date} {self.slot_time} status={self.status}>"
