"""Comprehensive test suite for JOYLIY.UZ Backend & Parser Rebuild.
Verifies:
1. 3x daily Tashkent schedule slot calculation (08:00, 14:00, 20:00).
2. Multi-tier duplicate prevention and data normalization.
3. Update history tracking (ListingUpdateHistory & ListingPriceHistory).
4. Full server-side pagination exceeding 100 items without truncation.
5. Telegram channel immediate broadcast with dual price and Joyliy.uz links.
6. Admin parser dashboard endpoints (status, manual run, pause/resume, logs).
7. Redis distributed locking and caching with graceful fallback.
"""

import math
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, func

from src.config import settings
from src.database import Base
from src.models.listing import Listing, ListingUpdateHistory
from src.models.ecosystem import ListingPriceHistory
from src.models.user import User
from src.providers.base import RawListingItem
from src.services.listing_service import listing_service
from src.services.monitor_worker import MonitorWorker
from src.services.notification_service import NotificationService
from src.services.redis_service import redis_service
from src.bot.formatter import format_channel_message, get_channel_inline_keyboard, TASHKENT_TZ


@pytest.mark.asyncio
async def test_schedule_slots_tashkent_timezone():
    """Verify 3x daily schedule slots (08:00, 14:00, 20:00) in Asia/Tashkent timezone."""
    worker = MonitorWorker()
    assert worker.scheduled_times == ["08:00", "14:00", "20:00"]

    # Verify custom schedule setting
    assert worker.set_schedule_times(["09:00", "15:00", "21:00"]) is True
    assert worker.scheduled_times == ["09:00", "15:00", "21:00"]

    # Revert to standard
    worker.set_schedule_times(["08:00", "14:00", "20:00"])
    assert worker.scheduled_times == ["08:00", "14:00", "20:00"]

    # Verify next scheduled run returns a valid string
    next_run = worker.get_next_scheduled_run()
    assert next_run is not None
    assert "Toshkent" in next_run


@pytest.mark.asyncio
async def test_multi_tier_deduplication_and_ingestion(test_session):
    """Verify newly discovered listings are ingested and subsequent identical items are detected as duplicates."""
    raw1 = RawListingItem(
        source="olx_uz",
        source_id="11223344",
        canonical_url="https://www.olx.uz/d/obyavlenie/chilonzor-2-xona-11223344.html",
        title="Chilonzor 9-mavze 2 xonali toza kvartira maklersiz",
        price_raw="4 500 000 so'm",
        price_uzs=4500000,
        currency="UZS",
        district="Chilonzor",
        rooms=2,
        area=56.0,
        floor="3/9",
        description="Egasidan toza kvartira, hamma sharoiti bor.",
        image_urls=["https://img.olx.uz/1.jpg"],
    )

    listing1, is_new1 = await listing_service.ingest_raw_listing(test_session, raw1)
    assert is_new1 is True
    assert listing1.id is not None
    assert listing1.district == "Chilonzor"

    # Second ingest of exact same item -> duplicate detected, is_new is False
    listing2, is_new2 = await listing_service.ingest_raw_listing(test_session, raw1)
    assert is_new2 is False
    assert listing2.id == listing1.id

    # Verify database has exactly 1 listing
    count = (await test_session.execute(select(func.count(Listing.id)))).scalar()
    assert count == 1


@pytest.mark.asyncio
async def test_update_history_tracking(test_session):
    """Verify price changes and photo updates on existing listings are tracked in ListingUpdateHistory."""
    raw_initial = RawListingItem(
        source="olx_uz",
        source_id="55667788",
        canonical_url="https://www.olx.uz/d/obyavlenie/yunusobod-3-xona-55667788.html",
        title="Yunusobod 4-mavze 3 xonali kvartira",
        price_raw="6 000 000 so'm",
        price_uzs=6000000,
        currency="UZS",
        district="Yunusobod",
        rooms=3,
        area=75.0,
        description="Yaxshi holatda",
        image_urls=[],
    )
    listing, is_new = await listing_service.ingest_raw_listing(test_session, raw_initial)
    assert is_new is True

    # Same listing discovers a price drop and new photos
    raw_updated = RawListingItem(
        source="olx_uz",
        source_id="55667788",
        canonical_url="https://www.olx.uz/d/obyavlenie/yunusobod-3-xona-55667788.html",
        title="Yunusobod 4-mavze 3 xonali kvartira",
        price_raw="5 500 000 so'm",
        price_uzs=5500000,
        currency="UZS",
        district="Yunusobod",
        rooms=3,
        area=75.0,
        description="Yaxshi holatda, narxi tushirildi!",
        image_urls=["https://img.olx.uz/new_photo.jpg"],
    )
    listing_up, is_new_up = await listing_service.ingest_raw_listing(test_session, raw_updated)
    assert is_new_up is False
    assert listing_up.price_uzs == 5500000
    assert len(listing_up.image_urls) == 1

    # Verify ListingUpdateHistory records
    hist_records = (await test_session.execute(
        select(ListingUpdateHistory).where(ListingUpdateHistory.listing_id == listing.id)
    )).scalars().all()
    assert len(hist_records) >= 1
    types = [h.change_type for h in hist_records]
    assert "price_change" in types or "photo_update" in types

    # Verify ListingPriceHistory records
    price_hist = (await test_session.execute(
        select(ListingPriceHistory).where(ListingPriceHistory.listing_id == listing.id)
    )).scalars().all()
    assert len(price_hist) >= 1
    assert price_hist[0].old_price_uzs == 6000000
    assert price_hist[0].new_price_uzs == 5500000


