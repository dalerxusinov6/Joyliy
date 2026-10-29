"""Unit tests for Telegram Bot Authentication and Web Deep-Link Login."""

import hashlib
import hmac
import time
import pytest
from httpx import AsyncClient, ASGITransport

from src.api.app import create_app
from src.database import init_db, AsyncSessionLocal
from src.services.auth_service import auth_service
from src.config import settings


@pytest.mark.asyncio
async def test_jwt_token_cycle():
    """Verify JWT token creation, signature verification, and decoding."""
    token = auth_service.create_jwt_token(user_id=42, telegram_id=987654321, is_admin=True)
    assert token is not None

    payload = auth_service.decode_jwt_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["tg_id"] == 987654321
    assert payload["admin"] is True

    # Tampered token
    tampered = token[:-4] + "fake"
    assert auth_service.decode_jwt_token(tampered) is None


@pytest.mark.asyncio
async def test_telegram_widget_signature():
    """Verify Telegram Login Widget HMAC-SHA256 signature algorithm."""
    test_token = settings.BOT_TOKEN
    now = int(time.time())
    data = {
        "id": 11223344,
        "first_name": "Sardor",
        "username": "sardor_dev",
        "auth_date": now,
    }

    # Generate valid hash
    check_arr = [f"{k}={data[k]}" for k in sorted(data.keys())]
    data_check_string = "\n".join(check_arr)
    secret_key = hashlib.sha256(test_token.encode("utf-8")).digest()
    valid_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    data["hash"] = valid_hash
    assert auth_service.verify_telegram_widget_data(data) is True

    # Bad hash
    data["hash"] = "invalid_hash"
    assert auth_service.verify_telegram_widget_data(data) is False


@pytest.mark.asyncio
async def test_auth_session_flow():
    """Verify deep-link session lifecycle: create -> check pending -> confirm -> check authenticated."""
    await init_db()
    async with AsyncSessionLocal() as session:
        session_info = await auth_service.create_auth_session(session)
        session_id = session_info["session_id"]
        assert session_id is not None
        assert session_info["bot_url"].startswith(f"https://t.me/{settings.BOT_USERNAME}?start=auth_")

        # Initial status should be PENDING
        status_pending = await auth_service.get_session_status(session, session_id)
        assert status_pending["status"] == "PENDING"

        # Confirm from bot
        success, user = await auth_service.confirm_auth_session(
            session=session,
            session_id=session_id,
            telegram_id=999888777,
            username="bot_user",
            first_name="Bot User",
        )
        assert success is True
        assert user is not None
        assert user.telegram_id == 999888777

        # Status should now be AUTHENTICATED with user and token
        status_auth = await auth_service.get_session_status(session, session_id)
        assert status_auth["status"] == "AUTHENTICATED"
        assert status_auth["token"] is not None
        assert status_auth["user"]["telegram_id"] == 999888777


@pytest.mark.asyncio
async def test_auth_api_endpoints():
    """Verify REST API auth endpoints: session creation, polling, mock confirmation, and /api/auth/me."""
    await init_db()
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create session
        res_create = await client.post("/api/auth/telegram/session")
        assert res_create.status_code == 200
        data = res_create.json()
        session_id = data["session_id"]
        assert "bot_url" in data

        # 2. Check pending
        res_check = await client.get(f"/api/auth/telegram/check?session_id={session_id}")
        assert res_check.status_code == 200
        assert res_check.json()["status"] == "PENDING"

        # 3. Confirm via mock endpoint
        res_confirm = await client.post(
            "/api/auth/telegram/mock_confirm",
            json={"session_id": session_id, "telegram_id": 88776655, "first_name": "Bekzod", "username": "bekzod"},
        )
        assert res_confirm.status_code == 200
        confirmed_data = res_confirm.json()
        assert confirmed_data["status"] == "AUTHENTICATED"
        token = confirmed_data["token"]
        assert token is not None

        # 4. Check session again
        res_check2 = await client.get(f"/api/auth/telegram/check?session_id={session_id}")
        assert res_check2.status_code == 200
        assert res_check2.json()["status"] == "AUTHENTICATED"

        # 5. Get current user profile using bearer token
        res_me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        me_data = res_me.json()
        assert me_data["telegram_id"] == 88776655
        assert me_data["first_name"] == "Bekzod"

