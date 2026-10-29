"""Periodic Background Monitor Worker for apartment listing discovery and dispatch."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List
from aiogram import Bot
from sqlalchemy import select, func

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.listing import Listing
from src.models.system import SourceMonitorRun
from src.providers.base import BaseListingProvider, ProviderStatus
from src.providers.olx_http import OLXHttpListingProvider
from src.providers.composite import CompositeListingProvider
from src.providers.fixture import FixtureListingProvider, ManualListingProvider
from src.services.listing_service import listing_service
from src.services.notification_service import notification_service
from src.bot.formatter import TASHKENT_TZ

logger = logging.getLogger(__name__)


class MonitorWorker:
    """Orchestrates periodic listing collection, classification, and notification cycles."""

    def __init__(
        self,
        provider: Optional[BaseListingProvider] = None,
        bot: Optional[Bot] = None,
        poll_interval: Optional[int] = None,
    ):
        self.poll_interval = poll_interval or settings.POLL_INTERVAL_SECONDS
        self.bot = bot
        self._is_running = False
        self._is_paused = False
        self._task: Optional[asyncio.Task] = None
        self._consecutive_failures = 0
        self._last_run_at: Optional[datetime] = None
        self._last_status: str = "IDLE"

        # Morning Scrape & On-Demand Control
        self.morning_scrape_enabled: bool = settings.MORNING_SCRAPE_ENABLED
        self.morning_scrape_time: str = settings.MORNING_SCRAPE_TIME
        self.morning_scrape_pages: int = settings.MORNING_SCRAPE_PAGES
        self.last_morning_scrape_date: Optional[str] = None
        self.last_scrape_stats: dict = {
            "last_run": None,
            "found": 0,
            "new": 0,
            "status": "IDLE",
            "is_deep": False,
        }

        # Initialize provider based on configuration (default to OLX)
        if provider:
            self.provider = provider
        elif settings.PROVIDER_TYPE == "fixture":
            self.provider = FixtureListingProvider()
        elif settings.PROVIDER_TYPE == "feed":
            self.provider = ManualListingProvider()
        else:
            self.provider = OLXHttpListingProvider()

    def set_bot(self, bot: Bot) -> None:
        self.bot = bot
        notification_service.set_bot(bot)

    def pause(self) -> None:
        """Pause periodic polling."""
        self._is_paused = True
        logger.info("Monitor worker paused by administrator.")

    def resume(self) -> None:
        """Resume periodic polling."""
        self._is_paused = False
        logger.info("Monitor worker resumed by administrator.")

    def set_morning_scrape_time(self, time_str: str) -> bool:
        """Validate and set Tashkent morning scrape time (HH:MM)."""
        import re
        time_clean = time_str.strip()
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", time_clean):
            return False
        self.morning_scrape_time = time_clean
        settings.MORNING_SCRAPE_TIME = time_clean
        logger.info("Morning scrape time updated to %s (Tashkent time)", time_clean)
        return True

    def toggle_morning_scrape(self, enable: Optional[bool] = None) -> bool:
        """Toggle or explicitly set morning scrape enabled state."""
        if enable is None:
            self.morning_scrape_enabled = not self.morning_scrape_enabled
        else:
            self.morning_scrape_enabled = enable
        settings.MORNING_SCRAPE_ENABLED = self.morning_scrape_enabled
        logger.info("Morning scrape enabled state set to: %s", self.morning_scrape_enabled)
        return self.morning_scrape_enabled

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def status_summary(self) -> dict:
        now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
        today_str = now_tash.strftime("%Y-%m-%d")
        return {
            "provider": self.provider.name,
            "is_running": self._is_running,
            "is_paused": self._is_paused,
            "poll_interval_seconds": self.poll_interval,
            "consecutive_failures": self._consecutive_failures,
            "last_run_at": self._last_run_at.isoformat() if self._last_run_at else None,
            "last_status": self._last_status,
            "morning_scrape_enabled": self.morning_scrape_enabled,
            "morning_scrape_time": self.morning_scrape_time,
            "morning_scrape_pages": self.morning_scrape_pages,
            "morning_done_today": self.last_morning_scrape_date == today_str,
            "last_stats": self.last_scrape_stats,
        }

    async def notify_admins(self, text: str) -> None:
        """Send diagnostic alert or morning digest to configured admins."""
        if not self.bot or not settings.ADMIN_IDS:
            return
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
            except Exception as e:
                logger.warning("Failed to notify admin %d: %s", admin_id, e)

    async def run_once(
        self,
        deep: bool = False,
        pages: Optional[int] = None,
        is_morning: bool = False,
    ) -> SourceMonitorRun:
        """Execute a single collection, persistence, and dispatch iteration (regular or deep)."""
        started_at = datetime.now(timezone.utc)
        self._last_run_at = started_at
        self._last_status = "RUNNING"
        logger.info(
            "Starting listing monitor cycle (deep=%s, morning=%s) with provider '%s'...",
            deep,
            is_morning,
            self.provider.name,
        )

        listings_found = 0
        listings_new = 0
        error_msg = None
        status = "SUCCESS"

        async with AsyncSessionLocal() as session:
            # Create monitor run audit record
            run_record = SourceMonitorRun(
                source_name=f"{self.provider.name}{'_morning' if is_morning else ('_deep' if deep else '')}",
                started_at=started_at,
                status="RUNNING",
            )
            session.add(run_record)
            await session.commit()

            try:
                # 1. Fetch raw listings from provider
                max_pages = pages or (self.morning_scrape_pages if (deep or is_morning) else 2)
                try:
                    raw_items = await self.provider.fetch_listings(deep=deep, max_pages=max_pages)
                except TypeError:
                    raw_items = await self.provider.fetch_listings()
                listings_found = len(raw_items)

                # Check provider health
                if listings_found > 0:
                    status = "SUCCESS"
                else:
                    health = await self.provider.check_health()
                    if health.status == ProviderStatus.BLOCKED_BY_ACCESS_CONTROL:
                        status = "BLOCKED_BY_ACCESS_CONTROL"
                        error_msg = health.message
                    elif health.status == ProviderStatus.DEGRADED:
                        status = "DEGRADED"
                        error_msg = health.message
                    elif health.status == ProviderStatus.ERROR:
                        status = "ERROR"
                        error_msg = health.message
                    else:
                        status = "SUCCESS"

                # 2. Ingest and classify items into database
                new_listings = []
                for item in raw_items:
                    try:
                        listing, is_new = await listing_service.ingest_raw_listing(session, item)
                        if is_new:
                            listings_new += 1
                            new_listings.append(listing)
                    except Exception as item_err:
                        logger.error("Error ingesting item %s: %s", item.canonical_url, item_err)

                # 3. Dispatch notifications for new listings to matching users
                if notification_service.bot:
                    for listing in new_listings:
                        try:
                            await notification_service.dispatch_new_listing(session, listing)
                        except Exception as notif_err:
                            logger.error("Error dispatching notification for listing %d: %s", listing.id, notif_err)

                    # 4. Broadcast batch to Telegram channel
                    try:
                        channel_posted = await notification_service.broadcast_channel_batch(
                            session,
                            new_listings=new_listings,
                        )
                        if channel_posted > 0:
                            logger.info(
                                "Channel batch broadcast: %d listings posted to %s",
                                channel_posted,
                                settings.CHANNEL_ID,
                            )
                    except Exception as ch_err:
                        logger.error("Error in channel batch broadcast: %s", ch_err)

                    # 5. Send automated morning digest if this was a scheduled morning run
                    if is_morning:
                        try:
                            total_active = (await session.execute(
                                select(func.count(Listing.id)).where(Listing.is_active == True)
                            )).scalar() or 0
                            ch_stats = await notification_service.get_channel_posting_stats(session)
                            now_tash = started_at.astimezone(TASHKENT_TZ)
                            morning_msg = (
                                f"🌅 <b>Ertalabki yangi e'lonlar muvaffaqiyatli yuklandi!</b>\n\n"
                                f"📅 Vaqt: <b>{now_tash.strftime('%Y-%m-%d, %H:%M')}</b> (Toshkent)\n"
                                f"🌐 Manba: <b>OLX Uzbekistan (Chuqur qidiruv)</b>\n"
                                f"📥 Tekshirilgan e'lonlar: <b>{listings_found}</b> ta\n"
                                f"✨ Yangi topilgan va saytga qo‘shildi: <b>+{listings_new}</b> ta\n"
                                f"🏠 Saytdagi barcha faol e'lonlar: <b>{total_active}</b> ta\n"
                                f"📢 Telegram kanal zaxirasida: <b>{ch_stats['unposted_total']}</b> ta e'lon\n\n"
                                f"<i>Barcha yangi e'lonlar saytda va botda e'lon qilindi.</i>"
                            )
                            await self.notify_admins(morning_msg)
                        except Exception as m_digest_err:
                            logger.warning("Could not send morning digest to admins: %s", m_digest_err)

                self._consecutive_failures = 0
                self._last_status = status

            except Exception as e:
                self._consecutive_failures += 1
                status = "ERROR"
                error_msg = str(e)
                self._last_status = "ERROR"
                logger.error("Monitor cycle failed: %s", e, exc_info=True)

                if self._consecutive_failures >= 3:
                    await self.notify_admins(
                        f"⚠️ Monitor ketma-ket {self._consecutive_failures} marta xatolikka uchradi!\n"
                        f"Manba: {self.provider.name}\n"
                        f"Xatolik: {error_msg}"
                    )

            finally:
                finished_at = datetime.now(timezone.utc)
                run_record.finished_at = finished_at
                run_record.status = status
                run_record.listings_found = listings_found
                run_record.listings_new = listings_new
                run_record.error_message = error_msg
                await session.commit()

                self.last_scrape_stats = {
                    "last_run": finished_at.astimezone(TASHKENT_TZ).strftime("%H:%M:%S (%Y-%m-%d)"),
                    "found": listings_found,
                    "new": listings_new,
                    "status": status,
                    "is_deep": deep or is_morning,
                }

        logger.info(
            "Monitor cycle finished. Found: %d, New: %d, Status: %s",
            listings_found,
            listings_new,
            status,
        )
        return run_record

    async def _worker_loop(self) -> None:
        """Continuous background execution loop with scheduled morning scrape support."""
        self._is_running = True
        logger.info("Monitor worker loop started. Interval: %d seconds.", self.poll_interval)

        while self._is_running:
            if not self._is_paused:
                now_tashkent = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
                today_str = now_tashkent.strftime("%Y-%m-%d")

                # 1. Scheduled Morning Scrape Check
                if self.morning_scrape_enabled and self.last_morning_scrape_date != today_str:
                    try:
                        sh, sm = map(int, self.morning_scrape_time.split(":"))
                        if (now_tashkent.hour > sh) or (now_tashkent.hour == sh and now_tashkent.minute >= sm):
                            logger.info(
                                "Triggering scheduled morning scrape for %s at %s Tashkent time...",
                                today_str,
                                now_tashkent.strftime("%H:%M"),
                            )
                            self.last_morning_scrape_date = today_str
                            await self.run_once(deep=True, is_morning=True, pages=self.morning_scrape_pages)
                    except Exception as m_err:
                        logger.error("Error evaluating morning scrape schedule: %s", m_err)

                # 2. Regular Periodic Polling Check
                now_utc = datetime.now(timezone.utc)
                if not self._last_run_at or (now_utc - self._last_run_at).total_seconds() >= self.poll_interval:
                    try:
                        await self.run_once()
                    except Exception as e:
                        logger.error("Unhandled error in monitor loop: %s", e)
            else:
                logger.debug("Monitor worker is paused, skipping cycle.")

            # Sleep 30 seconds between schedule checks
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break

        self._is_running = False
        logger.info("Monitor worker loop stopped.")

    def start(self) -> None:
        """Start the background monitor task."""
        if self._is_running:
            logger.warning("Monitor worker is already running.")
            return
        self._task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        """Gracefully stop the background monitor task."""
        if not self._is_running:
            return
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor worker has shut down.")


monitor_worker = MonitorWorker()
