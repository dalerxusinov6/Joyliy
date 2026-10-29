"""Periodic Background Monitor Worker for apartment listing discovery and dispatch."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List
from aiogram import Bot

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.system import SourceMonitorRun
from src.providers.base import BaseListingProvider, ProviderStatus
from src.providers.olx_http import OLXHttpListingProvider
from src.providers.composite import CompositeListingProvider
from src.providers.fixture import FixtureListingProvider, ManualListingProvider
from src.services.listing_service import listing_service
from src.services.notification_service import notification_service

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

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def status_summary(self) -> dict:
        return {
            "provider": self.provider.name,
            "is_running": self._is_running,
            "is_paused": self._is_paused,
            "poll_interval_seconds": self.poll_interval,
            "consecutive_failures": self._consecutive_failures,
            "last_run_at": self._last_run_at.isoformat() if self._last_run_at else None,
            "last_status": self._last_status,
        }

    async def notify_admins(self, text: str) -> None:
        """Send diagnostic alert to configured admins."""
        if not self.bot or not settings.ADMIN_IDS:
            return
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(chat_id=admin_id, text=f"🔔 <b>Admin Ogohlantirish</b>:\n{text}", parse_mode="HTML")
            except Exception as e:
                logger.warning("Failed to notify admin %d: %s", admin_id, e)

    async def run_once(self) -> SourceMonitorRun:
        """Execute a single collection, persistence, and dispatch iteration."""
        started_at = datetime.now(timezone.utc)
        self._last_run_at = started_at
        self._last_status = "RUNNING"
        logger.info("Starting listing monitor cycle with provider '%s'...", self.provider.name)

        listings_found = 0
        listings_new = 0
        error_msg = None
        status = "SUCCESS"

        async with AsyncSessionLocal() as session:
            # Create monitor run audit record
            run_record = SourceMonitorRun(
                source_name=self.provider.name,
                started_at=started_at,
                status="RUNNING",
            )
            session.add(run_record)
            await session.commit()

            try:
                # 1. Fetch raw listings from provider
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

                # 2. Ingest and classify items
                new_listings = []
                for item in raw_items:
                    try:
                        listing, is_new = await listing_service.ingest_raw_listing(session, item)
                        if is_new:
                            listings_new += 1
                            new_listings.append(listing)
                    except Exception as item_err:
                        logger.error("Error ingesting item %s: %s", item.canonical_url, item_err)

                # 3. Dispatch notifications for new listings
                if notification_service.bot:
                    for listing in new_listings:
                        try:
                            # Broadcast to Telegram channel if configured
                            if settings.CHANNEL_ID:
                                sent = await notification_service.send_to_channel(listing)
                                if sent:
                                    await asyncio.sleep(1.0)
                        except Exception as ch_err:
                            logger.error("Error broadcasting listing %d to channel: %s", listing.id, ch_err)

                        try:
                            # Dispatch to subscribed users matching preferences
                            await notification_service.dispatch_new_listing(session, listing)
                        except Exception as notif_err:
                            logger.error("Error dispatching notification for listing %d: %s", listing.id, notif_err)

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

        logger.info(
            "Monitor cycle finished. Found: %d, New: %d, Status: %s",
            listings_found,
            listings_new,
            status,
        )
        return run_record

    async def _worker_loop(self) -> None:
        """Continuous background execution loop."""
        self._is_running = True
        logger.info("Monitor worker loop started. Interval: %d seconds.", self.poll_interval)

        while self._is_running:
            if not self._is_paused:
                try:
                    await self.run_once()
                except Exception as e:
                    logger.error("Unhandled error in monitor loop: %s", e)
            else:
                logger.debug("Monitor worker is paused, skipping cycle.")

            # Sleep until next scheduled interval
            try:
                await asyncio.sleep(self.poll_interval)
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

