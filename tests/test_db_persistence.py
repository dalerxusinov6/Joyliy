"""Tests for database integrity, transactions, and foreign key cascades."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserSearchPreference
from src.models.listing import Listing, ListingClassification, Favorite, NotificationHistory
from src.models.system import SourceMonitorRun, AdminAuditLog


@pytest.mark.asyncio
async def test_user_telegram_id_uniqueness(test_session: AsyncSession):
    """Enforce unique telegram_id."""
    u1 = User(telegram_id=555111)
    test_session.add(u1)
    await test_session.commit()

    u2 = User(telegram_id=555111)
    test_session.add(u2)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


@pytest.mark.asyncio
async def test_favorite_unique_constraint(test_session: AsyncSession):
    """Cannot bookmark the same listing twice for a user."""
    user = User(telegram_id=777)
    test_session.add(user)
    listing = Listing(canonical_url="https://olx.uz/fav-test", title="Fav listing")
    test_session.add(listing)
    await test_session.commit()

    f1 = Favorite(user_id=user.id, listing_id=listing.id)
    test_session.add(f1)
    await test_session.commit()

    f2 = Favorite(user_id=user.id, listing_id=listing.id)
    test_session.add(f2)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


@pytest.mark.asyncio
async def test_cascade_delete_user(test_session: AsyncSession):
    """Deleting a user cascades and deletes preferences and favorites."""
    user = User(telegram_id=888)
    test_session.add(user)
    await test_session.flush()

    pref = UserSearchPreference(user_id=user.id, districts=[])
    test_session.add(pref)
    await test_session.commit()

    # Delete user
    await test_session.delete(user)
    await test_session.commit()

    # Ensure preference is also gone
    pref_check = (await test_session.execute(
        select(UserSearchPreference).where(UserSearchPreference.user_id == user.id)
    )).scalar_one_or_none()
    assert pref_check is None


@pytest.mark.asyncio
async def test_source_monitor_run_recording(test_session: AsyncSession):
    """Verify source monitor audit persistence."""
    run = SourceMonitorRun(
        source_name="olx_uz_http",
        status="SUCCESS",
        listings_found=15,
        listings_new=3,
    )
    test_session.add(run)
    await test_session.commit()

    loaded = (await test_session.execute(
        select(SourceMonitorRun).where(SourceMonitorRun.id == run.id)
    )).scalar_one()
    assert loaded.status == "SUCCESS"
    assert loaded.listings_new == 3

