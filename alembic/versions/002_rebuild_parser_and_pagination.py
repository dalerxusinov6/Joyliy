"""Rebuild parser, add listing_update_history and pagination indexes.

Revision ID: 002_rebuild_parser_and_pagination
Revises: 001_initial_schema
Create Date: 2026-11-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_rebuild_parser_and_pagination"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create listing_update_history table
    op.create_table(
        "listing_update_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=64), nullable=False),
        sa.Column("old_values", sa.JSON(), nullable=False),
        sa.Column("new_values", sa.JSON(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_update_history_listing_id"), "listing_update_history", ["listing_id"], unique=False)
    op.create_index(op.f("ix_listing_update_history_change_type"), "listing_update_history", ["change_type"], unique=False)
    op.create_index(op.f("ix_listing_update_history_detected_at"), "listing_update_history", ["detected_at"], unique=False)

    # 2. Performance indexes on listings table
    try:
        op.create_index("idx_listings_active_pubdate", "listings", ["is_active", "publication_date"], unique=False)
    except Exception:
        pass
    try:
        op.create_index("idx_listings_active_district_price", "listings", ["is_active", "district", "price_uzs"], unique=False)
    except Exception:
        pass
    try:
        op.create_index("idx_listings_active_rooms_price", "listings", ["is_active", "rooms", "price_uzs"], unique=False)
    except Exception:
        pass
    try:
        op.create_index("idx_listings_posted_channel", "listings", ["posted_to_channel_at"], unique=False)
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_index("idx_listings_posted_channel", table_name="listings")
        op.drop_index("idx_listings_active_rooms_price", table_name="listings")
        op.drop_index("idx_listings_active_district_price", table_name="listings")
        op.drop_index("idx_listings_active_pubdate", table_name="listings")
    except Exception:
        pass
    op.drop_table("listing_update_history")

