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


@pytest.mark.asyncio
async def test_deduplication_by_source_id_across_language_urls(
    test_session: AsyncSession, listing_service_test: ListingService
):
    """
    OLX listings accessed in Russian vs Uzbek Latin URLs share identical source_id.
    Ingestion must identify them as the identical apartment and never create a duplicate.
    """
    # Russian OLX URL
    item_ru = RawListingItem(
        source="olx_uz",
        source_id="66584170",
        canonical_url="https://www.olx.uz/d/obyavlenie/arenda-kvartira-2-2-4-ttz-2-remont-horosho-500-ID4wnAe.html",
        title="Аренда квартира 2/2/4 ТТЗ-2 ремонт хорошо 500",
        price_raw="500 y.e.",
        price_uzs=6400000,
        district="Mirzo Ulug‘bek",
        rooms=2,
    )

    listing1, is_new1 = await listing_service_test.ingest_raw_listing(test_session, item_ru)
    assert is_new1 is True
    assert listing1.source_id == "66584170"

    # Uzbek Latin OLX URL with different slug transliteration
    item_uz = RawListingItem(
        source="olx_uz",
        source_id="66584170",
        canonical_url="https://www.olx.uz/d/oz/obyavlenie/arenda-kvartira-2-2-4-ttz-2-remont-xorosho-500-ID4wnAe.html",
        title="Arenda kvartira 2/2/4 TTZ-2 remont yaxshi 500",
        price_raw="500 y.e.",
        price_uzs=6400000,
        district="Mirzo Ulug‘bek",
        rooms=2,
    )

    listing2, is_new2 = await listing_service_test.ingest_raw_listing(test_session, item_uz)
    assert is_new2 is False
    assert listing2.id == listing1.id

    # Verify database still only contains 1 listing
    stmt = select(func.count(Listing.id)).where(Listing.source_id == "66584170")
    count = (await test_session.execute(stmt)).scalar_one()
    assert count == 1

