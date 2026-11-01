"""Tests for Qwen 2.5 Free Model integration and continuous publishing."""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.free_llm_service import free_llm_service, FreeLLMService
from src.services.notification_service import NotificationService
from src.models.listing import Listing, ChannelPublishQueue, QueueStatus
from src.providers.base import RawListingItem
from src.services.listing_service import ListingService


@pytest.mark.asyncio
async def test_qwen_search_criteria_extraction():
    """Verify Qwen extracts structured real-estate criteria from conversational queries."""
    query = "Chilonzor metrosi yaqinida 2 xonali maklersiz kvartira kerak, byudjet 4 million"
    
    # Mock Qwen response
    mock_qwen_json = (
        '{"district": "Chilonzor", "metro": "Chilonzor", "rooms": 2, '
        '"max_price_uzs": 4000000, "owner_only": true, "target_audience": "any", '
        '"reasoning": "Chilonzorda 2 xonali maklersiz xonadon topildi."}'
    )
    
    with patch.object(free_llm_service, "_call_qwen_suite", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_qwen_json
        criteria = await free_llm_service.extract_search_criteria(query)
        
        assert criteria is not None
        assert criteria["district"] == "Chilonzor"
        assert criteria["rooms"] == 2
        assert criteria["max_price_uzs"] == 4000000
        assert criteria["owner_only"] is True


@pytest.mark.asyncio
async def test_qwen_listing_evaluation():
    """Verify Qwen listing evaluation returns grounded valuation and advice."""
    listing_info = {
        "title": "Chilonzor 9-kvartal 2 xonali kvartira",
        "price_uzs": 3500000,
        "district": "Chilonzor",
        "area": 50,
        "rooms": 2,
        "is_owner": True,
        "description": "Toza remont, barcha sharoitlari bor.",
    }
    question = "Bu kvartiraning narxi qanchalik adolatli?"
    
    with patch.object(free_llm_service, "_call_qwen_suite", new_callable=AsyncMock) as mock_qwen:
        mock_qwen.return_value = (
            "Ushbu kvartira Chilonzor tumani uchun juda yaxshi narxda (70,000 so‘m/m²). "
            "Bozor o‘rtacha narxi 75,000 so‘m/m². Egasidan bo‘lgani sababli 0% komissiya."
        )
        answer = await free_llm_service.evaluate_listing(listing_info, question)
        assert "Chilonzor" in answer
        assert "komissiya" in answer or "narx" in answer


@pytest.mark.asyncio
async def test_continuous_channel_publishing_without_artificial_cap(
    test_session: AsyncSession, listing_service_test: ListingService
):
    """
    Verify newly discovered listings are published directly upon scraping
    without returning 0 or being restricted by arbitrary daily caps.
    """
    notif = NotificationService()
    mock_bot = AsyncMock()
    mock_bot.send_message.return_value = AsyncMock(message_id=9901)
    notif.set_bot(mock_bot)

    # Ingest 3 genuinely new unique listings
    new_listings = []
    for i in range(1, 4):
        item = RawListingItem(
            source="olx_uz",
            source_id=f"cont-test-{i}",
            canonical_url=f"https://www.olx.uz/d/obyavlenie/unique-ad-{i}.html",
            title=f"Yunusobod {i}-mavze {i} xonali xonadon",
            price_raw=f"{3000000 + i * 500000} so'm",
            price_uzs=3000000 + i * 500000,
            district="Yunusobod",
            rooms=i,
        )
        listing, is_new = await listing_service_test.ingest_raw_listing(test_session, item)
        assert is_new is True
        new_listings.append(listing)

    # Broadcast batch to channel
    with patch.object(notif, "send_to_channel_verified", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = 8888
        posted = await notif.broadcast_channel_batch(test_session, new_listings=new_listings)

        # Must publish all 3 listings without being limited to 0 or 1
        assert posted == 3
        assert mock_send.call_count == 3

