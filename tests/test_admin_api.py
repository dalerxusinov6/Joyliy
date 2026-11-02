"""Integration tests for Enterprise Admin Dashboard API."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app
from src.config import settings
from src.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_admin_login_success():
    """Test successful admin login with master credentials."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "token" in data
        assert data["admin"]["username"] == "admin"
        assert data["admin"]["role"] == "super_admin"


@pytest.mark.asyncio
async def test_admin_login_failure():
    """Test rejected login with incorrect credentials."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "wrongpassword123"},
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_protected_routes():
    """Test that admin endpoints require authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Unauthenticated request should fail
        unauth_res = await ac.get("/api/admin/overview/stats")
        assert unauth_res.status_code == 401

        # Login and obtain token
        login_res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Overview Stats
        stats_res = await ac.get("/api/admin/overview/stats", headers=headers)
        assert stats_res.status_code == 200
        stats_data = stats_res.json()
        assert "summary" in stats_data
        assert "growth_chart" in stats_data
        assert "district_distribution" in stats_data
        assert "latest_listings" in stats_data

        # 2. Listings List
        listings_res = await ac.get("/api/admin/listings?limit=10", headers=headers)
        assert listings_res.status_code == 200
        listings_data = listings_res.json()
        assert "items" in listings_data
        assert "total" in listings_data
        assert "page" in listings_data

        # 3. Parser Status
        parser_res = await ac.get("/api/admin/parser/status", headers=headers)
        assert parser_res.status_code == 200
        parser_data = parser_res.json()
        assert "status" in parser_data
        assert "schedule_times" in parser_data

        # 4. Telegram Overview
        tg_res = await ac.get("/api/admin/telegram/overview", headers=headers)
        assert tg_res.status_code == 200
        tg_data = tg_res.json()
        assert "metrics" in tg_data
        assert "queue" in tg_data

        # 5. Users List
        users_res = await ac.get("/api/admin/users?limit=5", headers=headers)
        assert users_res.status_code == 200
        users_data = users_res.json()
        assert "items" in users_data

        # 6. Settings
        settings_res = await ac.get("/api/admin/settings", headers=headers)
        assert settings_res.status_code == 200
        settings_data = settings_res.json()
        assert "general" in settings_data
        assert "database" in settings_data


@pytest.mark.asyncio
async def test_public_ad_submission_and_admin_moderation():
    """Verify that user posted ads are submitted as pending and require admin approval."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. User submits an ad via public website
        post_data = {
            "title": "Chilonzorda yangi 2 xonali kvartira sotiladi",
            "district": "Chilonzor",
            "rooms": 2,
            "price": 550000000,
            "currency": "UZS",
            "area": 60.0,
            "floor": "4/9",
            "deal_type": "sale",
            "property_type": "secondary",
            "phone": "+998901234567",
            "telegram": "@testowner",
            "description": "Toza va qulay xonadon",
            "is_owner": True,
        }
        submit_res = await ac.post("/api/listings/submit", json=post_data)
        assert submit_res.status_code == 201
        res_json = submit_res.json()
        assert res_json["success"] is True
        listing_id = res_json["listing_id"]

        # 2. Check that the listing is NOT active in public listings catalog
        public_res = await ac.get(f"/api/listings/{listing_id}")
        assert public_res.status_code == 404 or public_res.json().get("is_active") is False

        # 3. Log in as admin
        login_res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Check listing in admin pending list
        pending_res = await ac.get("/api/admin/listings?status=pending", headers=headers)
        assert pending_res.status_code == 200
        pending_items = pending_res.json()["items"]
        assert any(item["id"] == listing_id for item in pending_items)

        # 5. Admin approves listing
        approve_res = await ac.post(
            f"/api/admin/listings/{listing_id}/approve",
            headers=headers,
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["success"] is True

        # 6. Verify listing is now active
        detail_res = await ac.get(f"/api/admin/listings/{listing_id}", headers=headers)
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["is_active"] is True
        assert detail_data["status"] == "active"


