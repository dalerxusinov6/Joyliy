"""Initial schema migration.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-28 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("first_name", sa.String(length=256), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("language_code", sa.String(length=10), server_default="uz", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    # 2. user_search_preferences
    op.create_table(
        "user_search_preferences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("districts", sa.JSON(), nullable=False),
        sa.Column("min_price", sa.BigInteger(), nullable=True),
        sa.Column("max_price", sa.BigInteger(), nullable=True),
        sa.Column("rooms", sa.JSON(), nullable=False),
        sa.Column("min_area", sa.Float(), nullable=True),
        sa.Column("max_area", sa.Float(), nullable=True),
        sa.Column("owner_only", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("include_agency", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("max_listing_age_hours", sa.Integer(), nullable=True),
        sa.Column("notifications_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("quiet_hours_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("quiet_hours_start", sa.String(length=5), server_default="23:00", nullable=False),
        sa.Column("quiet_hours_end", sa.String(length=5), server_default="08:00", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_search_preferences_user_id"), "user_search_preferences", ["user_id"], unique=True)

    # 3. listings
    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=64), server_default="olx_uz", nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("canonical_url", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("price_raw", sa.String(length=128), nullable=True),
        sa.Column("price_uzs", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(length=16), server_default="UZS", nullable=False),
        sa.Column("district", sa.String(length=128), nullable=True),
        sa.Column("rooms", sa.Integer(), nullable=True),
        sa.Column("area", sa.Float(), nullable=True),
        sa.Column("floor", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_urls", sa.JSON(), nullable=False),
        sa.Column("publication_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listings_canonical_url"), "listings", ["canonical_url"], unique=True)
    op.create_index(op.f("ix_listings_district"), "listings", ["district"], unique=False)
    op.create_index(op.f("ix_listings_rooms"), "listings", ["rooms"], unique=False)
    op.create_index(op.f("ix_listings_price_uzs"), "listings", ["price_uzs"], unique=False)
    op.create_index(op.f("ix_listings_first_seen_at"), "listings", ["first_seen_at"], unique=False)
    op.create_index(op.f("ix_listings_source"), "listings", ["source"], unique=False)
    op.create_index(op.f("ix_listings_source_id"), "listings", ["source_id"], unique=False)
    op.create_index("idx_listings_district_price", "listings", ["district", "price_uzs"])
    op.create_index("idx_listings_rooms_price", "listings", ["rooms", "price_uzs"])

    # 4. listing_classifications
    op.create_table(
        "listing_classifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=32), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_classifications_listing_id"), "listing_classifications", ["listing_id"], unique=True)
    op.create_index(op.f("ix_listing_classifications_label"), "listing_classifications", ["label"], unique=False)

    # 5. favorites
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_user_favorite_listing"),
    )
    op.create_index(op.f("ix_favorites_listing_id"), "favorites", ["listing_id"], unique=False)
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)

    # 6. notification_history
    op.create_table(
        "notification_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="delivered", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_user_listing_notification"),
    )
    op.create_index(op.f("ix_notification_history_listing_id"), "notification_history", ["listing_id"], unique=False)
    op.create_index(op.f("ix_notification_history_user_id"), "notification_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_notification_history_sent_at"), "notification_history", ["sent_at"], unique=False)

    # 7. source_monitor_runs
    op.create_table(
        "source_monitor_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_name", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("listings_found", sa.Integer(), server_default="0", nullable=False),
        sa.Column("listings_new", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_monitor_runs_source_name"), "source_monitor_runs", ["source_name"], unique=False)
    op.create_index(op.f("ix_source_monitor_runs_status"), "source_monitor_runs", ["status"], unique=False)

    # 8. admin_audit_logs
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_audit_logs_admin_id"), "admin_audit_logs", ["admin_id"], unique=False)


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("source_monitor_runs")
    op.drop_table("notification_history")
    op.drop_table("favorites")
    op.drop_table("listing_classifications")
    op.drop_table("listings")
    op.drop_table("user_search_preferences")
    op.drop_table("users")