@pytest.mark.asyncio
async def test_pagination_exceeding_100_listings(test_session):
    """Verify server-side pagination works for over 100 listings without truncation or artificial cap."""
    # Seed 125 mock listings
    listings_to_add = []
    for i in range(1, 126):
        listings_to_add.append(
            Listing(
                source="olx_uz",
                source_id=f"bulk_{i}",
                canonical_url=f"https://www.olx.uz/d/obyavlenie/listing-{i}.html",
                title=f"Toshkent xonadon #{i}",
                price_uzs=3000000 + (i * 10000),
                currency="UZS",
                district="Chilonzor" if i % 2 == 0 else "Yunusobod",
                rooms=(i % 4) + 1,
                area=40.0 + (i * 0.5),
                is_active=True,
                first_seen_at=datetime.now(timezone.utc),
                last_seen_at=datetime.now(timezone.utc),
            )
        )
    test_session.add_all(listings_to_add)
    await test_session.commit()

    # Query page 1 (limit=24)
    items_p1, total = await listing_service.search_listings(test_session, limit=24, offset=0)
    assert total == 125
    assert len(items_p1) == 24

    # Query page 5 (limit=24, offset=96)
    items_p5, _ = await listing_service.search_listings(test_session, limit=24, offset=96)
    assert len(items_p5) == 24

    # Query page 6 (limit=24, offset=120) -> should have remaining 5 items
    items_p6, _ = await listing_service.search_listings(test_session, limit=24, offset=120)
    assert len(items_p6) == 5

    # Test sorting
    items_cheap, _ = await listing_service.search_listings(test_session, sort="lo", limit=10, offset=0)
    assert items_cheap[0].price_uzs <= items_cheap[1].price_uzs

    items_expensive, _ = await listing_service.search_listings(test_session, sort="hi", limit=10, offset=0)
    assert items_expensive[0].price_uzs >= items_expensive[1].price_uzs


