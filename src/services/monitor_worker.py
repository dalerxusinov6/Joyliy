"""Production Background Monitor Worker for apartment listing discovery, deduplication, and real-time dispatch."""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set
from aiogram import Bot
from sqlalchemy import select, func

from src.config import settings
from src.database import AsyncSessionLocal, AsyncSession
from src.models.listing import Listing, ListingUpdateHistory, ChannelPublishQueue, ChannelPostHistory
from src.models.system import SourceMonitorRun
from src.providers.base import BaseListingProvider, ProviderStatus
from src.providers.olx_http import OLXHttpListingProvider
from src.providers.fixture import FixtureListingProvider, ManualListingProvider
from src.services.listing_service import listing_service
from src.services.notification_service import notification_service
from src.services.redis_service import redis_service
from src.bot.formatter import TASHKENT_TZ

logger = logging.getLogger(__name__)


class MonitorWorker:
    """
    Intelligent automatic parser & orchestrator.
    Executes scheduled discovery scans 3x daily (08:00, 14:00, 20:00 Asia/Tashkent),
    ingests listings with multi-tier deduplication and update tracking,
    immediately broadcasts newly discovered listings to the Telegram channel,
    and provides real-time administrative telemetry.
    """

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
        self._last_scan_duration: float = 0.0
        self._last_status: str = "IDLE"

        # 3x Daily Tashkent Schedule Slots
        self.scheduled_times: List[str] = list(settings.PARSER_SCHEDULE_TIMES)
        self.pages_per_run: int = settings.PARSER_PAGES_PER_RUN
        self._current_day: Optional[str] = None
        self._executed_slots_today: Set[str] = set()

        # Telemetry metrics
        self.total_discovered_today: int = 0
        self.new_discovered_today: int = 0
        self.updated_today: int = 0
        self.duplicates_detected_today: int = 0

        # Circular buffer of recent log entries (kept in-memory for admin UI)
        self._recent_logs: deque = deque(maxlen=150)

        # Legacy backward-compatibility fields
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

        # Initialize provider (default to OLX HTTP)
        if provider:
            self.provider = provider
        elif settings.PROVIDER_TYPE == "fixture":
            self.provider = FixtureListingProvider()
        elif settings.PROVIDER_TYPE == "feed":
            self.provider = ManualListingProvider()
        else:
            self.provider = OLXHttpListingProvider()

        self.log_event("INFO", f"MonitorWorker initialized with provider '{self.provider.name}'.")

    def set_bot(self, bot: Bot) -> None:
        self.bot = bot
        notification_service.set_bot(bot)

    def log_event(self, level: str, message: str) -> None:
        """Record structured event in circular log buffer and logger."""
        now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
        entry = {
            "timestamp": now_tash.strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
        }
        self._recent_logs.append(entry)
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def get_recent_logs(self) -> List[Dict[str, str]]:
        """Return shallow copy of in-memory logs in reverse chronological order."""
        return list(reversed(self._recent_logs))

    def pause(self) -> None:
        """Pause periodic and scheduled polling."""
        self._is_paused = True
        self.log_event("WARNING", "Monitor worker paused by administrator.")

    def resume(self) -> None:
        """Resume periodic and scheduled polling."""
        self._is_paused = False
        self.log_event("INFO", "Monitor worker resumed by administrator.")

    @property
    def schedule_times(self) -> List[str]:
        return self.scheduled_times

    def set_schedule_times(self, times: List[str]) -> bool:
        """Update daily scheduled discovery slots (HH:MM in Asia/Tashkent)."""
        import re
        valid_times = []
        for t in times:
            t_clean = t.strip()
            if re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", t_clean):
                valid_times.append(t_clean)
        if valid_times:
            self.scheduled_times = sorted(valid_times)
            self.log_event("INFO", f"Updated parser schedule times: {self.scheduled_times}")
            return True
        return False

    def set_morning_scrape_time(self, time_str: str) -> bool:
        """Validate and set Tashkent morning scrape time (HH:MM)."""
        import re
        time_clean = time_str.strip()
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", time_clean):
            return False
        self.morning_scrape_time = time_clean
        settings.MORNING_SCRAPE_TIME = time_clean
        self.log_event("INFO", f"Morning scrape time updated to {time_clean} (Tashkent time)")
        return True

    def toggle_morning_scrape(self, enable: Optional[bool] = None) -> bool:
        """Toggle or explicitly set morning scrape enabled state."""
        if enable is None:
            self.morning_scrape_enabled = not self.morning_scrape_enabled
        else:
            self.morning_scrape_enabled = enable
        settings.MORNING_SCRAPE_ENABLED = self.morning_scrape_enabled
        self.log_event("INFO", f"Morning scrape state set to: {self.morning_scrape_enabled}")
        return self.morning_scrape_enabled

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_next_scheduled_run(self) -> Optional[str]:
        """Compute the next scheduled slot in Tashkent local time."""
        now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
        now_hm = now_tash.strftime("%H:%M")
        for slot in sorted(self.scheduled_times):
            if slot > now_hm and slot not in self._executed_slots_today:
                return f"Bugun, {slot} (Toshkent)"
        if self.scheduled_times:
            return f"Ertaga, {sorted(self.scheduled_times)[0]} (Toshkent)"
        return None

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
            "last_scan_duration_seconds": round(self._last_scan_duration, 2),
            "last_status": self._last_status,
            "scheduled_times": self.scheduled_times,
            "completed_slots_today": sorted(list(self._executed_slots_today)),
            "next_scheduled_run": self.get_next_scheduled_run(),
            "total_discovered_today": self.total_discovered_today,
            "new_discovered_today": self.new_discovered_today,
            "updated_today": self.updated_today,
            "duplicates_detected_today": self.duplicates_detected_today,
            "morning_scrape_enabled": self.morning_scrape_enabled,
            "morning_scrape_time": self.morning_scrape_time,
            "morning_scrape_pages": self.morning_scrape_pages,
            "morning_done_today": today_str in (self.last_morning_scrape_date or ""),
            "last_stats": self.last_scrape_stats,
        }

    async def get_dashboard_stats(self, session: AsyncSession) -> dict:
        """Fetch unified parser health, database totals, and Telegram queue status for admin dashboard."""
        now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)

        # Database counts
        total_active = (await session.execute(
            select(func.count(Listing.id)).where(Listing.is_active == True)
        )).scalar() or 0

        unposted_count = (await session.execute(
            select(func.count(Listing.id)).where(
                Listing.is_active == True,
                Listing.posted_to_channel_at.is_(None),
            )
        )).scalar() or 0

        queue_pending = (await session.execute(
            select(func.count(ChannelPublishQueue.id)).where(ChannelPublishQueue.status == "pending")
        )).scalar() or 0

        queue_total = (await session.execute(
            select(func.count(ChannelPublishQueue.id))
        )).scalar() or 0

        channel_published_total = (await session.execute(
            select(func.count(ChannelPostHistory.id))
        )).scalar() or 0

        summary = self.status_summary
        summary.update({
            "active_listings_count": total_active,
            "unposted_channel_count": unposted_count,
            "telegram_queue_pending": queue_pending,
            "telegram_queue_total": queue_total,
            "channel_posts_published_total": channel_published_total,
            "server_tashkent_time": now_tash.strftime("%Y-%m-%d %H:%M:%S"),
        })
        return summary

    async def notify_admins(self, text: str) -> None:
        """Send diagnostic alert or digest to configured Telegram admins."""
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
        is_scheduled: bool = False,
        slot_name: Optional[str] = None,
        is_morning: bool = False,
    ) -> SourceMonitorRun:
        """
        Execute an end-to-end collection, multi-tier deduplication, database persistence,
        and immediate Telegram channel publishing iteration.
        """
        started_at = datetime.now(timezone.utc)
        self._last_run_at = started_at
        self._last_status = "RUNNING"
        run_mode = slot_name or ("scheduled" if is_scheduled else ("morning" if is_morning else ("deep" if deep else "quick")))

        self.log_event("INFO", f"Starting parser scan '{run_mode}' via provider '{self.provider.name}'...")

        listings_found = 0
        listings_new = 0
        listings_updated = 0
        duplicates_detected = 0
        channel_posted = 0
        error_msg = None
        status = "SUCCESS"

        async with redis_service.lock("parser_scan", timeout=600) as acquired:
            if not acquired:
                self.log_event("WARNING", "Concurrent scan detected. Another instance is currently executing a parser run.")
                return SourceMonitorRun(
                    source_name=f"{self.provider.name}_{run_mode}",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                    status="SKIPPED_CONCURRENT",
                )

            async with AsyncSessionLocal() as session:
                run_record = SourceMonitorRun(
                    source_name=f"{self.provider.name}_{run_mode}",
                    started_at=started_at,
                    status="RUNNING",
                )
                session.add(run_record)
                await session.commit()

            try:
                # 1. Fetch raw listings from provider
                max_pages = pages or (self.pages_per_run if (deep or is_scheduled or is_morning) else 2)
                try:
                    raw_items = await self.provider.fetch_listings(deep=deep or is_scheduled, max_pages=max_pages)
                except TypeError:
                    raw_items = await self.provider.fetch_listings()

                listings_found = len(raw_items)

                # Check provider health
                if listings_found == 0:
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

                # 2. Ingest and classify items with deduplication & update history
                new_listings: List[Listing] = []
                for item in raw_items:
                    try:
                        listing, is_new = await listing_service.ingest_raw_listing(session, item)
                        if is_new:
                            listings_new += 1
                            new_listings.append(listing)
                        else:
                            # Check if existing listing was updated during ingest
                            # (ListingUpdateHistory records created within the last 15s)
                            now_utc = datetime.now(timezone.utc)
                            recent_update_stmt = select(func.count(ListingUpdateHistory.id)).where(
                                ListingUpdateHistory.listing_id == listing.id,
                                ListingUpdateHistory.detected_at >= started_at,
                            )
                            has_update = (await session.execute(recent_update_stmt)).scalar() or 0
                            if has_update > 0:
                                listings_updated += 1
                            else:
                                duplicates_detected += 1
                    except Exception as item_err:
                        self.log_event("ERROR", f"Error ingesting item {item.canonical_url}: {item_err}")

                # Update daily telemetry counters
                self.total_discovered_today += listings_found
                self.new_discovered_today += listings_new
                self.updated_today += listings_updated
                self.duplicates_detected_today += duplicates_detected

                # 3. IMMEDIATELY Publish newly discovered listings to Telegram channel
                # (Requirements: Do NOT wait until next scan; publish immediately)
                if notification_service.bot:
                    # Dispatch to user alerts first
                    for listing in new_listings:
                        try:
                            await notification_service.dispatch_new_listing(session, listing)
                        except Exception as notif_err:
                            logger.error("Error dispatching user notification for #%d: %s", listing.id, notif_err)

                    # Batch broadcast directly to the Telegram channel (with automatic backfill of existing ads if 0 new)
                    try:
                        channel_posted = await notification_service.broadcast_channel_batch(
                            session,
                            new_listings=new_listings,
                            allow_backfill=True,
                        )
                        if channel_posted > 0:
                            post_type = "new" if new_listings else "gap-fill (existing)"
                            self.log_event(
                                "INFO",
                                f"Published {channel_posted} {post_type} listings directly to Telegram channel {settings.CHANNEL_ID}.",
                            )
                    except Exception as ch_err:
                        self.log_event("ERROR", f"Channel broadcast error: {ch_err}")

                # 4. If scheduled run, deliver admin digest
                if is_scheduled or is_morning:
                    try:
                        now_tash = started_at.astimezone(TASHKENT_TZ)
                        total_active = (await session.execute(
                            select(func.count(Listing.id)).where(Listing.is_active == True)
                        )).scalar() or 0
                        digest_msg = (
                            f"🔔 <b>Joyliy.uz — Avtomatik skanerlash hisoboti ({run_mode})</b>\n\n"
                            f"📅 Vaqt: <b>{now_tash.strftime('%Y-%m-%d, %H:%M')}</b> (Toshkent)\n"
                            f"🌐 Manba: <b>{self.provider.name}</b>\n"
                            f"📥 Topilgan e'lonlar: <b>{listings_found}</b> ta\n"
                            f"✨ Yangi qo‘shilgan: <b>+{listings_new}</b> ta\n"
                            f"🔄 Yangilangan (narx/rasm): <b>{listings_updated}</b> ta\n"
                            f"🛡 Takroriy (filtrlandi): <b>{duplicates_detected}</b> ta\n"
                            f"📢 Kanalga joylandi: <b>{channel_posted}</b> ta\n"
                            f"🏠 Saytdagi barcha faol: <b>{total_active}</b> ta\n\n"
                            f"<i>Barcha yangi e'lonlar saytda darhol ko‘rinadi.</i>"
                        )
                        await self.notify_admins(digest_msg)
                    except Exception as dig_err:
                        logger.warning("Could not send admin digest: %s", dig_err)

                self._consecutive_failures = 0
                self._last_status = status

            except Exception as e:
                self._consecutive_failures += 1
                status = "ERROR"
                error_msg = str(e)
                self._last_status = "ERROR"
                self.log_event("ERROR", f"Monitor cycle failed: {e}")

                if self._consecutive_failures >= 3:
                    await self.notify_admins(
                        f"⚠️ <b>Joyliy Parser Xatoligi!</b>\n"
                        f"Ketma-ket {self._consecutive_failures} marta muvaffaqiyatsiz bo‘ldi.\n"
                        f"Manba: {self.provider.name}\n"
                        f"Xatolik: <code>{error_msg}</code>"
                    )

            finally:
                finished_at = datetime.now(timezone.utc)
                self._last_scan_duration = (finished_at - started_at).total_seconds()
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
                    "updated": listings_updated,
                    "duplicates": duplicates_detected,
                    "posted_channel": channel_posted,
                    "duration_seconds": round(self._last_scan_duration, 2),
                    "status": status,
                    "is_deep": deep or is_scheduled,
                }

        self.log_event(
            "INFO",
            f"Parser scan finished in {self._last_scan_duration:.2f}s. "
            f"Found: {listings_found}, New: {listings_new}, Updated: {listings_updated}, "
            f"Duplicates: {duplicates_detected}, Telegram: {channel_posted}, Status: {status}",
        )
        return run_record

    async def run_manual_scan(self, deep: bool = True, pages: int = 3) -> dict:
        """Trigger an on-demand manual scan from the admin dashboard."""
        run = await self.run_once(deep=deep, pages=pages, slot_name="manual_admin")
        return {
            "status": run.status,
            "listings_found": run.listings_found or 0,
            "listings_new": run.listings_new or 0,
            "duration_seconds": round(self._last_scan_duration, 2),
            "error_message": run.error_message,
        }

    async def retry_channel_queue(self, session: AsyncSession) -> int:
        """Retry pending or failed Telegram channel posts from the queue."""
        if not self.bot:
            return 0
        posted = await notification_service.broadcast_channel_batch(session, force=True, batch_limit=5)
        self.log_event("INFO", f"Manual retry channel queue completed: {posted} items published.")
        return posted

    async def _worker_loop(self) -> None:
        """
        Continuous background execution loop.
        Monitors 3x daily schedule slots (08:00, 14:00, 20:00 Asia/Tashkent),
        resets daily counters at midnight, and triggers automatic scans without waiting.
        """
        self._is_running = True
        self.log_event("INFO", f"Parser background worker loop started. Scheduled slots: {self.scheduled_times}")

        while self._is_running:
            if not self._is_paused:
                now_tashkent = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
                today_str = now_tashkent.strftime("%Y-%m-%d")

                # Day rollover: reset today's executed slots & counters
                if self._current_day != today_str:
                    self._current_day = today_str
                    self._executed_slots_today.clear()
                    self.total_discovered_today = 0
                    self.new_discovered_today = 0
                    self.updated_today = 0
                    self.duplicates_detected_today = 0
                    self.log_event("INFO", f"New calendar day started in Tashkent: {today_str}. Schedule slots reset.")

                # Check 3x daily schedule slots (08:00, 14:00, 20:00 Tashkent time)
                current_hm = now_tashkent.strftime("%H:%M")
                for slot in self.scheduled_times:
                    if slot not in self._executed_slots_today:
                        try:
                            sh, sm = map(int, slot.split(":"))
                            if (now_tashkent.hour > sh) or (now_tashkent.hour == sh and now_tashkent.minute >= sm):
                                self.log_event("INFO", f"Executing scheduled discovery slot '{slot}' (Tashkent)...")
                                self._executed_slots_today.add(slot)
                                await self.run_once(
                                    deep=True,
                                    is_scheduled=True,
                                    slot_name=slot,
                                    pages=self.pages_per_run,
                                )
                        except Exception as slot_err:
                            self.log_event("ERROR", f"Error evaluating slot '{slot}': {slot_err}")

                # Regular periodic poll fallback (if no run in poll_interval seconds)
                now_utc = datetime.now(timezone.utc)
                if not self._last_run_at or (now_utc - self._last_run_at).total_seconds() >= self.poll_interval:
                    try:
                        await self.run_once(deep=False, pages=1)
                    except Exception as e:
                        self.log_event("ERROR", f"Unhandled error in periodic poll: {e}")
            else:
                logger.debug("Monitor worker is paused, skipping check.")

            # Sleep 30 seconds between schedule checks
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break

        self._is_running = False
        self.log_event("INFO", "Parser background worker loop stopped.")

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
        self.log_event("INFO", "Monitor worker shut down successfully.")


monitor_worker = MonitorWorker()
