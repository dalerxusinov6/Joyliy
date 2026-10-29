"""System Models: Source Monitor Runs and Admin Audit Logs."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SourceMonitorRun(Base):
    """Tracks background monitoring polling cycles, health, and yields."""

    __tablename__ = "source_monitor_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False
    )  # SUCCESS, ERROR, DEGRADED, BLOCKED
    listings_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    listings_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<SourceMonitorRun id={self.id} status={self.status} new={self.listings_new}>"


class AdminAuditLog(Base):
    """Tracks administrative operations performed via Telegram or API."""

    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:
        return f"<AdminAuditLog id={self.id} admin_id={self.admin_id} action={self.action}>"