@pytest.mark.asyncio
async def test_telegram_channel_formatter_and_links(test_session):
    """Verify Telegram channel publication template contains Title, UZS + USD price, district, specs, and Joyliy link."""
    listing = Listing(
        source="olx_uz",
        source_id="test_tg_1",
        canonical_url="https://www.olx.uz/d/obyavlenie/tg-test-listing.html",
        title="Shinam 2 xonali kvartira Chilonzorda",
        price_uzs=5120000,
        currency="UZS",
        district="Chilonzor",
        rooms=2,
        area=62.0,
        floor="4/9",
        description="Evro-remont, barcha jihozlari mavjud.",
        contact_phone="+998901234567",
        contact_telegram="@uy_egasi",
        is_active=True,
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    msg = format_channel_message(listing)
    assert "Shinam 2 xonali kvartira Chilonzorda" in msg
    assert "5 120 000" in msg
    assert "$" in msg  # USD conversion
    assert "Chilonzor" in msg
    assert "2 xona" in msg
    assert "62 m²" in msg
    assert "Joyliy.uz" in msg
    assert f"?listing={listing.id}" in msg

    kb = get_channel_inline_keyboard(listing)
    all_buttons = [btn for row in kb.inline_keyboard for btn in row]
    urls = [b.url for b in all_buttons]
    assert any("joyliy" in u.lower() or f"?listing={listing.id}" in u for u in urls if u)


@pytest.mark.asyncio
async def test_admin_parser_api_routes(test_session):
    """Verify admin parser dashboard, pause, resume, manual run, and log endpoints via ASGI."""
    from src.api.app import create_app
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. GET Dashboard
        resp = await client.get("/api/admin/parser/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "provider" in data
        assert "scheduled_times" in data
        assert "is_running" in data
        assert "server_tashkent_time" in data

        # 2. POST Pause
        p_resp = await client.post("/api/admin/parser/pause")
        assert p_resp.status_code == 200
        assert p_resp.json()["is_paused"] is True

        # 3. POST Resume
        r_resp = await client.post("/api/admin/parser/resume")
        assert r_resp.status_code == 200
        assert r_resp.json()["is_paused"] is False

        # 4. GET Logs
        l_resp = await client.get("/api/admin/parser/logs")
        assert l_resp.status_code == 200
        assert "logs" in l_resp.json()
        assert isinstance(l_resp.json()["logs"], list)

        # 5. GET Paginated Listings with page and limit
        list_resp = await client.get("/api/listings?page=1&limit=10")
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert "items" in list_data
        assert "total" in list_data
        assert "page" in list_data
        assert "total_pages" in list_data
        assert "has_next" in list_data
        assert "has_previous" in list_data


@pytest.mark.asyncio
async def test_redis_service_locking_and_cache():
    """Verify Redis distributed lock context manager and caching work with in-memory fallback."""
    # Distributed lock test
    async with redis_service.lock("unit_test_lock", timeout=10) as acquired:
        assert acquired is True

    # Caching test
    await redis_service.set_cached("test_key", {"status": "ok", "count": 42}, ttl_seconds=60)
    cached = await redis_service.get_cached("test_key")
    assert cached == {"status": "ok", "count": 42}

    # Clear cache
    await redis_service.clear_cache("test_*")
    cleared = await redis_service.get_cached("test_key")
    assert cleared is None


@pytest.mark.asyncio
async def test_channel_backfills_older_listings_when_no_new_found(test_session, mock_bot):
    """
    Verify requirement: 'e'lon topilmasa o'rnini yopish uchun eski e'lonlar kanalga push qilinsin'.
    When 0 new listings are discovered, existing listings from DB are pushed to the channel.
    """
    from src.services.notification_service import NotificationService
    service = NotificationService(bot=mock_bot)

    # Seed 1 existing active listing in the DB (already past seen)
    listing = Listing(
        source="olx_uz",
        source_id="backfill_test_1",
        canonical_url="https://www.olx.uz/d/obyavlenie/backfill-listing-1.html",
        title="Yunusobod 11-mavze 2 xonali kvartira",
        price_uzs=4000000,
        currency="UZS",
        district="Yunusobod",
        rooms=2,
        area=52.0,
        is_active=True,
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
        posted_to_channel_at=None,
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    # When new_listings is empty (0 new listings discovered)
    posted = await service.broadcast_channel_batch(
        test_session,
        new_listings=[],
        allow_backfill=True,
    )
    assert posted >= 1
    # Verify listing was marked posted
    await test_session.refresh(listing)
    assert listing.posted_to_channel_at is not None


@pytest.mark.asyncio
async def test_never_upload_duplicate_to_website(test_session):
    """
    Verify requirement: 'saytga bitta e'lon ikki marta hech qachon qayta yuklanmasin'.
    Ensures that various cross-format duplicates (mobile vs desktop URLs, language prefixes,
    matching source_ids or content hashes) never create a second row in the database.
    """
    # 1. Desktop URL format
    raw1 = RawListingItem(
        source="olx_uz",
        source_id="99887766",
        canonical_url="https://www.olx.uz/d/obyavlenie/shinam-kvartira-99887766.html",
        title="Chilonzor 1-mavze shinam kvartira",
        price_raw="3 500 000 so'm",
        price_uzs=3500000,
        currency="UZS",
        district="Chilonzor",
        rooms=1,
        area=38.0,
        description="Egasidan shinamgina kvartira",
    )
    l1, is_new1 = await listing_service.ingest_raw_listing(test_session, raw1)
    assert is_new1 is True

    # 2. Mobile Uzbek URL format with /oz/ prefix for exact same ad
    raw2 = RawListingItem(
        source="olx_uz",
        source_id=None,  # missing explicit source_id, must be extracted from URL
        canonical_url="https://m.olx.uz/d/oz/obyavlenie/shinam-kvartira-99887766.html?reason=observed_search",
        title="Chilonzor 1-mavze shinam kvartira",
        price_raw="3 500 000 so'm",
        price_uzs=3500000,
        currency="UZS",
        district="Chilonzor",
        rooms=1,
        area=38.0,
        description="Egasidan shinamgina kvartira",
    )
    l2, is_new2 = await listing_service.ingest_raw_listing(test_session, raw2)
    assert is_new2 is False
    assert l2.id == l1.id

    # 3. Third variant: different URL slug, but same source_id
    raw3 = RawListingItem(
        source="olx_uz",
        source_id="99887766",
        canonical_url="https://www.olx.uz/d/obyavlenie/arzon-kvartira-99887766.html",
        title="Chilonzor 1-mavze shinam kvartira",
        price_raw="3 500 000 so'm",
        price_uzs=3500000,
        currency="UZS",
        district="Chilonzor",
        rooms=1,
        area=38.0,
    )
    l3, is_new3 = await listing_service.ingest_raw_listing(test_session, raw3)
    assert is_new3 is False
    assert l3.id == l1.id

    # Total rows in DB must remain strictly 1
    total = (await test_session.execute(select(func.count(Listing.id)))).scalar()
    assert total == 1
