"""Admin commands, scraper management, and monitoring controls."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.user import User, UserSearchPreference
from src.models.listing import Listing, ListingClassification
from src.models.system import SourceMonitorRun, AdminAuditLog
from src.classification.types import ClassificationLabel
from src.services.monitor_worker import monitor_worker
from src.services.notification_service import notification_service
from src.services.channel_scheduler import channel_scheduler
from src.services.queue_service import queue_service
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard, TASHKENT_TZ

logger = logging.getLogger(__name__)
admin_router = Router(name="admin_router")


def is_admin(user_id: int) -> bool:
    """Verify if user ID is in configured ADMIN_IDS."""
    return user_id in settings.ADMIN_IDS


async def log_admin_action(admin_id: int, action: str, details: dict):
    """Record administrative audit event in DB."""
    async with AsyncSessionLocal() as session:
        log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            details=details,
        )
        session.add(log)
        await session.commit()


def build_scraper_dashboard(summary: dict, total_listings: int, ch_stats: dict) -> tuple[str, InlineKeyboardMarkup]:
    """Render interactive control dashboard for Scraper & Morning ingest."""
    status_icon = "🟢" if summary["is_running"] and not summary["is_paused"] else "⏸"
    morning_icon = "🟢 Yoqilgan" if summary["morning_scrape_enabled"] else "🔴 O‘chirilgan"
    done_str = "Bajarildi ✅" if summary["morning_done_today"] else "Kutilmoqda ⏳"

    last_stats = summary.get("last_stats", {})
    last_run_str = last_stats.get("last_run") or summary.get("last_run_at") or "Hali bajarilmadi"
    last_found = last_stats.get("found", 0)
    last_new = last_stats.get("new", 0)

    text = (
        f"⚙️ <b>Joyliy Scraper & Avtomatik yuklash boshqaruvi:</b>\n\n"
        f"• Tizim holati: {status_icon} <b>{'Faol (Active)' if not summary['is_paused'] else 'To‘xtatilgan (Paused)'}</b>\n"
        f"• Ertalabki avto-yuklash: <b>{morning_icon}</b>\n"
        f"• Ertalabki belgilangan vaqt: <b>⏰ {summary['morning_scrape_time']} (Toshkent vaqti)</b>\n"
        f"• Bugungi ertalabki yuklash: <b>{done_str}</b>\n"
        f"• So‘nggi yuklash vaqti: <code>{last_run_str}</code>\n"
        f"• So‘nggi sikl yangi e'lonlari: <b>+{last_new} ta</b> ({last_found} ta tekshirildi)\n"
        f"• Saytdagi barcha faol e'lonlar: <b>{total_listings} ta</b>\n"
        f"• Ulangan kanal: <code>{ch_stats['channel'] or 'Sozlanmagan'}</code>\n"
        f"• Provayder: <code>{summary['provider']}</code>\n\n"
        f"<i>Ertalabki yuklash har kuni belgilangan soatda avtomatik ishga tushib, OLX dan yangi e'lonlarni saytga yuklaydi.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Hoziroq yangi e'lonlarni yuklash", callback_data="sc_run_now")
        ],
        [
            InlineKeyboardButton(text=f"⏰ Vaqt: {summary['morning_scrape_time']}", callback_data="sc_time_menu"),
            InlineKeyboardButton(text=f"🔔 Ertalabki: {'🟢 Yoqilgan' if summary['morning_scrape_enabled'] else '🔴 O‘chirilgan'}", callback_data="sc_toggle_morning")
        ],
        [
            InlineKeyboardButton(text="📊 Yuklash tarixi", callback_data="sc_stats"),
            InlineKeyboardButton(text="📢 Kanal zaxirasi", callback_data="sc_channel_info")
        ],
        [
            InlineKeyboardButton(text="🔄 Dashboardni yangilash", callback_data="sc_refresh")
        ]
    ])
    return text, kb


def build_time_select_keyboard() -> InlineKeyboardMarkup:
    """Quick selection buttons for morning scrape time."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="06:30", callback_data="sc_set_time_06:30"),
            InlineKeyboardButton(text="07:00", callback_data="sc_set_time_07:00"),
            InlineKeyboardButton(text="07:30", callback_data="sc_set_time_07:30"),
        ],
        [
            InlineKeyboardButton(text="08:00 (Tavsiya)", callback_data="sc_set_time_08:00"),
            InlineKeyboardButton(text="08:30", callback_data="sc_set_time_08:30"),
            InlineKeyboardButton(text="09:00", callback_data="sc_set_time_09:00"),
        ],
        [
            InlineKeyboardButton(text="09:30", callback_data="sc_set_time_09:30"),
            InlineKeyboardButton(text="10:00", callback_data="sc_set_time_10:00"),
        ],
        [
            InlineKeyboardButton(text="◀️ Boshqaruvga qaytish", callback_data="sc_refresh")
        ]
    ])


