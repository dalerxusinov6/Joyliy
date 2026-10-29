"""Tests for user subscription management and preference persistence."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, UserSearchPreference


@pytest.mark.asyncio
async def test_user_subscription_lifecycle(test_session: AsyncSession):
    """Test pausing, resuming, and persisting user subscription settings."""
    user = User(telegram_id=112233, username="tashkent_renter")
    test_session.add(user)
    await test_session.flush()

    pref = UserSearchPreference(
        user_id=user.id,
        districts=["Chilonzor", "Yakkasaroy"],
        min_price=2000000,
        max_price=4500000,
        rooms=[1, 2],
        owner_only=True,
        notifications_enabled=True,
    )
    test_session.add(pref)
    await test_session.commit()

    # Verify initial settings
    loaded_pref = (await test_session.execute(
        select(UserSearchPreference).where(UserSearchPreference.user_id == user.id)
    )).scalar_one()
    assert loaded_pref.notifications_enabled is True
    assert loaded_pref.owner_only is True
    assert "Chilonzor" in loaded_pref.districts

    # Simulate /stop
    loaded_pref.notifications_enabled = False
    await test_session.commit()

    paused_pref = (await test_session.execute(
        select(UserSearchPreference).where(UserSearchPreference.user_id == user.id)
    )).scalar_one()
    assert paused_pref.notifications_enabled is False

    # Simulate /resume
    paused_pref.notifications_enabled = True
    await test_session.commit()

    resumed_pref = (await test_session.execute(
        select(UserSearchPreference).where(UserSearchPreference.user_id == user.id)
    )).scalar_one()
    assert resumed_pref.notifications_enabled is True

