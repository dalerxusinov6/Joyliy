"""Tests for the AI-Powered Real Estate Ecosystem services and endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.listing import Listing
from src.services.ai_match_service import ai_match_service
from src.services.price_intelligence_service import price_intelligence_service
from src.services.scam_detector_service import scam_detector_service
from src.services.roommate_service import roommate_service
from src.services.assistant_service import assistant_service
from src.services.neighborhood_service import neighborhood_service
from src.api.app import create_app


def test_ai_match_nlp_extraction():
    """Verify natural language extraction of district, budget, rooms, and audience."""
    query = "Chilonzorda metro yaqinida 4 million so'mgacha 2 xonali kvartira oila uchun maklersiz"
    parsed = ai_match_service.parse_natural_language_query(query)

    assert parsed["district"] == "Chilonzor"
    assert parsed["rooms"] == 2
    assert parsed["max_price_uzs"] == 4000000
    assert parsed["owner_only"] is True
    assert parsed["target_audience"] == "family"


@pytest.mark.asyncio
async def test_price_intelligence_evaluation(test_session: AsyncSession):
    """Verify market pricing classification (below market / fair price / above market)."""
    listing = Listing(
        title="2 xona Chilonzor",
        price_uzs=3200000,
        district="Chilonzor",
        rooms=2,
        area=50.0,
        canonical_url="https://test.olx.uz/item-price-1",
        source="test",
        source_id="tp-1",
    )
    test_session.add(listing)
    await test_session.flush()

    eval_res = await price_intelligence_service.evaluate_listing_price(test_session, listing)
    assert eval_res["category"] in ("below_market", "fair_price", "above_market")
    assert eval_res["estimated_market_price"] > 0


@pytest.mark.asyncio
async def test_scam_detector_signals(test_session: AsyncSession):
    """Verify fraud detection scores suspicious prepayment requests."""
    listing_safe = Listing(
        title="Chilonzor 2 xonali kvartira egasidan",
        price_uzs=4000000,
        district="Chilonzor",
        rooms=2,
        description="Toza kvartira, hamma sharoitlari bor. Ko'rib ma'qul kelsa shartnoma tuzamiz.",
        canonical_url="https://test.olx.uz/item-safe-1",
        source="test",
        source_id="ts-1",
    )
    res_safe = await scam_detector_service.analyze_listing_risk(test_session, listing_safe)
    assert res_safe["risk_score"] < 40
    assert res_safe["risk_level"].lower() == "low"

    listing_scam = Listing(
        title="Super arzon kvartira",
        price_uzs=800000,
        district="Chilonzor",
        rooms=2,
        description="Xonadonni ko'rishdan oldin plastik kartaga zakalat tashlang, odamlar ko'p kelyapti.",
        canonical_url="https://test.olx.uz/item-scam-1",
        source="test",
        source_id="tsc-1",
    )
    res_scam = await scam_detector_service.analyze_listing_risk(test_session, listing_scam)
    assert res_scam["risk_score"] > 40
    assert res_scam["risk_level"].lower() in ("medium", "high")
    assert any("to‘lov" in r.lower() or "pul" in r.lower() or "kartaga" in r.lower() for r in res_scam["reasons"])


@pytest.mark.asyncio
async def test_roommate_compatibility_and_seeding(test_session: AsyncSession):
    """Verify roommate profiles fetching and compatibility calculations."""
    profiles = await roommate_service.list_profiles(test_session, limit=10)
    assert len(profiles) >= 3

    p = profiles[0]
    res = roommate_service.calculate_compatibility(
        {"gender": p.gender, "preferred_districts": p.preferred_districts, "budget_uzs": p.budget_uzs},
        p
    )
    assert 60 <= res["score"] <= 100


@pytest.mark.asyncio
async def test_assistant_rental_advisor(test_session: AsyncSession):
    """Verify AI virtual advisor returns valid legal references and advice."""
    res = await assistant_service.get_response(test_session, "Ijara shartnomasini soliqda ro'yxatdan o'tkazish tartibi qanday?")
    reply = res.get("reply") or res.get("response") or ""
    assert "soliq" in reply.lower() or "shartnoma" in reply.lower()
    assert len(res["legal_references"]) > 0
    assert len(res["practical_tips"]) > 0


@pytest.mark.asyncio
async def test_ecosystem_api_routes(test_session: AsyncSession):
    """Verify REST API endpoints for neighborhoods, AI match, and assistant."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Neighborhoods
        resp_neigh = await ac.get("/api/neighborhoods")
        assert resp_neigh.status_code == 200
        data_neigh = resp_neigh.json()
        assert len(data_neigh["districts"]) == 12

        # 2. AI Match
        resp_match = await ac.post("/api/ai/match", json={"query": "Chilonzorda 4 mln gacha kvartira", "limit": 5})
        assert resp_match.status_code == 200
        data_match = resp_match.json()
        assert "results" in data_match
        assert data_match["parsed_filters"]["district"] == "Chilonzor"

        # 3. AI Assistant
        resp_ask = await ac.post("/api/assistant/chat", json={"message": "Zalog depozit qachon qaytariladi?"})
        assert resp_ask.status_code == 200
        data_ask = resp_ask.json()
        assert "reply" in data_ask or "response" in data_ask
        assert len(data_ask.get("practical_tips", [])) > 0