@admin_router.message(Command("admin"))
async def handle_admin_menu(message: Message):
    """Main administrative command hub."""
    if not is_admin(message.from_user.id):
        return

    text = (
        "👑 <b>Joyliy Admin Boshqaruv Markazi:</b>\n\n"
        "Quyidagi boshqaruv bo‘limlaridan birini tanlang yoki buyruqlardan foydalaning:\n\n"
        "• <code>/queue</code> — Telegram kanal e'lonlar navbati va 10 ta kunlik reja grafigi\n"
        "• <code>/channel</code> — Telegram kanal (@joyliy_uz) holati va statistika\n"
        "• <code>/scraper</code> — E'lonlarni avtomatik va ertalabki yuklash boshqaruvi\n"
        "• <code>/scrape_now</code> — Hoziroq yangi e'lonlarni yuklash\n"
        "• <code>/post_latest</code> — Kanalga navbatdagi 1 ta e'lonni chiqarish\n"
        "• <code>/admin_stats</code> — Foydalanuvchilar va platforma statistikasi\n"
        "• <code>/admin_health</code> — Server va provayder salomatligi\n"
        "• <code>/set_scrape_time 08:00</code> — Ertalabki yuklash vaqtini belgilash"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 E'lonlar Navbati (/queue)", callback_data="queue_refresh"),
            InlineKeyboardButton(text="📢 Kanal Boshqaruvi", callback_data="sc_channel_info")
        ],
        [
            InlineKeyboardButton(text="⚙️ Scraper Boshqaruvi", callback_data="sc_refresh"),
            InlineKeyboardButton(text="📊 Tizim Statistikasi", callback_data="admin_stats_menu")
        ],
        [
            InlineKeyboardButton(text="🩺 Salomatlik (Health)", callback_data="admin_health_menu")
        ]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@admin_router.message(Command("scraper"))
@admin_router.message(Command("morning"))
async def handle_scraper_dashboard_cmd(message: Message):
    """Open interactive Scraper & Morning Ingest control dashboard."""
    if not is_admin(message.from_user.id):
        return

    summary = monitor_worker.status_summary
    async with AsyncSessionLocal() as session:
        total_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar_one()
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text, kb = build_scraper_dashboard(summary, total_listings, ch_stats)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await log_admin_action(message.from_user.id, "scraper_dashboard", {})


@admin_router.callback_query(F.data == "sc_refresh")
async def handle_scraper_refresh_cb(cb: CallbackQuery):
    """Refresh the scraper dashboard."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    summary = monitor_worker.status_summary
    async with AsyncSessionLocal() as session:
        total_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar_one()
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text, kb = build_scraper_dashboard(summary, total_listings, ch_stats)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await cb.answer("Yangilandi!")


@admin_router.callback_query(F.data == "sc_toggle_morning")
async def handle_toggle_morning_cb(cb: CallbackQuery):
    """Toggle morning scrape enabled state."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    new_state = monitor_worker.toggle_morning_scrape()
    state_str = "yoqildi 🟢" if new_state else "o‘chirildi 🔴"
    await cb.answer(f"Ertalabki yuklash {state_str}!", show_alert=False)

    summary = monitor_worker.status_summary
    async with AsyncSessionLocal() as session:
        total_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar_one()
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text, kb = build_scraper_dashboard(summary, total_listings, ch_stats)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await log_admin_action(cb.from_user.id, "toggle_morning_scrape", {"enabled": new_state})


@admin_router.callback_query(F.data == "sc_time_menu")
async def handle_time_menu_cb(cb: CallbackQuery):
    """Display time selection buttons for morning scrape."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    text = (
        "⏰ <b>Ertalabki avtomatik yuklash vaqtini tanlang:</b>\n\n"
        f"Hozirgi belgilangan vaqt: <b>{monitor_worker.morning_scrape_time} (Toshkent)</b>\n\n"
        "Quyidagi vaqtlardan birini bosing yoki botga ixtiyoriy vaqtni yuboring:\n"
        "<code>/set_scrape_time 07:15</code>"
    )
    kb = build_time_select_keyboard()
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@admin_router.callback_query(F.data.startswith("sc_set_time_"))
async def handle_set_time_cb(cb: CallbackQuery):
    """Apply selected time from button."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    chosen_time = cb.data.replace("sc_set_time_", "")
    ok = monitor_worker.set_morning_scrape_time(chosen_time)
    if ok:
        await cb.answer(f"✅ Vaqt {chosen_time} qilib belgilandi!", show_alert=True)
    else:
        await cb.answer("Noto‘g‘ri vaqt formati.", show_alert=True)

    summary = monitor_worker.status_summary
    async with AsyncSessionLocal() as session:
        total_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar_one()
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text, kb = build_scraper_dashboard(summary, total_listings, ch_stats)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await log_admin_action(cb.from_user.id, "set_morning_scrape_time", {"time": chosen_time})


