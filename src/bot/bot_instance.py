"""Telegram Bot and Dispatcher setup."""

import logging
from typing import Optional, Tuple
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.bot.handlers.common import common_router
from src.bot.handlers.search import search_router
from src.bot.handlers.favorites import favorites_router
from src.bot.handlers.subscription import subscription_router
from src.bot.handlers.admin import admin_router
from src.bot.handlers.ecosystem import ecosystem_router

logger = logging.getLogger(__name__)


def create_bot_and_dispatcher() -> Tuple[Optional[Bot], Optional[Dispatcher]]:
    """Factory to initialize aiogram Bot and register all routers.

    Safely handles missing or mock tokens so web application can run even without Telegram.
    """
    token = settings.BOT_TOKEN
    if not token or token in ("mock_token_for_testing", "none", "") or ":" not in token:
        logger.warning(
            "Telegram BOT_TOKEN is not configured or is a placeholder ('%s'). Running without Telegram Bot.",
            token,
        )
        return None, None

    try:
        bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        dp = Dispatcher(storage=MemoryStorage())

        # Include routers in proper precedence order
        dp.include_router(admin_router)
        dp.include_router(subscription_router)
        dp.include_router(favorites_router)
        dp.include_router(search_router)
        dp.include_router(ecosystem_router)
        dp.include_router(common_router)

        return bot, dp
    except Exception as exc:
        logger.error("Failed to initialize Telegram Bot (%s). Continuing without Bot.", exc)
        return None, None


