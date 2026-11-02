"""Tests for Roommate Questionnaire (Anketa) Submission and Admin Moderation Workflow."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app
from src.config import settings


@pytest.mark.asyncio
async def test_roommate_submission_and_admin_moderation():
    """
    Test complete end-to-end roommate anketa flow:
    1. User submits an anketa from website (via POST /api/roommates or /api/roommates/profiles).
    2. Anketa is saved with is_active=False (pending admin moderation).
    3. Public GET /api/roommates only returns active profiles, so pending anketa is hidden.
    4. Admin inspects pending queue via GET /api/admin/roommates?status=pending.
    5. Admin approves profile via POST /api/admin/roommates/{id}/approve -> becomes active.
    6. Public GET /api/roommates now includes the newly approved profile.
    7. Admin rejects profile via POST /api/admin/roommates/{id}/reject -> deactivates it.
    8. Admin deletes profile via DELETE /api/admin/roommates/{id}.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. User submits anketa from website
        payload = {
            "name": "Alisher Navoiy",
            "age": 23,
            "gender": "male",
            "preferred_district": "Chilonzor",
            "budget_uzs": 2200000,
            "occupation": "Dasturchi (Fullstack)",
            "lifestyle_tags": ["Chekmaydi", "Tinch rejim", "Tozalik"],
            "about": "Metro yaqinidan 2 kishilik xonadonga sherik izlayapman.",
            "contact_telegram": "@alisher_coder",
        }

        # Submit via /api/roommates
        res1 = await ac.post("/api/roommates", json=payload)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["status"] == "created"
        assert data1["is_active"] is False  # Must be pending moderation!
        profile_id = data1["profile_id"]

        # Also verify alias /api/roommates/profiles works without errors
        res2 = await ac.post("/api/roommates/profiles", json={**payload, "name": "Shoxrux Mirzo", "contact_telegram": "shoxrux_m"})
        assert res2.status_code == 200
        assert res2.json()["status"] == "created"
        profile_id_2 = res2.json()["profile_id"]

        # 2. Public list should NOT include unapproved profiles
        pub_res = await ac.get("/api/roommates")
        assert pub_res.status_code == 200
        pub_profiles = pub_res.json()["profiles"]
        pub_ids = [p["id"] for p in pub_profiles]
        assert profile_id not in pub_ids
        assert profile_id_2 not in pub_ids

        # 3. Log in as admin
        login_res = await ac.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD},
        )
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Check admin overview stats include roommates metrics
        stats_res = await ac.get("/api/admin/overview", headers=headers)
        assert stats_res.status_code == 200
        stats_data = stats_res.json()
        assert "roommates" in stats_data
        assert stats_data["roommates"]["pending"] >= 2

        # 5. Admin lists pending roommates
        admin_pending_res = await ac.get("/api/admin/roommates?status=pending", headers=headers)
        assert admin_pending_res.status_code == 200
        pending_items = admin_pending_res.json()["items"]
        target = next((item for item in pending_items if item["id"] == profile_id), None)
        assert target is not None
        assert target["is_active"] is False
        assert target["name"] == "Alisher Navoiy"
        assert target["preferred_district"] == "Chilonzor"
        assert "Chekmaydi" in target["lifestyle_tags"]
        assert target["contact_telegram"] == "alisher_coder"

        # 6. Admin approves profile
        approve_res = await ac.post(f"/api/admin/roommates/{profile_id}/approve", headers=headers)
        assert approve_res.status_code == 200
        assert approve_res.json()["is_active"] is True

        # 7. Now public list must include Alisher Navoiy
        pub_res_after = await ac.get("/api/roommates")
        pub_profiles_after = pub_res_after.json()["profiles"]
        approved_target = next((p for p in pub_profiles_after if p["id"] == profile_id), None)
        assert approved_target is not None
        assert approved_target["is_active"] is True
        assert approved_target["preferred_district"] == "Chilonzor"

        # 8. Test connection request
        connect_res = await ac.post(
            f"/api/roommates/{profile_id}/connect",
            json={
                "from_name": "Bobur",
                "from_contact": "@bobur_dev",
                "message": "Salom, birga ijaraga turish bo‘yicha gaplashsak bo‘ladimi?",
            },
        )
        assert connect_res.status_code == 200
        assert connect_res.json()["status"] == "sent"

        # 9. Admin rejects / deactivates profile
        reject_res = await ac.post(
            f"/api/admin/roommates/{profile_id}/reject",
            json={"reason": "Telefon raqami noto‘g‘ri"},
            headers=headers,
        )
        assert reject_res.status_code == 200
        assert reject_res.json()["is_active"] is False

        # 10. Admin deletes second profile
        del_res = await ac.delete(f"/api/admin/roommates/{profile_id_2}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True