@admin_router.callback_query(F.data == "sc_run_now")
async def handle_run_now_cb(cb: CallbackQuery):
    """Trigger immediate deep scrape from inline button."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    await cb.answer("Yuklash boshlandi...")
    await cb.message.edit_text(
        "🔄 <b>OLX dan yangi e'lonlar yuklanmoqda...</b>\n\n"
        "• Rasmiy API va qidiruv sahifalari tahlil qilinmoqda...\n"
        "• Kvartiralar saralanmoqda va maklersiz e'lonlar tekshirilmoqda...\n"
        "<i>Iltimos, bir necha soniya kuting...</i>",
        parse_mode="HTML",
    )

    try:
        run_rec = await monitor_worker.run_once(deep=True, pages=4)
        async with AsyncSessionLocal() as session:
            total_listings = (await session.execute(
                select(func.count(Listing.id)).where(Listing.is_active == True)
            )).scalar_one()
            ch_stats = await notification_service.get_channel_posting_stats(session)

        status_text = "Muvaffaqiyatli ✅" if run_rec.status in ("SUCCESS", "OK") else run_rec.status
        note = f"\n🚀 <b>+{run_rec.listings_new}</b> ta yangi e'lon bazaga qo‘shildi!" if run_rec.listings_new > 0 else "\nℹ️ Yangi e'lonlar topilmadi (mavjud e'lonlar yangilandi)."

        res_text = (
            f"✅ <b>E'lonlarni yuklash yakunlandi!</b>\n\n"
            f"• Manba: <b>OLX Tashkent (Chuqur qidiruv)</b>\n"
            f"• Ko‘rib chiqilgan e'lonlar: <b>{run_rec.listings_found}</b> ta\n"
            f"• Saytga qo‘shilgan yangi e'lonlar: <b>+{run_rec.listings_new}</b> ta\n"
            f"• Holat: <b>{status_text}</b>\n"
            f"• Saytdagi barcha faol e'lonlar: <b>{total_listings}</b> ta\n"
            f"• Kanal zaxirasida: <b>{ch_stats['unposted_total']}</b> ta e'lon\n"
            f"{note}\n\n"
            f"<i>Barcha yangi e'lonlar saytda darhol e'lon qilindi va kanalga navbatga qo‘yildi.</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Scraper Boshqaruviga Qaytish", callback_data="sc_refresh")
            ]
        ])
        await cb.message.edit_text(res_text, reply_markup=kb, parse_mode="HTML")
        await log_admin_action(cb.from_user.id, "run_scraper_now", {"found": run_rec.listings_found, "new": run_rec.listings_new})
    except Exception as e:
        logger.error("Error in on-demand scrape: %s", e)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="sc_refresh")]
        ])
        await cb.message.edit_text(f"❌ Yuklashda xatolik yuz berdi: {e}", reply_markup=kb)


@admin_router.callback_query(F.data == "sc_stats")
async def handle_scraper_stats_cb(cb: CallbackQuery):
    """Show scraper history."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        runs = (await session.execute(
            select(SourceMonitorRun).order_by(SourceMonitorRun.started_at.desc()).limit(5)
        )).scalars().all()

    lines = []
    for r in runs:
        t_str = r.started_at.astimezone(TASHKENT_TZ).strftime("%d.%m %H:%M")
        status_s = "✅" if r.status in ("SUCCESS", "OK") else "⚠️"
        lines.append(f"• <b>{t_str}</b>: {status_s} {r.listings_found} ta tekshirildi, <b>+{r.listings_new}</b> yangi")

    history_str = "\n".join(lines) if lines else "Tarix mavjud emas."
    text = (
        f"📊 <b>So‘nggi yuklashlar tarixi:</b>\n\n"
        f"{history_str}\n\n"
        f"<i>Tizim har kuni ertalab soat {monitor_worker.morning_scrape_time} da va kun davomida davriy ravishda tekshiruv olib boradi.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Boshqaruvga qaytish", callback_data="sc_refresh")]
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@admin_router.callback_query(F.data == "sc_channel_info")
async def handle_channel_info_cb(cb: CallbackQuery):
    """Show channel broadcast info from button."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        stats = await notification_service.get_channel_posting_stats(session)

    quiet_str = "Sokin vaqt (tunda yuborilmaydi)" if stats["is_quiet_hours"] else "Faol vaqt (e'lonlar uzatilmoqda)"
    text = (
        f"📢 <b>Telegram Kanal Holati:</b>\n\n"
        f"• Ulangan kanal: <code>{stats['channel'] or 'Sozlanmagan'}</code>\n"
        f"• Bugun kanalga chiqdi: <b>{stats['posted_today']} / {stats['daily_limit']}</b> ta\n"
        f"• Qolgan kunlik limit: <b>{stats['remaining_today']}</b> ta\n"
        f"• Kanal navbatidagi e'lonlar: <b>{stats['unposted_total']}</b> ta\n"
        f"• Rejim: <b>Kun bo‘yi bo‘lib-bo‘lib (har 10 daqiqada 1 tadan)</b>\n"
        f"• Hozirgi holat: <b>{quiet_str}</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Kanalga 1 ta e'lon chiqarish", callback_data="admin_post_one_now")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="sc_refresh")]
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@admin_router.callback_query(F.data == "admin_post_one_now")
async def handle_admin_post_one_cb(cb: CallbackQuery):
    """Post one listing to channel immediately from button."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    channel = settings.CHANNEL_ID
    if not channel:
        await cb.answer("Kanal sozlanmagan!", show_alert=True)
        return

    await cb.answer("Yuborilmoqda...")
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Listing)
            .options(selectinload(Listing.classification))
            .where(
                Listing.is_active == True,
                Listing.posted_to_channel_at.is_(None),
            )
            .order_by(
                Listing.publication_date.desc().nullslast(),
                Listing.id.desc(),
            )
            .limit(10)
        )
        res = await session.execute(stmt)
        candidates = res.scalars().all()

        target_listing = None
        for it in candidates:
            if not await notification_service.is_channel_duplicate(session, it):
                target_listing = it
                break
            else:
                it.posted_to_channel_at = datetime.now(timezone.utc)
                it.is_active = False
                session.add(it)
                await session.commit()

        if target_listing:
            ok = await notification_service.send_to_channel(target_listing, channel_id=channel, session=session)
            if ok:
                await cb.message.answer(
                    f"✅ <b>{target_listing.title}</b> kanalda muvaffaqiyatli e'lon qilindi!",
                    parse_mode="HTML"
                )
            else:
                await cb.message.answer("❌ Kanalga yuborishda xatolik yuz berdi.")
        else:
            await cb.message.answer("ℹ️ Kanalga yuborilmagan yangi e'lon qolmadi. Avval /scrape_now orqali yangilang.")

    # Refresh dashboard
    summary = monitor_worker.status_summary
    async with AsyncSessionLocal() as session:
        total_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar_one()
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text, kb = build_scraper_dashboard(summary, total_listings, ch_stats)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass


