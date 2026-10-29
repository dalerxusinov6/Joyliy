"""Admin commands and monitoring controls."""

import logging
from datetime import datetime, timezone, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.user import User, UserSearchPreference
from src.models.listing import Listing, ListingClassification
from src.models.system import SourceMonitorRun, AdminAuditLog
from src.classification.types import ClassificationLabel
from src.services.monitor_worker import monitor_worker
from src.services.notification_service import notification_service
from src.bot.formatter import format_listing_message, get_listing_inline_keyboard

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


@admin_router.message(Command("admin_health"))
async def handle_admin_health(message: Message):
    """Check health of monitor, provider, and database."""
    if not is_admin(message.from_user.id):
        return

    status_info = monitor_worker.status_summary
    health = await monitor_worker.provider.check_health()

    status_icon = "🟢" if health.status.value == "HEALTHY" else ("🟡" if "DEGRADED" in health.status.value else "🔴")

    text = (
        "🩺 <b>Tizim Salomatligi (Health Check):</b>\n\n"
        f"• Monitor holati: {'To‘xtatilgan (PAUSED)' if status_info['is_paused'] else 'Ishlamoqda (ACTIVE)'}\n"
        f"• Ishlayotgan provayder: <code>{status_info['provider']}</code>\n"
        f"• Provayder holati: {status_icon} <b>{health.status.value}</b>\n"
        f"• Xabar: {health.message}\n"
        f"• So‘nggi muvaffaqiyatli sikl: {status_info['last_run_at'] or 'Hali ishga tushmadi'}\n"
        f"• Ketma-ket xatoliklar: {status_info['consecutive_failures']}\n"
        f"• Intervall: {status_info['poll_interval_seconds']} soniya"
    )
    await message.answer(text=text, parse_mode="HTML")


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
        f"So‘rov oralig‘i: <b>{settings.POLL_INTERVAL_SECONDS}s</b>\n\n"
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


@admin_router.message(Command("channel"))
async def handle_channel_status(message: Message):
    """Show channel status or test broadcast."""
    if not is_admin(message.from_user.id):
        return
    channel = settings.CHANNEL_ID
    if not channel:
        await message.answer(
            "⚠️ Kanal sozlanmagan.\n"
            "Kanalni ulash uchun: <code>/set_channel @kanal_nomi</code> buyrug‘ini yuboring.",
            parse_mode="HTML",
        )
        return

    await message.answer(
        f"📢 <b>Ulangan kanal:</b> <code>{channel}</code>\n\n"
        "Kanalga test xabar yuborish uchun <code>/scrape_now</code> buyrug‘idan foydalanishingiz mumkin.",
        parse_mode="HTML",
    )


@admin_router.message(Command("scrape_now"))
async def handle_scrape_now(message: Message):
    """Manually trigger immediate OLX scrape and channel broadcast."""
    if not is_admin(message.from_user.id):
        return
    status_msg = await message.answer("🔄 OLX dan yangi e'lonlar qidirilmoqda...")
    try:
        run_rec = await monitor_worker.run_once()
        note = ""
        if run_rec.listings_new == 0 and run_rec.listings_found > 0:
            note = "\n\nℹ️ <i>Barcha topilgan e'lonlar allaqachon bazaga kiritilgan. Kanalga yuborish uchun <code>/post_latest 1</code> buyrug'idan foydalaning.</i>"
        elif run_rec.listings_new > 0:
            note = f"\n\n🚀 <b>{run_rec.listings_new}</b> ta yangi e'lon kanalga yuborildi!"

        await status_msg.edit_text(
            f"✅ <b>Monitoring sikli yakunlandi!</b>\n\n"
            f"• Topilgan e'lonlar: <b>{run_rec.listings_found}</b>\n"
            f"• Yangi e'lonlar: <b>{run_rec.listings_new}</b>\n"
            f"• Status: <b>{run_rec.status}</b>\n"
            f"• Kanal: <code>{settings.CHANNEL_ID or 'Sozlanmagan'}</code>"
            f"{note}",
            parse_mode="HTML",
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


@admin_router.message(Command("post_latest"))
async def handle_post_latest(message: Message):
    """Post N most recent listings to configured channel."""
    if not is_admin(message.from_user.id):
        return
    channel = settings.CHANNEL_ID
    if not channel:
        await message.answer("⚠️ Avval <code>/set_channel @kanal_nomi</code> buyrug‘i orqali kanalni sozlang.", parse_mode="HTML")
        return

    parts = message.text.split()
    count = 1
    if len(parts) > 1 and parts[1].isdigit():
        count = min(10, max(1, int(parts[1])))

    status_msg = await message.answer(f"📤 So‘nggi {count} ta e'lon <code>{channel}</code> kanaliga yuklanmoqda...", parse_mode="HTML")

    from sqlalchemy.orm import selectinload
    import asyncio
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Listing)
            .options(selectinload(Listing.classification))
            .order_by(Listing.id.desc())
            .limit(count)
        )
        res = await session.execute(stmt)
        listings = res.scalars().all()

    success_cnt = 0
    for listing in reversed(listings):
        try:
            ok = await notification_service.send_to_channel(listing, channel_id=channel)
            if ok:
                success_cnt += 1
            await asyncio.sleep(1.5)  # Telegram pace
        except Exception as e:
            logger.error("Error posting listing %d to channel: %s", listing.id, e)

    await status_msg.edit_text(
        f"✅ <b>{success_cnt}/{len(listings)} ta e'lon {channel} kanaliga muvaffaqiyatli yuklandi!</b>",
        parse_mode="HTML"
    )

