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
