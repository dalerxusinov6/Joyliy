"""Ecosystem Models: Price History, Roommate Profiles, Connection Requests, Reports, and Saved Searches."""

from datetime import datetime, timezone
from typing import Optional, List
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
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ListingPriceHistory(Base):
    """Tracks historical price fluctuations for an apartment listing."""

    __tablename__ = "listing_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    old_price_uzs: Mapped[int] = mapped_column(BigInteger, nullable=False)
    new_price_uzs: Mapped[int] = mapped_column(BigInteger, nullable=False)
    diff_uzs: Mapped[int] = mapped_column(BigInteger, nullable=False)
    diff_percent: Mapped[float] = mapped_column(Float, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    listing = relationship("Listing", backref="price_history")

    def __repr__(self) -> str:
        return f"<ListingPriceHistory listing_id={self.listing_id} {self.old_price_uzs}->{self.new_price_uzs}>"


class RoommateProfile(Base):
    """Roommate search profile for shared apartment living in Tashkent."""

    __tablename__ = "roommate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(32), default="any", index=True, nullable=False)  # male, female, any
    budget_uzs: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    preferred_districts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # e.g. ["Chilonzor", "Yunusobod"]
    occupation: Mapped[str] = mapped_column(String(64), default="student", index=True, nullable=False)  # student, professional, freelancer
    lifestyle_cleanliness: Mapped[str] = mapped_column(String(32), default="clean", nullable=False)
    lifestyle_sleep: Mapped[str] = mapped_column(String(32), default="flexible", nullable=False)
    smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    move_in_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    contact_telegram: Mapped[str] = mapped_column(String(128), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    requests = relationship("RoommateConnectionRequest", back_populates="roommate", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RoommateProfile id={self.id} name={self.name} budget={self.budget_uzs}>"


class RoommateConnectionRequest(Base):
    """In-platform connection request between users seeking roommates."""

    __tablename__ = "roommate_connection_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roommate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roommate_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    from_name: Mapped[str] = mapped_column(String(128), nullable=False)
    from_contact: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, accepted, declined
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    roommate = relationship("RoommateProfile", back_populates="requests")

    def __repr__(self) -> str:
        return f"<RoommateConnectionRequest id={self.id} roommate_id={self.roommate_id} status={self.status}>"


class ListingReport(Base):
    """User complaints and fraud alerts for suspicious listings."""

    __tablename__ = "listing_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    reason: Mapped[str] = mapped_column(String(128), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)  # pending, reviewed, dismissed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    listing = relationship("Listing")

    def __repr__(self) -> str:
        return f"<ListingReport id={self.id} listing_id={self.listing_id} reason={self.reason}>"


class SavedSearchAlert(Base):
    """Persistent user alert criteria for new listings and price drops."""

    __tablename__ = "saved_search_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    query_text: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    min_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    owner_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_telegram: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_price_drop: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<SavedSearchAlert id={self.id} title={self.title!r} user_id={self.user_id}>"

