"""Authentication Service for Joyliy Telegram Bot and Web Integration."""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.models.user import User, UserSearchPreference, AuthSession

logger = logging.getLogger(__name__)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))


class AuthService:
    """Handles Telegram Bot Deep-Link login and official Telegram Widget authentication."""

    @staticmethod
    def create_jwt_token(user_id: int, telegram_id: int, is_admin: bool, expires_days: int = 30) -> str:
        """Generate HMAC-SHA256 signed bearer JWT token without external dependencies."""
        now = int(time.time())
        exp = now + (expires_days * 86400)
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": str(user_id),
            "tg_id": telegram_id,
            "admin": is_admin,
            "iat": now,
            "exp": exp,
        }

        b64_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        b64_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{b64_header}.{b64_payload}".encode("utf-8")

        signature = hmac.new(
            settings.JWT_SECRET.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        b64_sig = _b64url_encode(signature)

        return f"{b64_header}.{b64_payload}.{b64_sig}"

    @staticmethod
    def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify signature and expiration of JWT bearer token."""
        try:
            parts = token.strip().split(".")
            if len(parts) != 3:
                return None
            b64_header, b64_payload, b64_sig = parts
            signing_input = f"{b64_header}.{b64_payload}".encode("utf-8")

            expected_sig = hmac.new(
                settings.JWT_SECRET.encode("utf-8"),
                signing_input,
                hashlib.sha256,
            ).digest()
            received_sig = _b64url_decode(b64_sig)

            if not hmac.compare_digest(expected_sig, received_sig):
                return None

            payload = json.loads(_b64url_decode(b64_payload).decode("utf-8"))
            if payload.get("exp", 0) < int(time.time()):
                return None
            return payload
        except Exception as exc:
            logger.debug("Failed to decode JWT token: %s", exc)
            return None

    @staticmethod
    def verify_telegram_widget_data(auth_data: Dict[str, Any]) -> bool:
        """
        Verify Telegram Web Login Widget authorization payload using HMAC-SHA256.
        Follows official Telegram Login Widget specification:
        https://core.telegram.org/widgets/login#checking-authorization
        """
        received_hash = auth_data.get("hash")
        if not received_hash:
            return False

        # Filter out hash and sort key=value by key
        check_arr = []
        for key in sorted(auth_data.keys()):
            if key != "hash" and auth_data[key] is not None:
                check_arr.append(f"{key}={auth_data[key]}")
        data_check_string = "\n".join(check_arr)

        # secret_key = SHA256(bot_token)
        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode("utf-8")).digest()
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(computed_hash, received_hash):
            return False

        # Check timestamp (must not be older than 24 hours)
        auth_date = int(auth_data.get("auth_date", 0))
        if int(time.time()) - auth_date > 86400:
            return False

        return True

    async def get_or_create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> User:
        """Retrieve existing user or create a new user profile with search preferences."""
        stmt = (
            select(User)
            .options(selectinload(User.preference))
            .where(User.telegram_id == telegram_id)
        )
        user = (await session.execute(stmt)).scalar_one_or_none()
        is_admin = telegram_id in settings.ADMIN_IDS

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                photo_url=photo_url,
                is_active=True,
                is_admin=is_admin,
            )
            session.add(user)
            await session.flush()

            pref = UserSearchPreference(
                user_id=user.id,
                districts=[],
                rooms=[],
                owner_only=False,
                include_agency=True,
                notifications_enabled=True,
                quiet_hours_enabled=False,
            )
            session.add(pref)
            await session.commit()
            user.preference = pref
        else:
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if photo_url and user.photo_url != photo_url:
                user.photo_url = photo_url
                updated = True
            if is_admin and not user.is_admin:
                user.is_admin = True
                updated = True
            if updated:
                await session.commit()

        return user

    async def create_auth_session(self, session: AsyncSession) -> Dict[str, Any]:
        """Create a new temporary auth session for Telegram Bot Deep-Link login."""
        session_id = secrets.token_hex(16)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        auth_session = AuthSession(
            session_id=session_id,
            status="PENDING",
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        session.add(auth_session)
        await session.commit()

        bot_username = settings.BOT_USERNAME.lstrip("@")
        bot_url = f"https://t.me/{bot_username}?start=auth_{session_id}"

        return {
            "session_id": session_id,
            "bot_username": bot_username,
            "bot_url": bot_url,
            "expires_in": 600,
        }

    async def confirm_auth_session(
        self,
        session: AsyncSession,
        session_id: str,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> Tuple[bool, Optional[User]]:
        """Mark an auth session as confirmed by Telegram user interaction."""
        stmt = select(AuthSession).where(AuthSession.session_id == session_id)
        auth_session = (await session.execute(stmt)).scalar_one_or_none()
        if not auth_session:
            return False, None

        if auth_session.is_expired():
            auth_session.status = "EXPIRED"
            await session.commit()
            return False, None

        user = await self.get_or_create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            photo_url=photo_url,
        )

        auth_session.status = "AUTHENTICATED"
        auth_session.telegram_id = telegram_id
        auth_session.username = username
        auth_session.first_name = first_name
        auth_session.photo_url = photo_url
        await session.commit()

        return True, user

    async def get_session_status(self, session: AsyncSession, session_id: str) -> Dict[str, Any]:
        """Check status of a deep-link auth session, returning user and JWT on success."""
        stmt = select(AuthSession).where(AuthSession.session_id == session_id)
        auth_session = (await session.execute(stmt)).scalar_one_or_none()
        if not auth_session:
            return {"status": "NOT_FOUND"}

        if auth_session.is_expired():
            if auth_session.status != "AUTHENTICATED":
                auth_session.status = "EXPIRED"
                await session.commit()
                return {"status": "EXPIRED"}

        if auth_session.status == "AUTHENTICATED" and auth_session.telegram_id:
            user = await self.get_or_create_user(
                session=session,
                telegram_id=auth_session.telegram_id,
                username=auth_session.username,
                first_name=auth_session.first_name,
                photo_url=auth_session.photo_url,
            )
            token = self.create_jwt_token(
                user_id=user.id,
                telegram_id=user.telegram_id,
                is_admin=user.is_admin,
            )
            return {
                "status": "AUTHENTICATED",
                "token": token,
                "user": {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "first_name": user.first_name,
                    "username": user.username,
                    "photo_url": user.photo_url,
                    "is_admin": user.is_admin,
                },
            }

        return {"status": auth_session.status}

    async def authenticate_widget(self, session: AsyncSession, widget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user through official Telegram Login Widget payload."""
        if not self.verify_telegram_widget_data(widget_data):
            return {"status": "INVALID_SIGNATURE", "error": "Telegram signatura tekshiruvdan o'tmadi"}

        tg_id = int(widget_data["id"])
        first_name = widget_data.get("first_name")
        username = widget_data.get("username")
        photo_url = widget_data.get("photo_url")

        user = await self.get_or_create_user(
            session=session,
            telegram_id=tg_id,
            username=username,
            first_name=first_name,
            photo_url=photo_url,
        )

        token = self.create_jwt_token(
            user_id=user.id,
            telegram_id=user.telegram_id,
            is_admin=user.is_admin,
        )

        return {
            "status": "AUTHENTICATED",
            "token": token,
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "photo_url": user.photo_url,
                "is_admin": user.is_admin,
            },
        }


auth_service = AuthService()

