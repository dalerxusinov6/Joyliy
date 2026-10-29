"""Common command and main menu handlers."""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.user import User, UserSearchPreference
from src.models.listing import Listing
from src.services.listing_service import listing_service
from src.services.auth_service import auth_service
from src.bot.i18n import get_text
from src.bot.keyboards import get_main_menu_keyboard, get_settings_keyboard
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard

logger = logging.getLogger(__name__)
common_router = Router(name="common_router")


async def get_or_create_user(session, telegram_id: int, username: str | None, first_name: str | None) -> User:
    """Ensure user and their default search preferences exist in DB."""
    stmt = (
        select(User)
        .options(selectinload(User.preference))
        .where(User.telegram_id == telegram_id)
    )
    user = (await session.execute(stmt)).scalar_one_or_none()
    if not user:
        is_admin = telegram_id in settings.ADMIN_IDS
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
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
    return user


@common_router.message(CommandStart())
async def handle_start(message: Message, command: CommandObject = None):
    """Handle /start command: web auth deep-link or main welcome."""
    args = command.args if command else None

    # Check if this is a web login deep-link (e.g. /start auth_3f92b...)
    if args and args.startswith("auth_"):
        session_id = args[5:]
        async with AsyncSessionLocal() as session:
            photo_url = None
            try:
                photos = await message.bot.get_user_profile_photos(
                    user_id=message.from_user.id, limit=1
                )
                if photos.total_count > 0:
                    file_id = photos.photos[0][-1].file_id
                    file_info = await message.bot.get_file(file_id)
                    photo_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_info.file_path}"
            except Exception as e:
                logger.debug("Could not retrieve profile photo: %s", e)

            success, user = await auth_service.confirm_auth_session(
                session=session,
                session_id=session_id,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                photo_url=photo_url,
            )

        if success:
            site_url = settings.WEBSITE_URL
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🌐 Joyliy saytiga qaytish", url=site_url
                        )
                    ]
                ]
            )
            await message.answer(
                f"🎉 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
                f"<b>Joyliy</b> veb-saytiga kirishingiz muvaffaqiyatli tasdiqlandi! ✅\n\n"
                f"Brauzeringizdagi sahifaga qaytib, saytdan foydalanishda davom etishingiz mumkin.",
                reply_markup=kb,
                parse_mode="HTML",
            )
            return
        else:
            await message.answer(
                "⚠️ <b>Kirish sessiyasi muddati o‘tgan yoki topilmadi.</b>\n\n"
                "Iltimos, Joyliy saytiga qaytib qaytadan 'Telegram orqali kirish' tugmasini bosing.",
                parse_mode="HTML",
            )
            return

    # Regular /start without deep-link
    async with AsyncSessionLocal() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    await message.answer(
        text=get_text("welcome"),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@common_router.message(Command("help"))
async def handle_help(message: Message):
    """Handle /help command: usage guide."""
    await message.answer(
        text=get_text("help"),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@common_router.message(Command("privacy"))
async def handle_privacy(message: Message):
    """Handle /privacy command: explain user data retention."""
    await message.answer(
        text=get_text("privacy"),
        parse_mode="HTML",
    )


@common_router.message(F.text == "🆕 Yangi e'lonlar")
async def handle_latest_listings(message: Message):
    """Display the most recent apartment rental listings."""
    async with AsyncSessionLocal() as session:
        listings, total = await listing_service.search_listings(
            session=session,
            limit=5,
            offset=0,
        )

    if not listings:
        await message.answer(
            "Hozircha bazada yangi e'lonlar yo‘q. Monitor yangi e'lonlarni tekshirmoqda...",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(f"🆕 <b>Toshkentdagi so‘nggi {len(listings)} ta e'lon:</b>", parse_mode="HTML")
    for listing in listings:
        msg_text = format_listing_message(listing)
        kb = get_listing_inline_keyboard(listing)
        await message.answer(msg_text, reply_markup=kb)


@common_router.message(F.text == "🏠 Maklersiz kvartiralar")
async def handle_maklersiz_listings(message: Message):
    """Display latest listings classified as LIKELY_OWNER."""
    async with AsyncSessionLocal() as session:
        listings, total = await listing_service.search_listings(
            session=session,
            owner_only=True,
            limit=5,
            offset=0,
        )

    if not listings:
        await message.answer(
            "Hozircha egasidan deb belgilangan yangi e'lonlar topilmadi. Tez orada yangilanadi!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(f"🏠 <b>Egasidan bo‘lishi mumkin bo‘lgan {len(listings)} ta e'lon:</b>", parse_mode="HTML")
    for listing in listings:
        msg_text = format_listing_message(listing)
        kb = get_listing_inline_keyboard(listing)
        await message.answer(msg_text, reply_markup=kb)

