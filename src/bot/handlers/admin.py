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

    async with AsyncSessionLocal() as session:
        ch_stats = await notification_service.get_channel_posting_stats(session)

    text = (
        "🩺 <b>Tizim Salomatligi (Health Check):</b>\n\n"
        f"• Monitor holati: {'To‘xtatilgan (PAUSED)' if status_info['is_paused'] else 'Ishlamoqda (ACTIVE)'}\n"
        f"• Ishlayotgan provayder: <code>{status_info['provider']}</code>\n"
        f"• Provayder holati: {status_icon} <b>{health.status.value}</b>\n"
        f"• Xabar: {health.message}\n"
        f"• Ulangan kanal: <code>{ch_stats['channel'] or 'Sozlanmagan'}</code>\n"
        f"• Bugun kanalga yuborildi: <b>{ch_stats['posted_today']} / {ch_stats['daily_limit']}</b> ta\n"
        f"• Navbatdagi yangi e'lonlar: <b>{ch_stats['unposted_total']}</b> ta\n"
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
    status_msg = await message.answer("🔄 OLX dan yangi e'lonlar qidirilmoqda va kanal yangilanmoqda...")
    try:
        run_rec = await monitor_worker.run_once()

        async with AsyncSessionLocal() as session:
            stats = await notification_service.get_channel_posting_stats(session)

        status_text = "Faol / Ishlamoqda" if run_rec.status in ("SUCCESS", "OK") else run_rec.status
        note = ""
        if run_rec.listings_new > 0:
            note = f"\n\n🚀 <b>{run_rec.listings_new}</b> ta yangi e'lon topildi!"

        await status_msg.edit_text(
            f"✅ <b>Monitoring va Kanal yangilandi!</b>\n\n"
            f"• Manba: <b>OLX Uzbekistan</b>\n"
            f"• Tekshirilgan e'lonlar: <b>{run_rec.listings_found}</b> ta\n"
            f"• Yangi topilgan: <b>{run_rec.listings_new}</b> ta\n"
            f"• Holat: <b>{status_text}</b>\n"
            f"• Ulangan kanal: <code>{settings.CHANNEL_ID or 'Sozlanmagan'}</code>\n"
            f"• Bugun kanalga yuborildi: <b>{stats['posted_today']} / {stats['daily_limit']}</b> ta\n"
            f"• Navbatdagi zaxira e'lonlar: <b>{stats['unposted_total']}</b> ta\n"
            f"• Taqsimot: <b>Kuniga 100 tagacha bo‘lib-bo‘lib (har 10 daqiqada 1-2 tadan)</b>"
            f"{note}",
            parse_mode="HTML",
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")


@admin_router.message(Command("channel_status"))
@admin_router.message(Command("channel"))
async def handle_channel_status(message: Message):
    """View channel broadcast status, today's count, and queue size."""
    if not is_admin(message.from_user.id):
        return
    async with AsyncSessionLocal() as session:
        stats = await notification_service.get_channel_posting_stats(session)

    channel_name = settings.CHANNEL_ID or "Sozlanmagan"
    quiet_str = "Sokin vaqt (tunda yuborilmaydi)" if stats["is_quiet_hours"] else "Faol vaqt (e'lonlar uzatilmoqda)"

    text = (
        f"📢 <b>Kanalga e'lon uzatish holati:</b>\n\n"
        f"• Ulangan kanal: <code>{channel_name}</code>\n"
        f"• Bugun yuborilgan e'lonlar: <b>{stats['posted_today']} / {stats['daily_limit']}</b> ta\n"
        f"• Qolgan kunlik limit: <b>{stats['remaining_today']}</b> ta\n"
        f"• Bazadagi navbatda turgan e'lonlar: <b>{stats['unposted_total']}</b> ta\n"
        f"• Tizim grafigi: <b>Kun bo‘yi bo‘lib-bo‘lib (har 10 daqiqada 1-2 tadan)</b>\n"
        f"• Hozirgi holat: <b>{quiet_str}</b>\n\n"
        f"<b>Buyruqlar:</b>\n"
        f"• <code>/post_latest 1</code> — hoziroq kanalga 1 ta e'lon chiqarish\n"
        f"• <code>/scrape_now</code> — hozir qidirish va kanalni yangilash\n"
        f"• <code>/set_channel @kanal_nomi</code> — kanal nomini o‘zgartirish"
    )
    await message.answer(text, parse_mode="HTML")


@admin_router.message(Command("post_latest"))
async def handle_post_latest(message: Message):
    """Post N most recent unposted, unique listings to configured channel."""
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

    status_msg = await message.answer(f"📤 So‘nggi {count} ta yangi e'lon <code>{channel}</code> kanaliga tayyorlanmoqda...", parse_mode="HTML")

    from sqlalchemy.orm import selectinload
    import asyncio
    async with AsyncSessionLocal() as session:
        # Strictly select ONLY listings that have NEVER been posted to the channel
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
            .limit(count * 5)
        )
        res = await session.execute(stmt)
        candidates = res.scalars().all()

        chosen_candidates = []
        for listing in candidates:
            if len(chosen_candidates) >= count:
                break
            # Skip any duplicate match against history and already chosen items
            if await notification_service.is_channel_duplicate(session, listing, in_batch_candidates=chosen_candidates):
                listing.posted_to_channel_at = datetime.now(timezone.utc)
                listing.is_active = False
                session.add(listing)
                await session.commit()
                continue
            chosen_candidates.append(listing)

        success_cnt = 0
        for listing in chosen_candidates:
            try:
                ok = await notification_service.send_to_channel(listing, channel_id=channel, session=session)
                if ok:
                    success_cnt += 1
                await asyncio.sleep(2.0)  # Telegram pace
            except Exception as e:
                logger.error("Error posting listing %d to channel: %s", listing.id, e)

    if success_cnt > 0:
        await status_msg.edit_text(
            f"✅ <b>{success_cnt} ta mutlaqo yangi e'lon {channel} kanaliga muvaffaqiyatli yuklandi!</b>",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text(
            f"ℹ️ <b>Bazada kanalga yuborilmagan yangi e'lon qolmadi.</b>\n\n"
            f"Barcha e'lonlar allaqachon kanalga chiqqan. Yangi e'lonlarni internetdan (OLX) yuklab olish uchun <code>/scrape_now</code> buyrug‘ini bosing.",
            parse_mode="HTML"
        )

