"""Tests for notification engine, deduplication, quiet hours, and flood control."""

import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User, UserSearchPreference
from src.models.listing import Listing, ListingClassification, NotificationHistory
from src.classification.types import ClassificationLabel
from src.services.notification_service import (
    NotificationService,
    is_in_quiet_hours,
)


def test_quiet_hours():
    """Verify overnight quiet hours calculations."""
    pref = UserSearchPreference(
        user_id=1,
        districts=[],
        rooms=[],
        quiet_hours_enabled=True,
        quiet_hours_start="23:00",
        quiet_hours_end="08:00",
    )

    # 02:30 Tashkent time (UTC 21:30 previous day) -> Inside quiet hours
    dt_night = datetime(2026, 10, 28, 21, 30, tzinfo=timezone.utc)
    assert is_in_quiet_hours(pref, dt_night) is True

    # 15:00 Tashkent time (UTC 10:00) -> Daytime, outside quiet hours
    dt_day = datetime(2026, 10, 28, 10, 0, tzinfo=timezone.utc)
    assert is_in_quiet_hours(pref, dt_day) is False

    # Disabled quiet hours
    pref.quiet_hours_enabled = False
    assert is_in_quiet_hours(pref, dt_night) is False


@pytest.mark.asyncio
async def test_notification_deduplication(test_session: AsyncSession, mock_bot):
    """
    Ensure the same listing is never sent to the same user twice.
    """
    service = NotificationService(bot=mock_bot)

    # Create active user and preference
    user = User(telegram_id=1234567, is_active=True)
    test_session.add(user)
    await test_session.flush()

    pref = UserSearchPreference(
        user_id=user.id,
        districts=[],
        rooms=[],
        notifications_enabled=True,
        quiet_hours_enabled=False,
    )
    test_session.add(pref)

    listing = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/test-1",
        title="Chilonzor 2 xonali kvartira",
        price_uzs=3500000,
        district="Chilonzor",
        rooms=2,
        first_seen_at=datetime.now(timezone.utc),
        is_active=True,
    )
    test_session.add(listing)
    await test_session.flush()

    cls = ListingClassification(
        listing_id=listing.id,
        label=ClassificationLabel.LIKELY_OWNER.value,
        confidence_score=0.85,
    )
    test_session.add(cls)
    await test_session.commit()

    listing.classification = cls

    # First dispatch -> delivered (1 message sent)
    count1 = await service.dispatch_new_listing(test_session, listing)
    assert count1 == 1
    assert len(mock_bot.sent_messages) == 1

    # Second dispatch of the same listing -> skipped by deduplication (0 sent)
    count2 = await service.dispatch_new_listing(test_session, listing)
    assert count2 == 0
    assert len(mock_bot.sent_messages) == 1


@pytest.mark.asyncio
async def test_telegram_retry_after_handling(mock_bot):
    """
    Verify that Telegram flood control (RetryAfter) is caught, slept, and retried.
    """
    service = NotificationService(bot=mock_bot)
    mock_bot.force_retry_after = 1  # will trigger RetryAfter on first attempt, then succeed

    listing = Listing(
        id=1,
        canonical_url="https://olx.uz/test",
        title="Test apartment",
        price_uzs=3000000,
        district="Chilonzor",
        rooms=2,
    )

    success = await service.send_to_user_with_retry(
        telegram_id=987654,
        listing=listing,
        max_retries=3,
    )
    assert success is True
    assert len(mock_bot.sent_messages) == 1


@pytest.mark.asyncio
async def test_bot_blocked_by_user_deactivation(test_session: AsyncSession, mock_bot):
    """
    When TelegramForbiddenError occurs (user blocked bot), the user should be deactivated.
    """
    service = NotificationService(bot=mock_bot)
    mock_bot.force_forbidden = True

    user = User(telegram_id=999888, is_active=True)
    test_session.add(user)
    await test_session.flush()

    pref = UserSearchPreference(
        user_id=user.id,
        districts=[],
        rooms=[],
        notifications_enabled=True,
        quiet_hours_enabled=False,
    )
    test_session.add(pref)

    listing = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/test-forbidden",
        title="Apartment",
        first_seen_at=datetime.now(timezone.utc),
    )
    test_session.add(listing)
    await test_session.commit()

    await service.dispatch_new_listing(test_session, listing)

    # Verify user is deactivated
    updated_user = (await test_session.execute(
        select(User).where(User.telegram_id == 999888)
    )).scalar_one()
    assert updated_user.is_active is False