@admin_router.message(Command("set_scrape_time"))
async def handle_set_scrape_time_cmd(message: Message):
    """Set morning scrape time via slash command."""
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "Iltimos, vaqtni <code>HH:MM</code> formatida kiriting.\n"
            "Masalan: <code>/set_scrape_time 08:00</code> yoki <code>/set_scrape_time 07:30</code>",
            parse_mode="HTML"
        )
        return

    time_val = parts[1].strip()
    ok = monitor_worker.set_morning_scrape_time(time_val)
    if ok:
        await message.answer(
            f"✅ <b>Ertalabki avtomatik yuklash vaqti o‘rnatildi: {time_val} (Toshkent vaqti)</b>\n\n"
            f"Tizim har kuni soat <b>{time_val}</b> da yangi e'lonlarni yuklab saytga joylaydi.",
            parse_mode="HTML"
        )
        await log_admin_action(message.from_user.id, "set_scrape_time", {"time": time_val})
    else:
        await message.answer(
            "❌ Noto‘g‘ri vaqt formati. Iltimos, <code>00:00</code> dan <code>23:59</code> gacha bo‘lgan vaqt kiriting.\n"
            "Masalan: <code>/set_scrape_time 08:00</code>",
            parse_mode="HTML"
        )


@admin_router.message(Command("morning_scrape"))
async def handle_morning_scrape_toggle_cmd(message: Message):
    """Enable or disable morning scrape."""
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip().lower()
        if arg in ("on", "1", "ha", "true", "yoqish"):
            monitor_worker.toggle_morning_scrape(True)
        elif arg in ("off", "0", "yoq", "false", "ochirish"):
            monitor_worker.toggle_morning_scrape(False)

    state_str = "yoqilgan 🟢" if monitor_worker.morning_scrape_enabled else "o‘chirilgan 🔴"
    await message.answer(
        f"Ertalabki avto-yuklash holati: <b>{state_str}</b>\n"
        f"Vaqti: <b>{monitor_worker.morning_scrape_time}</b>\n\n"
        "O‘zgartirish uchun: <code>/morning_scrape on</code> yoki <code>/morning_scrape off</code>",
        parse_mode="HTML"
    )


