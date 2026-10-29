"""Tests for Composite Listing Provider aggregation."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.providers.base import ProviderStatus, RawListingItem
from src.providers.composite import CompositeListingProvider


@pytest.mark.asyncio
async def test_composite_provider():
    """Test CompositeListingProvider aggregation and health checks."""
    p1 = MagicMock()
    p1.name = "source_1"
    item1 = RawListingItem(
        source="src1",
        source_id="1",
        canonical_url="https://src1.uz/1",
        title="1 xonali Chilonzor",
    )
    p1.fetch_listings = AsyncMock(return_value=[item1])
    p1.check_health = AsyncMock(
        return_value=MagicMock(status=ProviderStatus.HEALTHY, message="OK")
    )

    p2 = MagicMock()
    p2.name = "source_2"
    item2 = RawListingItem(
        source="src2",
        source_id="2",
        canonical_url="https://src2.uz/2",
        title="2 xonali Yunusobod",
    )
    p2.fetch_listings = AsyncMock(return_value=[item2])
    p2.check_health = AsyncMock(
        return_value=MagicMock(status=ProviderStatus.HEALTHY, message="OK")
    )

    composite = CompositeListingProvider([p1, p2])
    results = await composite.fetch_listings()
    assert len(results) == 2
    assert results[0].canonical_url == "https://src1.uz/1"
    assert results[1].canonical_url == "https://src2.uz/2"

    health = await composite.check_health()
    assert health.status == ProviderStatus.HEALTHY
