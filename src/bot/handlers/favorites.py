"""Favorites and listing action callbacks."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.user import User
from src.services.listing_service import listing_service
from src.bot.i18n import get_text
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard
from src.bot.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)
favorites_router = Router(name="favorites_router")


@favorites_router.message(Command("favorites"))
@favorites_router.message(F.text == "❤️ Saqlanganlar")
async def handle_list_favorites(message: Message):
    """Display user's saved listings."""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            await message.answer(get_text("no_favorites"))
            return

        favorites = await listing_service.get_user_favorites(
            session=session, user_id=user.id, limit=10
        )

    if not favorites:
        await message.answer(
            text=get_text("no_favorites"),
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(f"❤️ <b>Saqlangan e'lonlaringiz ({len(favorites)} ta):</b>", parse_mode="HTML")
    for listing in favorites:
        msg_text = format_listing_message(listing)
        kb = get_listing_inline_keyboard(listing, is_favorited=True)
        await message.answer(text=msg_text, reply_markup=kb)


@favorites_router.callback_query(F.data.startswith("fav:"))
async def handle_add_favorite(callback: CallbackQuery):
    """Add listing to user's favorites."""
    listing_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == callback.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return

        added = await listing_service.add_favorite(session, user_id=user.id, listing_id=listing_id)
        listing = await listing_service.get_listing_by_id(session, listing_id)

    if added:
        await callback.answer(get_text("saved_to_favorites"))
    else:
        await callback.answer("Bu e'lon avval saqlangan.")

    if listing:
        kb = get_listing_inline_keyboard(listing, is_favorited=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=kb)
        except Exception:
            pass


@favorites_router.callback_query(F.data.startswith("unfav:"))
async def handle_remove_favorite(callback: CallbackQuery):
    """Remove listing from user's favorites."""
    listing_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == callback.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return

        removed = await listing_service.remove_favorite(session, user_id=user.id, listing_id=listing_id)
        listing = await listing_service.get_listing_by_id(session, listing_id)

    if removed:
        await callback.answer(get_text("removed_from_favorites"))
    else:
        await callback.answer("E'lon topilmadi.")

    if listing:
        kb = get_listing_inline_keyboard(listing, is_favorited=False)
        try:
            await callback.message.edit_reply_markup(reply_markup=kb)
        except Exception:
            pass


@favorites_router.callback_query(F.data.startswith("hide:"))
async def handle_hide_listing(callback: CallbackQuery):
    """Hide/delete the listing message from user chat view."""
    try:
        await callback.message.delete()
        await callback.answer(get_text("hidden_listing"))
    except Exception:
        await callback.answer("E'lon o‘chirildi.")