@admin_router.message(Command("scrape"))
@admin_router.message(Command("scrape_now"))
async def handle_scrape_now(message: Message):
    """Manually trigger immediate OLX scrape and channel broadcast."""
    if not is_admin(message.from_user.id):
        return
    status_msg = await message.answer("🔄 OLX dan yangi e'lonlar qidirilmoqda va sayt yangilanmoqda...")
    try:
        run_rec = await monitor_worker.run_once(deep=True, pages=4)

        async with AsyncSessionLocal() as session:
            stats = await notification_service.get_channel_posting_stats(session)
            total_listings = (await session.execute(
                select(func.count(Listing.id)).where(Listing.is_active == True)
            )).scalar_one()

        status_text = "Faol / Ishlamoqda" if run_rec.status in ("SUCCESS", "OK") else run_rec.status
        note = ""
        if run_rec.listings_new > 0:
            note = f"\n\n🚀 <b>+{run_rec.listings_new}</b> ta yangi e'lon saytga qo‘shildi!"

        await status_msg.edit_text(
            f"✅ <b>Yangi e'lonlar muvaffaqiyatli yuklandi!</b>\n\n"
            f"• Manba: <b>OLX Uzbekistan</b>\n"
            f"• Tekshirilgan e'lonlar: <b>{run_rec.listings_found}</b> ta\n"
            f"• Yangi topilgan: <b>+{run_rec.listings_new}</b> ta\n"
            f"• Holat: <b>{status_text}</b>\n"
            f"• Saytdagi barcha faol e'lonlar: <b>{total_listings}</b> ta\n"
            f"• Ulangan kanal: <code>{settings.CHANNEL_ID or 'Sozlanmagan'}</code>\n"
            f"• Bugun kanalga yuborildi: <b>{stats['posted_today']} / {stats['daily_limit']}</b> ta\n"
            f"• Navbatdagi zaxira e'lonlar: <b>{stats['unposted_total']}</b> ta\n"
            f"• Taqsimot: <b>Kuniga 100 tagacha bo‘lib-bo‘lib (har 10 daqiqada 1 tadan)</b>"
            f"{note}",
            parse_mode="HTML",
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


@admin_router.message(Command("admin_stats"))
async def handle_admin_stats(message: Message):
    """Display user and listing metrics."""
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar_one()
        active_users = (await session.execute(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )).scalar_one()

        total_listings = (await session.execute(select(func.count(Listing.id)))).scalar_one()

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_listings = (await session.execute(
            select(func.count(Listing.id)).where(Listing.first_seen_at >= today_start)
        )).scalar_one()

        owner_listings = (await session.execute(
            select(func.count(ListingClassification.id)).where(
                ListingClassification.label == ClassificationLabel.LIKELY_OWNER.value
            )
        )).scalar_one()

    text = (
        "📊 <b>Admin Statistikasi:</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🟢 Faol foydalanuvchilar: <b>{active_users}</b>\n\n"
        f"🏠 Jami e'lonlar: <b>{total_listings}</b>\n"
        f"🆕 Bugungi yangi e'lonlar: <b>{today_listings}</b>\n"
        f"🔑 Maklersiz (Egasi deb topilgan): <b>{owner_listings}</b>"
    )
    await message.answer(text=text, parse_mode="HTML")
    await log_admin_action(message.from_user.id, "admin_stats", {})


@admin_router.callback_query(F.data == "admin_stats_menu")
async def handle_admin_stats_menu_cb(cb: CallbackQuery):
    """Show admin stats via callback query."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar_one()
        active_users = (await session.execute(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )).scalar_one()
        total_listings = (await session.execute(select(func.count(Listing.id)))).scalar_one()
        owner_listings = (await session.execute(
            select(func.count(ListingClassification.id)).where(
                ListingClassification.label == ClassificationLabel.LIKELY_OWNER.value
            )
        )).scalar_one()

    text = (
        "📊 <b>Platforma Statistikasi:</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🟢 Faol foydalanuvchilar: <b>{active_users}</b>\n\n"
        f"🏠 Saytdagi jami e'lonlar: <b>{total_listings}</b>\n"
        f"🔑 Maklersiz (Uy egasidan): <b>{owner_listings}</b>\n\n"
        f"<i>Barcha e'lonlar bevosita Joyliy saytida aks etadi.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Boshqaruvga qaytish", callback_data="sc_refresh")]
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@admin_router.message(Command("admin_health"))
async def handle_admin_health(message: Message):
    """Check health of monitor, provider, and database."""
    if not is_admin(message.from_user.id):
        return

    status_info = monitor_worker.status_summary
    health = await monitor_worker.provider.check_health()

    status_icon = "🟢" if health.status.value == "HEALTHY" else ("🟡" if "DEGRADED" in health.status.value else "🔴")

    async with AsyncSessionLocal() as session:
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text = (
        "🩺 <b>Tizim Salomatligi (Health Check):</b>\n\n"
        f"• Monitor holati: {'To‘xtatilgan (PAUSED)' if status_info['is_paused'] else 'Ishlamoqda (ACTIVE)'}\n"
        f"• Ishlayotgan provayder: <code>{status_info['provider']}</code>\n"
        f"• Provayder holati: {status_icon} <b>{health.status.value}</b>\n"
        f"• Xabar: {health.message}\n"
        f"• Ertalabki avto-yuklash: <b>{'🟢 Yoqilgan' if status_info['morning_scrape_enabled'] else '🔴 O‘chirilgan'}</b>\n"
        f"• Ertalabki vaqt: <b>{status_info['morning_scrape_time']}</b>\n"
        f"• Ulangan kanal: <code>{ch_stats['channel'] or 'Sozlanmagan'}</code>\n"
        f"• Bugun kanalga yuborildi: <b>{ch_stats['posted_today']} / {ch_stats['daily_limit']}</b> ta\n"
        f"• Navbatdagi yangi e'lonlar: <b>{ch_stats['unposted_total']}</b> ta\n"
        f"• So‘nggi muvaffaqiyatli sikl: {status_info['last_run_at'] or 'Hali ishga tushmadi'}\n"
        f"• Ketma-ket xatoliklar: {status_info['consecutive_failures']}\n"
        f"• Intervall: {status_info['poll_interval_seconds']} soniya"
    )
    await message.answer(text=text, parse_mode="HTML")


@admin_router.callback_query(F.data == "admin_health_menu")
async def handle_admin_health_menu_cb(cb: CallbackQuery):
    """Show health info via callback."""
    if not is_admin(cb.from_user.id):
        await cb.answer("Ruxsat berilmagan.", show_alert=True)
        return

    status_info = monitor_worker.status_summary
    health = await monitor_worker.provider.check_health()
    status_icon = "🟢" if health.status.value == "HEALTHY" else ("🟡" if "DEGRADED" in health.status.value else "🔴")

    text = (
        "🩺 <b>Tizim Salomatligi:</b>\n\n"
        f"• Monitor: {'To‘xtatilgan' if status_info['is_paused'] else 'Ishlamoqda 🟢'}\n"
        f"• Provayder: {status_icon} <b>{health.status.value}</b> (<code>{status_info['provider']}</code>)\n"
        f"• Xabar: {health.message}\n"
        f"• Ertalabki yuklash: <b>{'🟢 ' + status_info['morning_scrape_time'] if status_info['morning_scrape_enabled'] else '🔴 O‘chirilgan'}</b>\n"
        f"• Xatoliklar soni: {status_info['consecutive_failures']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Boshqaruvga qaytish", callback_data="sc_refresh")]
    ])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@admin_router.message(Command("admin_test"))
async def handle_admin_test(message: Message):
    """Send a preview test notification to verify layout and button callback handling."""
    if not is_admin(message.from_user.id):
        return

    test_listing = Listing(
        id=99999,
        source="olx_uz",
        canonical_url="https://www.olx.uz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/",
        title="Chilonzor 7-kvartal 2 xonali kvartira — Sinov xabari",
        price_uzs=3500000,
        district="Chilonzor",
        rooms=2,
        area=54.0,
        first_seen_at=datetime.now(timezone.utc),
        classification=ListingClassification(
            label=ClassificationLabel.LIKELY_OWNER.value,
            confidence_score=0.85,
        ),
    )

    msg_text = format_listing_message(test_listing)
    kb = get_listing_inline_keyboard(test_listing)

    await message.answer("🧪 <b>Test Bildirishnoma Ko‘rinishi:</b>", parse_mode="HTML")
    await message.answer(text=msg_text, reply_markup=kb)


@admin_router.message(Command("admin_sources"))
async def handle_admin_sources(message: Message):
    """Display configured data sources and URLs."""
    if not is_admin(message.from_user.id):
        return

    urls = "\n".join([f"• <code>{u}</code>" for u in settings.OLX_SEARCH_URLS])
    text = (
        "🌐 <b>Sozlangan Manbalar:</b>\n\n"
        f"Provayder turi: <b>{settings.PROVIDER_TYPE}</b>\n"
        f"So‘rov oralig‘i: <b>{settings.POLL_INTERVAL_SECONDS}s</b>\n"
        f"Ertalabki yuklash vaqti: <b>{settings.MORNING_SCRAPE_TIME}</b>\n\n"
        f"<b>Kuzatilayotgan havolalar:</b>\n{urls}"
    )
    await message.answer(text=text, parse_mode="HTML")


@admin_router.message(Command("admin_review"))
async def handle_admin_review(message: Message):
    """Inspect listings marked as NEEDS_REVIEW."""
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        stmt = (
            select(Listing)
            .join(ListingClassification)
            .where(ListingClassification.label == ClassificationLabel.NEEDS_REVIEW.value)
            .order_by(Listing.first_seen_at.desc())
            .limit(3)
        )
        res = await session.execute(stmt)
        listings = res.scalars().all()

    if not listings:
        await message.answer("Ko‘rib chiqish talab qilinadigan noaniq e'lonlar mavjud emas.")
        return

    await message.answer(f"🔍 <b>Noaniq deb topilgan {len(listings)} ta e'lon:</b>", parse_mode="HTML")
    for l in listings:
        msg = format_listing_message(l)
        kb = get_listing_inline_keyboard(l)
        await message.answer(msg, reply_markup=kb)


@admin_router.message(Command("admin_pause"))
async def handle_admin_pause(message: Message):
    """Pause monitor worker."""
    if not is_admin(message.from_user.id):
        return
    monitor_worker.pause()
    await message.answer("⏸ Monitoring vaqtincha to‘xtatildi.")
    await log_admin_action(message.from_user.id, "admin_pause", {})


@admin_router.message(Command("admin_resume"))
async def handle_admin_resume(message: Message):
    """Resume monitor worker."""
    if not is_admin(message.from_user.id):
        return
    monitor_worker.resume()
    await message.answer("▶️ Monitoring qayta faollashtirildi.")
    await log_admin_action(message.from_user.id, "admin_resume", {})


@admin_router.message(Command("set_channel"))
async def handle_set_channel(message: Message):
    """Set or update target Telegram channel for new listing broadcasts."""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "Iltimos, kanal username yoki ID sini kiriting.\n"
            "Masalan: <code>/set_channel @joyliy_kanal</code> yoki <code>/set_channel -1001234567890</code>",
            parse_mode="HTML",
        )
        return

    new_channel = parts[1].strip()
    settings.CHANNEL_ID = new_channel
    await message.answer(
        f"✅ Telegram kanali muvaffaqiyatli o‘rnatildi: <b>{new_channel}</b>\n\n"
        "Endi OLX dan yangi aniqlangan har bir e'lon rasmlari bilan ushbu kanalga yuboriladi.\n"
        "Eslatma: Bot ushbu kanalda administrator bo‘lishi va xabar yuborish huquqiga ega bo‘lishi kerak.",
        parse_mode="HTML",
    )
    await log_admin_action(message.from_user.id, "set_channel", {"channel_id": new_channel})


@admin_router.message(Command("queue"))
async def handle_admin_queue(message: Message):
    """Display persistent publishing queue status and today's 10 schedule slots."""
    if not is_admin(message.from_user.id):
        return

    status = await channel_scheduler.get_schedule_status()
    q = status["queue"]

    slot_lines = []
    for sl in status["slots"]:
        st = sl["status"]
        if st == "published":
            icon = "✅"
        elif st == "skipped":
            icon = "⏭"
        elif st == "missed":
            icon = "⚠️"
        elif st == "publishing":
            icon = "🔄"
        elif st == "due":
            icon = "⏳"
        else:
            icon = "⚪️"
        slot_lines.append(f"{icon} <code>{sl['time']}</code> — {st}")

    slots_formatted = "\n".join(slot_lines)

    text = (
        f"📋 <b>Telegram Kanal E'lonlar Navbati (Queue & Schedule):</b>\n\n"
        f"• Toshkent vaqti: <b>⏰ {status['tashkent_time']}</b>\n"
        f"• Nashr oraliq oynasi: <b>08:00 – 20:00</b> ({'🟢 Ochiq' if status['is_within_window'] else '🔴 Yopiq'})\n"
        f"• Bugun chop etilgan: <b>{status['published_today']} / {status['total_slots']} ta</b>\n"
        f"• Navbatdagi reja sloti: <b>{status['next_slot']}</b>\n\n"
        f"📦 <b>Doimiy navbat holati (Persistent DB Queue):</b>\n"
        f"• Kutilmoqda (Pending): <b>{q.get('pending', 0)} ta</b>\n"
        f"• Jarayonda (Publishing): <b>{q.get('publishing', 0)} ta</b>\n"
        f"• Kanalga chiqqan (Published): <b>{q.get('published', 0)} ta</b>\n"
        f"• Rad etilgan (Duplicate): <b>{q.get('rejected', 0)} ta</b>\n"
        f"• Xato bergan (Failed): <b>{q.get('failed', 0)} ta</b>\n\n"
        f"📅 <b>Bugungi 10 ta reja grafigi:</b>\n"
        f"{slots_formatted}\n\n"
        f"<i>Kanalga har bir slotda faqat 1 ta eng yangi va noyob e'lon chiqadi. Dublikatlar qat'iyan taqiqlangan.</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Navbatni yangilash", callback_data="queue_refresh"),
            InlineKeyboardButton(text="📤 Keyingisini chiqarish", callback_data="queue_publish_next"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Scraper Boshqaruvi", callback_data="sc_refresh"),
        ]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@admin_router.callback_query(F.data == "queue_refresh")
async def handle_queue_refresh(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    status = await channel_scheduler.get_schedule_status()
    q = status["queue"]
    slot_lines = []
    for sl in status["slots"]:
        st = sl["status"]
        icon = "✅" if st == "published" else ("⏭" if st == "skipped" else ("⚠️" if st == "missed" else ("🔄" if st == "publishing" else ("⏳" if st == "due" else "⚪️"))))
        slot_lines.append(f"{icon} <code>{sl['time']}</code> — {st}")
    slots_formatted = "\n".join(slot_lines)

    text = (
        f"📋 <b>Telegram Kanal E'lonlar Navbati (Queue & Schedule):</b>\n\n"
        f"• Toshkent vaqti: <b>⏰ {status['tashkent_time']}</b>\n"
        f"• Nashr oraliq oynasi: <b>08:00 – 20:00</b> ({'🟢 Ochiq' if status['is_within_window'] else '🔴 Yopiq'})\n"
        f"• Bugun chop etilgan: <b>{status['published_today']} / {status['total_slots']} ta</b>\n"
        f"• Navbatdagi reja sloti: <b>{status['next_slot']}</b>\n\n"
        f"📦 <b>Doimiy navbat holati (Persistent DB Queue):</b>\n"
        f"• Kutilmoqda (Pending): <b>{q.get('pending', 0)} ta</b>\n"
        f"• Jarayonda (Publishing): <b>{q.get('publishing', 0)} ta</b>\n"
        f"• Kanalga chiqqan (Published): <b>{q.get('published', 0)} ta</b>\n"
        f"• Rad etilgan (Duplicate): <b>{q.get('rejected', 0)} ta</b>\n"
        f"• Xato bergan (Failed): <b>{q.get('failed', 0)} ta</b>\n\n"
        f"📅 <b>Bugungi 10 ta reja grafigi:</b>\n"
        f"{slots_formatted}\n\n"
        f"<i>Kanalga har bir slotda faqat 1 ta eng yangi va noyob e'lon chiqadi. Dublikatlar qat'iyan taqiqlangan.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Navbatni yangilash", callback_data="queue_refresh"),
            InlineKeyboardButton(text="📤 Keyingisini chiqarish", callback_data="queue_publish_next"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Scraper Boshqaruvi", callback_data="sc_refresh"),
        ]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer("Navbat yangilandi.")


@admin_router.callback_query(F.data == "queue_publish_next")
async def handle_queue_publish_next(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
    await callback.answer("Keyingi e'lon chop etilmoqda...")
    now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
    today_str = now_tash.strftime("%Y-%m-%d")
    res = await channel_scheduler.execute_slot(today_str, "manual", force=True)
    if res.get("status") == "published":
        await callback.message.answer(
            f"✅ <b>Yangi e'lon kanalga muvaffaqiyatli chiqarildi!</b>\n"
            f"Listing ID: #{res.get('listing_id')} | Msg ID: {res.get('telegram_message_id')}",
            parse_mode="HTML"
        )
    elif res.get("status") == "skipped":
        await callback.message.answer("ℹ️ <b>Navbatda yangi e'lon yo‘q.</b> Barcha e'lonlar allaqachon chiqarilgan.", parse_mode="HTML")
    else:
        await callback.message.answer(f"⚠️ Natija: {res.get('status')} - {res.get('error', '')}", parse_mode="HTML")


@admin_router.message(Command("channel_status"))
@admin_router.message(Command("channel"))
async def handle_channel_status(message: Message):
    """View channel broadcast status, today's count, and queue size."""
    if not is_admin(message.from_user.id):
        return

    sched_status = await channel_scheduler.get_schedule_status()
    channel_name = settings.CHANNEL_ID or "Sozlanmagan"
    quiet_str = "Faol vaqt (08:00 – 20:00)" if sched_status["is_within_window"] else "Sokin vaqt (tunda yuborilmaydi)"

    text = (
        f"📢 <b>Kanalga e'lon uzatish tizimi (@joyliy_uz):</b>\n\n"
        f"• Ulangan kanal: <code>{channel_name}</code>\n"
        f"• Bugun e'lon qilingan: <b>{sched_status['published_today']} / {sched_status['total_slots']} ta</b>\n"
        f"• Navbatdagi vaqt sloti: <b>⏰ {sched_status['next_slot']}</b>\n"
        f"• Nashr oynasi: <b>08:00 – 20:00 (12 soat davomida teng 10 ta post)</b>\n"
        f"• Hozirgi holat: <b>{quiet_str}</b>\n"
        f"• Navbatdagi kutilayotgan e'lonlar: <b>{sched_status['queue'].get('pending', 0)} ta</b>\n\n"
        f"<b>Buyruqlar:</b>\n"
        f"• <code>/queue</code> — E'lonlar navbati va bugungi 10 ta reja grafigi\n"
        f"• <code>/post_latest</code> — Navbatdagi 1 ta e'lonni hoziroq chiqarish\n"
        f"• <code>/scrape_now</code> — Internetdan yangi e'lonlarni yuklash\n"
        f"• <code>/set_channel @kanal_nomi</code> — Kanal nomini o‘zgartirish"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 E'lonlar Navbati (/queue)", callback_data="queue_refresh"),
            InlineKeyboardButton(text="📤 1 ta chiqarish", callback_data="queue_publish_next"),
        ]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@admin_router.message(Command("post_latest"))
async def handle_post_latest(message: Message):
    """Post next eligible unposted, unique listing from queue to configured channel."""
    if not is_admin(message.from_user.id):
        return
    channel = settings.CHANNEL_ID
    if not channel:
        await message.answer("⚠️ Avval <code>/set_channel @kanal_nomi</code> buyrug‘i orqali kanalni sozlang.", parse_mode="HTML")
        return

    status_msg = await message.answer(f"📤 Navbatdagi yangi e'lon <code>{channel}</code> kanaliga tayyorlanmoqda...", parse_mode="HTML")

    now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
    today_str = now_tash.strftime("%Y-%m-%d")
    res = await channel_scheduler.execute_slot(today_str, "manual", force=True)

    if res.get("status") == "published":
        await status_msg.edit_text(
            f"✅ <b>E'lon #{res.get('listing_id')} muvaffaqiyatli kanalga joylandi!</b>\n"
            f"Kanal: {channel}\nTelegram Message ID: <code>{res.get('telegram_message_id')}</code>",
            parse_mode="HTML"
        )
    elif res.get("status") == "skipped":
        await status_msg.edit_text(
            f"ℹ️ <b>Bazada kanalga yuborilmagan yangi e'lon qolmadi.</b>\n\n"
            f"Barcha e'lonlar allaqachon kanalga chiqqan yoki dublikat sifatida filtrlangan. Yangi e'lonlarni yuklash uchun <code>/scrape_now</code> buyrug‘ini bosing.",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text(
            f"⚠️ <b>Chiqarishda xatolik yuz berdi:</b>\n<code>{res.get('error', 'Nomaʼlum xato')}</code>",
            parse_mode="HTML"
        )
