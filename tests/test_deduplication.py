"""Tests for listing deduplication and idempotent persistence."""

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.listing_service import ListingService
from src.providers.base import RawListingItem
from src.models.listing import Listing, ListingClassification


@pytest.mark.asyncio
async def test_deduplication_by_canonical_url(
    test_session: AsyncSession, listing_service_test: ListingService
):
    """
    Ingesting identical canonical URLs must update existing records
    rather than creating duplicates.
    """
    item1 = RawListingItem(
        source="olx_uz",
        source_id="55501",
        canonical_url="https://www.olx.uz/d/oz/obyavlenie/chilonzor-test-ID55501.html",
        title="Chilonzor 2 xonali kvartira egasidan",
        price_raw="3 500 000 so'm",
        price_uzs=3500000,
        district="Chilonzor",
        rooms=2,
    )

    # First ingestion -> New
    listing1, is_new1 = await listing_service_test.ingest_raw_listing(test_session, item1)
    assert is_new1 is True
    assert listing1.id is not None
    first_seen_initial = listing1.first_seen_at

    # Count total listings
    count1 = (await test_session.execute(select(func.count(Listing.id)))).scalar_one()
    assert count1 == 1

    # Second ingestion of the same canonical URL (with perhaps modified price)
    item2 = RawListingItem(
        source="olx_uz",
        source_id="55501",
        canonical_url="https://www.olx.uz/d/oz/obyavlenie/chilonzor-test-ID55501.html",
        title="Chilonzor 2 xonali kvartira egasidan",
        price_raw="3 600 000 so'm",
        price_uzs=3600000,
        district="Chilonzor",
        rooms=2,
    )

    listing2, is_new2 = await listing_service_test.ingest_raw_listing(test_session, item2)
    assert is_new2 is False
    assert listing2.id == listing1.id
    assert listing2.price_uzs == 3600000
    assert listing2.first_seen_at == first_seen_initial

    # Ensure still exactly 1 row in DB
    count2 = (await test_session.execute(select(func.count(Listing.id)))).scalar_one()
    assert count2 == 1

