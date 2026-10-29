"""Tests for REST API endpoints and website integration."""

import pytest
from httpx import AsyncClient
from src.config import settings
from src.models.listing import Listing, ListingClassification
from src.classification.types import ClassificationLabel


@pytest.mark.asyncio
async def test_api_health(api_client: AsyncClient):
    """Verify GET /api/health returns 200 and db connectivity."""
    resp = await api_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "OK"
    assert data["database_connected"] is True


@pytest.mark.asyncio
async def test_api_listings_pagination_and_attribution(api_client: AsyncClient, test_session):
    """Verify GET /api/listings includes pagination and proper external source attribution."""
    # Seed a listing
    listing = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/sample-api-test",
        title="Chilonzor 2 xonali kvartira egasidan",
        price_uzs=3500000,
        district="Chilonzor",
        rooms=2,
        area=54.0,
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

    resp = await api_client.get("/api/listings?limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    item = data["items"][0]
    assert item["canonical_url"] == "https://olx.uz/sample-api-test"
    # Verify original source attribution is preserved
    assert item["source"] == "olx_uz"
    assert "OLX" in item["source_attribution"]
    assert "asl manba havolasi saqlangan" in item["disclaimer"].lower()


@pytest.mark.asyncio
async def test_api_admin_monitor_status_security(api_client: AsyncClient):
    """Verify /api/admin/monitor-status enforces X-API-Key authentication."""
    # Without header -> 401
    resp_unauth = await api_client.get("/api/admin/monitor-status")
    assert resp_unauth.status_code == 401

    # With invalid header -> 401
    resp_bad = await api_client.get(
        "/api/admin/monitor-status",
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp_bad.status_code == 401

    # With correct header -> 200
    resp_ok = await api_client.get(
        "/api/admin/monitor-status",
        headers={"X-API-Key": settings.API_KEY},
    )
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert "provider" in data
    assert "is_running" in data


@pytest.mark.asyncio
async def test_api_manual_listing_ingest(api_client: AsyncClient):
    """Verify POST /api/listings manual ingestion endpoint."""
    payload = {
        "canonical_url": "https://olx.uz/d/manual-test-listing.html",
        "title": "Yunusobod 1 xonali kvartira, egasidan vositachilarsiz",
        "price_raw": "2 500 000 so'm",
        "district": "Yunusobod",
        "rooms": 1,
        "area": 36.0,
        "description": "Kvartira toza, barcha qulayliklar bor.",
    }

    resp = await api_client.post(
        "/api/listings",
        json=payload,
        headers={"X-API-Key": settings.API_KEY},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["price_uzs"] == 2500000
    assert data["classification"] is not None
    assert data["classification"]["label"] == ClassificationLabel.LIKELY_OWNER.value

