"""Telegram Bot and Dispatcher setup."""

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


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Factory to initialize aiogram Bot and register all routers."""
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers in proper precedence order
    dp.include_router(admin_router)
    dp.include_router(subscription_router)
    dp.include_router(favorites_router)
    dp.include_router(search_router)
    dp.include_router(common_router)

    return bot, dp

