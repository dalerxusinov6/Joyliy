"""Tests for Public Ad Image Uploading, Admin Moderation, and Telegram Channel Broadcast."""

import base64
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.app import app
from src.config import settings
from src.services.notification_service import notification_service
from tests.conftest import MockTelegramBot


@pytest.mark.asyncio
async def test_upload_image_multipart_and_base64():
    """Verify POST /api/upload/image handles both multipart file uploads and base64 payloads."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Test multipart upload
        dummy_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00"
        files = {"file": ("test_room.jpg", dummy_jpeg, "image/jpeg")}
        resp1 = await ac.post("/api/upload/image", files=files)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["success"] is True
        assert data1["url"].startswith("/uploads/img_")
        assert data1["url"].endswith(".jpg")

        # Verify static serving of uploaded image
        uploaded_url = data1["url"]
        get_resp = await ac.get(uploaded_url)
        assert get_resp.status_code == 200
        assert len(get_resp.content) == len(dummy_jpeg)

        # 2. Test base64 JSON upload
        b64_str = base64.b64encode(dummy_jpeg).decode("utf-8")
        payload = {
            "image": f"data:image/jpeg;base64,{b64_str}",
            "filename": "living_room.png",
        }
        resp2 = await ac.post("/api/upload/image", json=payload)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["success"] is True
        assert data2["url"].startswith("/uploads/img_")


@pytest.mark.asyncio
async def test_submit_ad_with_images_and_admin_telegram_approval(mock_bot: MockTelegramBot):
    """
    Complete end-to-end flow:
    1. Upload images
    2. Submit public ad with uploaded images
    3. Verify ad is pending moderation and not publicly live
    4. Admin inspects ad in /api/admin/listings?status=pending with photos
    5. Admin approves ad -> becomes active and broadcasts to Telegram channel
    """
    # Attach mock bot to notification_service for telegram testing
    notification_service.set_bot(mock_bot)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Upload two photos
        dummy_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00"
        files1 = {"file": ("room1.jpg", dummy_jpeg, "image/jpeg")}
        up1 = (await ac.post("/api/upload/image", files=files1)).json()
        files2 = {"file": ("room2.jpg", dummy_jpeg, "image/jpeg")}
        up2 = (await ac.post("/api/upload/image", files=files2)).json()

        image_urls = [up1["url"], up2["url"]]

        # 2. Submit ad with images
        submit_payload = {
            "title": "Chilonzorda 3 xonali ta’mirlangan shinam xonadon",
            "district": "Chilonzor",
            "rooms": 3,
            "price": 5500000,
            "currency": "UZS",
            "area": 75.0,
            "floor": "4/9",
            "deal_type": "rent",
            "phone": "+998901234567",
            "telegram": "@chilonzor_owner",
            "description": "Barcha qulayliklar bor, mebellar va texnika yangi.",
            "is_owner": True,
            "image_urls": image_urls,
        }
        sub_resp = await ac.post("/api/listings/submit", json=submit_payload)
        assert sub_resp.status_code == 201
        sub_data = sub_resp.json()
        assert sub_data["success"] is True
        listing_id = sub_data["listing_id"]

        # 3. Log in as admin
        login_res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Check listing appears in pending moderation queue
        pending_res = await ac.get("/api/admin/listings?status=pending", headers=headers)
        assert pending_res.status_code == 200
        pending_items = pending_res.json()["items"]
        target_item = next((item for item in pending_items if item["id"] == listing_id), None)
        assert target_item is not None
        assert target_item["is_active"] is False
        assert target_item["district"] == "Chilonzor"
        assert len(target_item["image_urls"]) == 2

        # 5. Admin approves listing -> should activate and send to Telegram
        approve_res = await ac.post(f"/api/admin/listings/{listing_id}/approve", headers=headers)
        assert approve_res.status_code == 200
        approve_data = approve_res.json()
        assert approve_data["is_active"] is True
        assert approve_data["telegram_posted"] is True

        # 6. Verify Telegram mock bot captured the channel post with photos
        assert len(mock_bot.sent_photos) > 0 or len(mock_bot.sent_messages) > 0

        # 7. Verify listing is now publicly active
        detail_res = await ac.get(f"/api/listings/{listing_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["is_active"] is True
        assert len(detail_data["image_urls"]) == 2

