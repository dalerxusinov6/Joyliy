"""Search and Preferences interactive configuration handlers using FSM and Inline Keyboards."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import AsyncSessionLocal
from src.models.user import User, UserSearchPreference
from src.services.listing_service import listing_service
from src.bot.states import SearchConfigState
from src.bot.keyboards import (
    get_settings_keyboard,
    get_districts_keyboard,
    get_rooms_keyboard,
    get_cancel_keyboard,
    get_main_menu_keyboard,
    TASHKENT_DISTRICTS,
)
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard
from src.bot.handlers.common import get_or_create_user

logger = logging.getLogger(__name__)
search_router = Router(name="search_router")


async def render_settings_message(user_id: int) -> tuple[str, any]:
    """Helper to generate settings text and keyboard for a user."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(UserSearchPreference)
            .join(User)
            .where(User.telegram_id == user_id)
        )
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if not pref:
            # Fallback
            pref = UserSearchPreference(user_id=1, districts=[], rooms=[])

        text = (
            "⚙️ <b>Qidiruv va Bildirishnoma Sozlamalari</b>\n\n"
            "Quyidagi tugmalar orqali o‘zingizga mos ijara parametrlarini sozlang. "
            "Yangi e'lon chiqqanda bot shu parametrlar bo‘yicha sizga darhol xabar yuboradi:"
        )
        kb = get_settings_keyboard(pref)
        return text, kb


@search_router.message(Command("search"))
@search_router.message(Command("settings"))
@search_router.message(F.text == "🔎 Kvartira qidirish")
@search_router.message(F.text == "⚙️ Sozlamalar")
async def handle_open_settings(message: Message, state: FSMContext):
    """Open settings overview."""
    await state.clear()
    async with AsyncSessionLocal() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    text, kb = await render_settings_message(message.from_user.id)
    await message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@search_router.callback_query(F.data == "nav:back_to_settings")