@pytest.mark.asyncio
async def test_channel_batch_broadcast_and_stats(test_session: AsyncSession, mock_bot):
    """
    Verify distributed batch channel posting, daily limits, and unposted queue management.
    """
    service = NotificationService(bot=mock_bot)

    # Insert 3 listings
    l1 = Listing(source="olx_uz", canonical_url="https://olx.uz/ch-1", title="Flat 1", is_active=True)
    l2 = Listing(source="olx_uz", canonical_url="https://olx.uz/ch-2", title="Flat 2", is_active=True)
    l3 = Listing(source="olx_uz", canonical_url="https://olx.uz/ch-3", title="Flat 3", is_active=True)
    test_session.add_all([l1, l2, l3])
    await test_session.commit()

    # Initial stats
    stats = await service.get_channel_posting_stats(test_session)
    assert stats["posted_today"] == 0
    assert stats["daily_limit"] == 100
    assert stats["remaining_today"] == 100
    assert stats["unposted_total"] >= 3

    # Post batch of 2
    posted = await service.broadcast_channel_batch(test_session, batch_limit=2, force=True)
    assert posted == 2

    # Verify updated stats
    stats_after = await service.get_channel_posting_stats(test_session)
    assert stats_after["posted_today"] == 2
    assert stats_after["remaining_today"] == 98


@pytest.mark.asyncio
async def test_channel_duplicate_detection(test_session: AsyncSession, mock_bot):
    """
    Ensure identical titles, phone numbers, and URLs are never posted twice.
    """
    service = NotificationService(bot=mock_bot)

    # 1. First listing posted
    l1 = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-original",
        title="Chilonzor 9-kvartal 2 xonali kvartira",
        district="Chilonzor",
        rooms=2,
        price_uzs=4000000,
        contact_phone="+998901234567",
        posted_to_channel_at=datetime.now(timezone.utc),
        is_active=True,
    )
    test_session.add(l1)
    await test_session.commit()

    # 2. Duplicate with exact same title in same district
    l2 = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-dup-title",
        title="Chilonzor 9-kvartal 2 xonali kvartira",
        district="Chilonzor",
        is_active=True,
    )
    test_session.add(l2)
    await test_session.commit()
    assert await service.is_channel_duplicate(test_session, l2) is True

    # 3. Duplicate with same phone, district, and room count
    l3 = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-dup-phone",
        title="Срочно сдам 2 комнатную на Чиланзаре",
        district="Chilonzor",
        rooms=2,
        contact_phone="+998901234567",
        is_active=True,
    )
    test_session.add(l3)
    await test_session.commit()
    assert await service.is_channel_duplicate(test_session, l3) is True

    # 4. Genuinely different listing -> not a duplicate
    l4 = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-fresh",
        title="Yunusobod 12-kvartal 3 xonali yangi remont",
        district="Yunusobod",
        rooms=3,
        contact_phone="+998939998877",
        is_active=True,
    )
    test_session.add(l4)
    await test_session.commit()
    assert await service.is_channel_duplicate(test_session, l4) is False

    # 5. In-batch candidate duplicate detection
    l5 = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-batch-dup",
        title="Yunusobod 12-kvartal 3 xonali yangi remont",
        district="Yunusobod",
        rooms=3,
        contact_phone="+998939998877",
        is_active=True,
    )
    test_session.add(l5)
    await test_session.commit()
    # When l4 is unposted but present in in_batch_candidates, l5 must be recognized as duplicate!
    assert await service.is_channel_duplicate(test_session, l5, in_batch_candidates=[l4]) is True

    # 6. Genuinely different listing -> not a duplicate
    l4_diff = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/ch-fresh-different",
        title="Mirzo Ulugbek 1-xona shinam",
        district="Mirzo Ulugbek",
        rooms=1,
        contact_phone="+998991112233",
        is_active=True,
    )
    test_session.add(l4_diff)
    await test_session.commit()
    assert await service.is_channel_duplicate(test_session, l4_diff, in_batch_candidates=[l4]) is False


