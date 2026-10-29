"""Tests for per-user search preference matching and filtering."""

from src.models.listing import Listing, ListingClassification
from src.models.user import UserSearchPreference
from src.classification.types import ClassificationLabel
from src.services.notification_service import matches_user_preference


def test_district_filtering():
    """Verify listings match when in user's selected districts and reject otherwise."""
    pref = UserSearchPreference(
        user_id=1,
        districts=["Chilonzor", "Yunusobod"],
        rooms=[],
        notifications_enabled=True,
    )

    matching_listing = Listing(
        canonical_url="https://olx.uz/1",
        title="Chilonzor kvartira",
        district="Chilonzor",
    )
    non_matching_listing = Listing(
        canonical_url="https://olx.uz/2",
        title="Sergeli kvartira",
        district="Sergeli",
    )

    assert matches_user_preference(matching_listing, pref) is True
    assert matches_user_preference(non_matching_listing, pref) is False


def test_price_range_filtering():
    """Verify min and max price boundaries in UZS."""
    pref = UserSearchPreference(
        user_id=1,
        districts=[],
        rooms=[],
        min_price=2000000,
        max_price=4000000,
        notifications_enabled=True,
    )

    in_range = Listing(canonical_url="https://olx.uz/1", title="Uy", price_uzs=3000000)
    too_cheap = Listing(canonical_url="https://olx.uz/2", title="Uy", price_uzs=1500000)
    too_expensive = Listing(canonical_url="https://olx.uz/3", title="Uy", price_uzs=5000000)

    assert matches_user_preference(in_range, pref) is True
    assert matches_user_preference(too_cheap, pref) is False
    assert matches_user_preference(too_expensive, pref) is False


def test_room_count_filtering():
    """Verify room count filters."""
    pref = UserSearchPreference(
        user_id=1,
        districts=[],
        rooms=[1, 2],
        notifications_enabled=True,
    )

    one_room = Listing(canonical_url="https://olx.uz/1", title="Uy", rooms=1)
    two_rooms = Listing(canonical_url="https://olx.uz/2", title="Uy", rooms=2)
    three_rooms = Listing(canonical_url="https://olx.uz/3", title="Uy", rooms=3)

    assert matches_user_preference(one_room, pref) is True
    assert matches_user_preference(two_rooms, pref) is True
    assert matches_user_preference(three_rooms, pref) is False


def test_owner_only_filter():
    """When owner_only is True, agency listings must be rejected."""
    pref = UserSearchPreference(
        user_id=1,
        districts=[],
        rooms=[],
        owner_only=True,
        notifications_enabled=True,
    )

    owner_listing = Listing(
        canonical_url="https://olx.uz/1",
        title="Uy",
        classification=ListingClassification(
            label=ClassificationLabel.LIKELY_OWNER.value,
            confidence_score=0.85,
        ),
    )
    agent_listing = Listing(
        canonical_url="https://olx.uz/2",
        title="Uy",
        classification=ListingClassification(
            label=ClassificationLabel.LIKELY_AGENT.value,
            confidence_score=0.20,
        ),
    )

    assert matches_user_preference(owner_listing, pref) is True
    assert matches_user_preference(agent_listing, pref) is False


def test_agency_exclusion_filter():
    """When include_agency is False, LIKELY_AGENT listings must be rejected."""
    pref = UserSearchPreference(
        user_id=1,
        districts=[],
        rooms=[],
        owner_only=False,
        include_agency=False,
        notifications_enabled=True,
    )

    review_listing = Listing(
        canonical_url="https://olx.uz/1",
        title="Uy",
        classification=ListingClassification(
            label=ClassificationLabel.NEEDS_REVIEW.value,
            confidence_score=0.50,
        ),
    )
    agent_listing = Listing(
        canonical_url="https://olx.uz/2",
        title="Uy",
        classification=ListingClassification(
            label=ClassificationLabel.LIKELY_AGENT.value,
            confidence_score=0.15,
        ),
    )

    assert matches_user_preference(review_listing, pref) is True
    assert matches_user_preference(agent_listing, pref) is False

