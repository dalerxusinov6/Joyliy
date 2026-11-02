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
