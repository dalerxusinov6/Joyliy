"""User and Search Preferences ORM Models."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Telegram User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), default="uz", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    preference: Mapped[Optional["UserSearchPreference"]] = relationship(
        "UserSearchPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("NotificationHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} username={self.username}>"


class UserSearchPreference(Base):
    """User apartment search filters and notification configuration."""

    __tablename__ = "user_search_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # Filter preferences
    districts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    min_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    rooms: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # e.g. [1, 2]
    min_area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    owner_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    include_agency: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_listing_age_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Notification preferences
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quiet_hours_start: Mapped[str] = mapped_column(String(5), default="23:00", nullable=False)
    quiet_hours_end: Mapped[str] = mapped_column(String(5), default="08:00", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preference")

    def __repr__(self) -> str:
        return f"<UserSearchPreference user_id={self.user_id} owner_only={self.owner_only}>"


class AuthSession(Base):
    """Temporary session for Telegram Bot Deep-Link web authentication."""

    __tablename__ = "auth_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(
        String(32), default="PENDING", index=True, nullable=False
    )  # PENDING, AUTHENTICATED, EXPIRED
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    def is_expired(self) -> bool:
        exp = self.expires_at
        if exp is not None and exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > exp

    def __repr__(self) -> str:
        return f"<AuthSession session_id={self.session_id} status={self.status}>"


