"""Comprehensive tests for Joyliy Technical SEO, XML Sitemaps, and Robots.txt."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.app import app
from src.config import settings
from src.models.listing import Listing
from src.services.seo_service import seo_service, DISTRICT_METADATA


@pytest.mark.asyncio
async def test_robots_txt():
    """Verify /robots.txt serves correct directives, allows search routes, and declares sitemaps."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/robots.txt")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        body = resp.text
        assert "User-agent: *" in body
        assert "Allow: /" in body
        assert "Allow: /elon/" in body
        assert "Allow: /toshkent/" in body
        assert "Disallow: /admin/" in body
        assert "Disallow: /api/" in body
        assert "Sitemap: https://joyliy.uz/sitemap.xml" in body


@pytest.mark.asyncio
async def test_sitemap_index():
    """Verify /sitemap.xml serves valid sitemap index referencing all sub-sitemaps."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/sitemap.xml")
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["content-type"]
        body = resp.text
        assert "<sitemapindex" in body
        assert "https://joyliy.uz/sitemap-pages.xml" in body
        assert "https://joyliy.uz/sitemap-locations.xml" in body
        assert "https://joyliy.uz/sitemap-categories.xml" in body
        assert "https://joyliy.uz/sitemap-listings.xml" in body


@pytest.mark.asyncio
async def test_sitemap_pages():
    """Verify /sitemap-pages.xml includes homepage and core landing pages."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/sitemap-pages.xml")
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["content-type"]
        body = resp.text
        assert "<urlset" in body
        assert "<loc>https://joyliy.uz/</loc>" in body
        assert "<loc>https://joyliy.uz/toshkent</loc>" in body
        assert "<loc>https://joyliy.uz/toshkent/arzon-kvartiralar</loc>" in body
        assert "<loc>https://joyliy.uz/toshkent/sotiladigan-uylar</loc>" in body


@pytest.mark.asyncio
async def test_sitemap_locations():
    """Verify /sitemap-locations.xml includes all 12 Tashkent districts."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/sitemap-locations.xml")
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["content-type"]
        body = resp.text
        assert "<urlset" in body
        for dist in DISTRICT_METADATA:
            assert f"https://joyliy.uz/toshkent/{dist['slug']}" in body


@pytest.mark.asyncio
async def test_sitemap_categories():
    """Verify /sitemap-categories.xml includes room counts and district category pages."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/sitemap-categories.xml")
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["content-type"]
        body = resp.text
        assert "<urlset" in body
        assert "https://joyliy.uz/toshkent/1-xonali-kvartiralar" in body
        assert "https://joyliy.uz/toshkent/2-xonali-kvartiralar" in body
        assert "https://joyliy.uz/toshkent/3-xonali-kvartiralar" in body
        assert "https://joyliy.uz/toshkent/chilonzor/kvartiralar" in body


@pytest.mark.asyncio
async def test_sitemap_listings(api_client: AsyncClient, test_session: AsyncSession):
    """Verify /sitemap-listings.xml queries database and outputs listing loc, lastmod, and images."""
    # Seed a test listing
    listing = Listing(
        source="olx_uz",
        canonical_url="https://olx.uz/test-sitemap-seo-item-1",
        title="Yunusobod 3 xonali shinam kvartira",
        price_uzs=4500000,
        district="Yunusobod",
        rooms=3,
        area=72.0,
        image_urls=["https://frankfurt.apollo.olxcdn.com/test-img-1.jpg"],
        is_active=True,
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    resp = await api_client.get("/sitemap-listings.xml")
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    body = resp.text
    assert "<urlset" in body
    assert f"<loc>https://joyliy.uz/elon/{listing.id}</loc>" in body
    assert "https://frankfurt.apollo.olxcdn.com/test-img-1.jpg" in body
    assert "Yunusobod 3 xonali shinam kvartira" in body


@pytest.mark.asyncio
async def test_seo_district_helper():
    """Verify district slug lookup logic and metadata."""
    chil = seo_service.get_district_info("chilonzor")
    assert chil is not None
    assert chil["name_uz"] == "Chilonzor"
    assert chil["name_ru"] == "Чиланзар"

    mirzo = seo_service.get_district_info("mirzo-ulugbek")
    assert mirzo is not None
    assert "Mirzo Ulug‘bek" in mirzo["db_names"]

    unknown = seo_service.get_district_info("unknown-region")
    assert unknown is None


@pytest.mark.asyncio
async def test_admin_seo_endpoints():
    """Verify authenticated admin can fetch SEO audit summary and trigger sitemaps sync."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login as admin
        login_res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get SEO summary
        summary_res = await ac.get("/api/admin/seo/summary", headers=headers)
        assert summary_res.status_code == 200
        data = summary_res.json()
        assert "health_score" in data
        assert "total_active_listings" in data
        assert "total_indexable_urls" in data
        assert "sitemaps" in data
        assert len(data["sitemaps"]) == 5

        # 3. Trigger sync
        sync_res = await ac.post("/api/admin/seo/sync", headers=headers)
        assert sync_res.status_code == 200
        sync_data = sync_res.json()
        assert sync_data["success"] is True
        assert "details" in sync_data
