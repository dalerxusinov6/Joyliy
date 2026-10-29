"""Subscription and notification toggle handlers."""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.user import User, UserSearchPreference
from src.bot.i18n import get_text
from src.bot.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)
subscription_router = Router(name="subscription_router")


@subscription_router.message(Command("stop"))
async def handle_stop_notifications(message: Message):
    """Pause new listing notifications."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(UserSearchPreference)
            .join(User)
            .where(User.telegram_id == message.from_user.id)
        )
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.notifications_enabled = False
            await session.commit()

    await message.answer(
        text=get_text("stop_success"),
        reply_markup=get_main_menu_keyboard(),
    )


@subscription_router.message(Command("resume"))
async def handle_resume_notifications(message: Message):
    """Resume new listing notifications."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(UserSearchPreference)
            .join(User)
            .where(User.telegram_id == message.from_user.id)
        )
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.notifications_enabled = True
            await session.commit()

    await message.answer(
        text=get_text("resume_success"),
        reply_markup=get_main_menu_keyboard(),
    )


@subscription_router.message(Command("subscription"))
async def handle_subscription_info(message: Message):
    """Show current subscription status and configuration."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(UserSearchPreference)
            .join(User)
            .where(User.telegram_id == message.from_user.id)
        )
        pref = (await session.execute(stmt)).scalar_one_or_none()

    if not pref:
        await message.answer("Siz hali ro‘yxatdan o‘tmagansiz. /start buyrug‘ini bosing.")
        return

    status_str = "🟢 Faol" if pref.notifications_enabled else "🔴 To‘xtatilgan (/resume)"
    owner_str = "Faqat egasidan" if pref.owner_only else "Barcha e'lonlar"
    dist_str = ", ".join(pref.districts) if pref.districts else "Barcha tumanlar"

    text = (
        "📋 <b>Obuna va Bildirishnoma holati:</b>\n\n"
        f"• Holat: {status_str}\n"
        f"• Tanlangan tumanlar: {dist_str}\n"
        f"• E'lonlar turi: {owner_str}\n"
        f"• Tinch rejim (Quiet hours): {'Yoqilgan (' + pref.quiet_hours_start + '-' + pref.quiet_hours_end + ')' if pref.quiet_hours_enabled else 'O‘chirilgan'}\n\n"
        "Sozlamalarni o‘zgartirish uchun /settings buyrug‘idan foydalaning."
    )
    await message.answer(text=text, parse_mode="HTML")