@search_router.callback_query(F.data == "nav:cancel")
async def handle_back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Cancel any active FSM and return to settings menu."""
    await state.clear()
    text, kb = await render_settings_message(callback.from_user.id)
    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# --- District Configuration ---

@search_router.callback_query(F.data == "cfg:district")
async def handle_open_districts(callback: CallbackQuery, state: FSMContext):
    """Open district selection keyboard."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        current_districts = list(pref.districts) if pref and pref.districts else []

    await state.set_state(SearchConfigState.selecting_district)
    await state.update_data(temp_districts=current_districts)

    kb = get_districts_keyboard(current_districts)
    await callback.message.edit_text(
        "📍 <b>Tumanlarni tanlang:</b>\nBir nechta tumanni belgilashingiz mumkin. Tugatgach «💾 Saqlash» tugmasini bosing:",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@search_router.callback_query(F.data.startswith("dist_toggle:"))
async def handle_district_toggle(callback: CallbackQuery, state: FSMContext):
    """Toggle a specific district in temporary state."""
    district_name = callback.data.split(":", 1)[1]
    data = await state.get_data()
    temp_districts = data.get("temp_districts", [])

    if district_name in temp_districts:
        temp_districts.remove(district_name)
    else:
        temp_districts.append(district_name)

    await state.update_data(temp_districts=temp_districts)
    kb = get_districts_keyboard(temp_districts)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await callback.answer()


@search_router.callback_query(F.data == "dist_action:all")
async def handle_district_all(callback: CallbackQuery, state: FSMContext):
    """Clear district filter (meaning all districts)."""
    await state.update_data(temp_districts=[])
    kb = get_districts_keyboard([])
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await callback.answer("Barcha tumanlar tanlandi.")


@search_router.callback_query(F.data == "dist_action:save")
async def handle_district_save(callback: CallbackQuery, state: FSMContext):
    """Persist chosen districts in database."""
    data = await state.get_data()
    temp_districts = data.get("temp_districts", [])

    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.districts = temp_districts
            await session.commit()

    await state.clear()
    text, kb = await render_settings_message(callback.from_user.id)
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer("Tumanlar saqlandi!")


# --- Rooms Configuration ---

@search_router.callback_query(F.data == "cfg:rooms")
async def handle_open_rooms(callback: CallbackQuery, state: FSMContext):
    """Open room count selection keyboard."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        current_rooms = list(pref.rooms) if pref and pref.rooms else []

    await state.set_state(SearchConfigState.selecting_rooms)
    await state.update_data(temp_rooms=current_rooms)

    kb = get_rooms_keyboard(current_rooms)
    await callback.message.edit_text(
        "🛏 <b>Kerakli xonalar sonini tanlang:</b>\nTugatgach «💾 Saqlash» tugmasini bosing:",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@search_router.callback_query(F.data.startswith("room_toggle:"))
async def handle_room_toggle(callback: CallbackQuery, state: FSMContext):
    """Toggle a room count."""
    room_num = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    temp_rooms = data.get("temp_rooms", [])

    if room_num in temp_rooms:
        temp_rooms.remove(room_num)
    else:
        temp_rooms.append(room_num)

    await state.update_data(temp_rooms=temp_rooms)
    kb = get_rooms_keyboard(temp_rooms)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await callback.answer()


@search_router.callback_query(F.data == "room_action:all")
async def handle_room_all(callback: CallbackQuery, state: FSMContext):
    """Clear room count filter."""
    await state.update_data(temp_rooms=[])
    kb = get_rooms_keyboard([])
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await callback.answer("Ixtiyoriy xonalar tanlandi.")


@search_router.callback_query(F.data == "room_action:save")
async def handle_room_save(callback: CallbackQuery, state: FSMContext):
    """Persist room counts in DB."""
    data = await state.get_data()
    temp_rooms = data.get("temp_rooms", [])

    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.rooms = temp_rooms
            await session.commit()

    await state.clear()
    text, kb = await render_settings_message(callback.from_user.id)
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer("Xonalar saqlandi!")


# --- Direct Toggles (Owner Mode, Notifications, Quiet Hours) ---

@search_router.callback_query(F.data == "cfg:owner_toggle")
async def handle_toggle_owner(callback: CallbackQuery):
    """Toggle owner_only flag."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.owner_only = not pref.owner_only
            await session.commit()
            msg = "Faqat egasidan (maklersiz) rejim yoqildi!" if pref.owner_only else "Barcha e'lonlar rejimi yoqildi."
            await callback.answer(msg)

    text, kb = await render_settings_message(callback.from_user.id)
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")


@search_router.callback_query(F.data == "cfg:notif_toggle")
async def handle_toggle_notif(callback: CallbackQuery):
    """Toggle notifications_enabled flag."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.notifications_enabled = not pref.notifications_enabled
            await session.commit()
            msg = "Bildirishnomalar yoqildi!" if pref.notifications_enabled else "Bildirishnomalar o‘chirildi."
            await callback.answer(msg)

    text, kb = await render_settings_message(callback.from_user.id)
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")


@search_router.callback_query(F.data == "cfg:quiet")
async def handle_toggle_quiet(callback: CallbackQuery):
    """Toggle quiet hours."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.quiet_hours_enabled = not pref.quiet_hours_enabled
            await session.commit()
            msg = f"Tinch rejim yoqildi ({pref.quiet_hours_start}-{pref.quiet_hours_end})!" if pref.quiet_hours_enabled else "Tinch rejim o‘chirildi."
            await callback.answer(msg)

    text, kb = await render_settings_message(callback.from_user.id)
    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")


# --- Price Range Input via FSM ---

@search_router.callback_query(F.data == "cfg:price")
async def handle_price_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt user for maximum monthly rent in UZS."""
    await state.set_state(SearchConfigState.waiting_max_price)
    await callback.message.edit_text(
        "💰 <b>Oylik ijara byudjetingizning eng yuqori chegarasini kiriting (so‘mda):</b>\n\n"
        "Masalan: <code>4000000</code> yoki <code>4 500 000</code>\n"
        "(Cheklovsiz bo‘lishi uchun <code>0</code> deb yozing)",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@search_router.message(SearchConfigState.waiting_max_price)
async def handle_price_input(message: Message, state: FSMContext):
    """Validate and store max price in UZS."""
    raw_text = message.text.strip().replace(" ", "").replace(",", "").replace(".", "")
    if not raw_text.isdigit():
        await message.answer(
            "⚠️ Iltimos, faqat raqam kiriting (masalan: 3500000 yoki 0):",
            reply_markup=get_cancel_keyboard(),
        )
        return

    val = int(raw_text)
    max_price = val if val > 0 else None

    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == message.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if pref:
            pref.max_price = max_price
            await session.commit()

    await state.clear()
    text, kb = await render_settings_message(message.from_user.id)
    await message.answer("✅ Narx chegarasi saqlandi!\n\n" + text, reply_markup=kb, parse_mode="HTML")


# --- Immediate Search Execution ---

@search_router.callback_query(F.data == "cfg:run_search")
async def handle_run_search(callback: CallbackQuery):
    """Run search immediately according to the user's active preferences."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserSearchPreference).join(User).where(User.telegram_id == callback.from_user.id)
        pref = (await session.execute(stmt)).scalar_one_or_none()
        if not pref:
            await callback.answer("Sozlamalar topilmadi.")
            return

        listings, total = await listing_service.search_listings(
            session=session,
            districts=pref.districts or None,
            min_price=pref.min_price,
            max_price=pref.max_price,
            rooms=pref.rooms or None,
            min_area=pref.min_area,
            max_area=pref.max_area,
            owner_only=pref.owner_only,
            include_agency=pref.include_agency,
            max_age_hours=pref.max_listing_age_hours,
            limit=5,
            offset=0,
        )

    await callback.answer()
    if not listings:
        await callback.message.answer(
            "Siz tanlagan parametrlar bo‘yicha hozircha e'lonlar topilmadi. "
            "Yangi e'lon paydo bo‘lishi bilan bot sizga xabar beradi!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await callback.message.answer(f"🔎 <b>Sizning parametrlaringiz bo‘yicha {len(listings)} ta e'lon topildi:</b>", parse_mode="HTML")
    for listing in listings:
        msg_text = format_listing_message(listing)
        kb = get_listing_inline_keyboard(listing)
        await callback.message.answer(msg_text, reply_markup=kb)

