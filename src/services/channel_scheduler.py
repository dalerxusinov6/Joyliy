"""Automated Telegram Channel Publishing Scheduler adhering to 10-post daily timeline."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta, time
from typing import Optional, List, Dict, Any
from aiogram import Bot
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.listing import (
    Listing,
    ChannelPublishSchedule,
    ChannelPublishQueue,
    QueueStatus,
    utc_now,
)
from src.services.queue_service import queue_service
from src.services.notification_service import notification_service
from src.bot.formatter import TASHKENT_TZ

logger = logging.getLogger(__name__)


class ChannelScheduler:
    """
    Automated publishing scheduler for Telegram channel (@joyliy_uz).
    Executes exactly across 10 scheduled daily slots:
    08:00, 09:20, 10:40, 12:00, 13:20, 14:40, 16:00, 17:20, 18:40, 20:00 (Asia/Tashkent).

    Strict Guarantees:
    - Never publishes duplicate ads.
    - Never publishes outside 08:00-20:00 window.
    - If queue is empty, skips the slot cleanly.
    - Never creates catch-up bursts after being offline.
    - Persistent state survives bot restarts.
    """

    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot
        self._is_running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.schedule_times: List[str] = list(settings.CHANNEL_SCHEDULE_TIMES)

    def set_bot(self, bot: Bot) -> None:
        self.bot = bot
        notification_service.set_bot(bot)

    def is_within_publishing_window(self, dt: Optional[datetime] = None) -> bool:
        """Check if Tashkent time is within the allowed 08:00 - 20:00 window."""
        tash_dt = (dt or datetime.now(timezone.utc)).astimezone(TASHKENT_TZ)
        cur_time = tash_dt.time()
        try:
            sh, sm = map(int, settings.CHANNEL_WINDOW_START.split(":"))
            eh, em = map(int, settings.CHANNEL_WINDOW_END.split(":"))
            start_t = time(sh, sm)
            end_t = time(eh, em)
        except Exception:
            start_t = time(8, 0)
            end_t = time(20, 0)
        return start_t <= cur_time <= end_t

    def get_next_scheduled_slot(self, dt: Optional[datetime] = None) -> Optional[str]:
        """Compute the next scheduled slot in Tashkent time."""
        tash_dt = (dt or datetime.now(timezone.utc)).astimezone(TASHKENT_TZ)
        cur_hm = tash_dt.strftime("%H:%M")
        for s in self.schedule_times:
            if s > cur_hm:
                return s
        return f"Ertaga {self.schedule_times[0]}"

    async def execute_slot(
        self,
        slot_date: str,
        slot_time: str,
        force: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        Execute an individual scheduled publication slot with atomic persistence.
        """
        async with self._lock:
            if session is not None:
                return await self._execute_slot_internal(session, slot_date, slot_time, force)
            else:
                async with AsyncSessionLocal() as s:
                    return await self._execute_slot_internal(s, slot_date, slot_time, force)

    async def _execute_slot_internal(
        self,
        session: AsyncSession,
        slot_date: str,
        slot_time: str,
        force: bool = False,
    ) -> Dict[str, Any]:
                # 1. Check if slot was already executed for this date
                stmt = select(ChannelPublishSchedule).where(
                    and_(
                        ChannelPublishSchedule.slot_date == slot_date,
                        ChannelPublishSchedule.slot_time == slot_time,
                    )
                )
                res = await session.execute(stmt)
                slot_record = res.scalars().first()

                if slot_record and slot_record.status in ("published", "executing") and not force:
                    logger.info("Slot %s %s already executed (status: %s).", slot_date, slot_time, slot_record.status)
                    return {"status": "already_executed", "slot": slot_time}

                if not slot_record:
                    slot_record = ChannelPublishSchedule(
                        slot_date=slot_date,
                        slot_time=slot_time,
                        status="executing",
                    )
                    session.add(slot_record)
                    await session.commit()
                else:
                    slot_record.status = "executing"
                    session.add(slot_record)
                    await session.commit()

                # 2. Select next eligible advertisement from persistent queue
                queue_item = await queue_service.get_next_eligible_item(session)

                if not queue_item:
                    # No new advertisement waiting in queue -> skip slot cleanly
                    slot_record.status = "skipped"
                    slot_record.executed_at = utc_now()
                    session.add(slot_record)
                    await session.commit()
                    logger.info(
                        "No new eligible advertisements in queue for slot %s %s. Slot skipped without publishing.",
                        slot_date,
                        slot_time,
                    )
                    return {
                        "status": "skipped",
                        "reason": "empty_queue",
                        "slot": slot_time,
                    }

                # 3. Double-check for duplicate against channel history
                listing = queue_item.listing
                if not listing:
                    # Reload listing
                    listing = (
                        await session.execute(
                            select(Listing).where(Listing.id == queue_item.listing_id)
                        )
                    ).scalars().first()

                if not listing:
                    await queue_service.mark_failed(session, queue_item, "Listing record not found")
                    slot_record.status = "failed"
                    session.add(slot_record)
                    await session.commit()
                    return {"status": "failed", "reason": "listing_missing"}

                is_dup, dup_reason = await queue_service.is_duplicate(
                    session, listing, exclude_queue_id=queue_item.id
                )
                if is_dup:
                    logger.warning("Queue item #%d was rejected as duplicate before post: %s", queue_item.id, dup_reason)
                    await queue_service.mark_failed(session, queue_item, f"Duplicate detected: {dup_reason}")
                    slot_record.status = "skipped"
                    session.add(slot_record)
                    await session.commit()
                    return {"status": "skipped", "reason": dup_reason}

                # 4. Dispatch to Telegram channel
                logger.info(
                    "Publishing slot %s %s: Listing #%d ('%s')...",
                    slot_date,
                    slot_time,
                    listing.id,
                    listing.title[:40],
                )
                try:
                    msg_id = await notification_service.send_to_channel_verified(
                        listing=listing,
                        channel_id=settings.CHANNEL_ID,
                    )

                    if msg_id:
                        # 5. Persist published status and record message ID
                        slot_name = f"{slot_date} {slot_time}"
                        await queue_service.mark_published(
                            session=session,
                            queue_item=queue_item,
                            telegram_message_id=msg_id,
                            slot_name=slot_name,
                        )
                        slot_record.status = "published"
                        slot_record.queue_item_id = queue_item.id
                        slot_record.telegram_message_id = msg_id
                        slot_record.executed_at = utc_now()
                        session.add(slot_record)
                        await session.commit()

                        logger.info(
                            "Slot %s %s published successfully! Listing #%d -> Telegram message #%s",
                            slot_date,
                            slot_time,
                            listing.id,
                            msg_id,
                        )
                        return {
                            "status": "published",
                            "slot": slot_time,
                            "listing_id": listing.id,
                            "telegram_message_id": msg_id,
                        }
                    else:
                        error_msg = "Telegram delivery failed (no message ID returned)"
                        await queue_service.mark_failed(session, queue_item, error_msg)
                        slot_record.status = "failed"
                        slot_record.executed_at = utc_now()
                        session.add(slot_record)
                        await session.commit()
                        return {"status": "failed", "reason": error_msg}

                except Exception as post_err:
                    logger.error("Error executing publishing slot %s %s: %s", slot_date, slot_time, post_err, exc_info=True)
                    await queue_service.mark_failed(session, queue_item, str(post_err))
                    slot_record.status = "failed"
                    slot_record.executed_at = utc_now()
                    session.add(slot_record)
                    await session.commit()
                    return {"status": "failed", "error": str(post_err)}

    async def check_and_run_due_slots(self, now_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Check timeline for current due slots.
        Reconciles missed slots while offline (marks them missed, does NOT flood).
        Executes active slot if due.
        """
        if not settings.CHANNEL_POSTING_ENABLED:
            return []

        tash_dt = (now_dt or datetime.now(timezone.utc)).astimezone(TASHKENT_TZ)
        today_str = tash_dt.strftime("%Y-%m-%d")
        cur_hm = tash_dt.strftime("%H:%M")

        # If outside publishing window (08:00 - 20:00), do nothing
        if not self.is_within_publishing_window(tash_dt):
            return []

        results = []
        async with AsyncSessionLocal() as session:
            # Query all schedule records for today
            sched_rows = (
                await session.execute(
                    select(ChannelPublishSchedule).where(
                        ChannelPublishSchedule.slot_date == today_str
                    )
                )
            ).scalars().all()
            recorded_map = {r.slot_time: r for r in sched_rows}

            for s_time in self.schedule_times:
                if s_time > cur_hm:
                    continue  # Future slot

                record = recorded_map.get(s_time)
                if record:
                    continue  # Already processed or currently processing

                # Slot is in past or current
                sh, sm = map(int, s_time.split(":"))
                slot_moment = tash_dt.replace(hour=sh, minute=sm, second=0, microsecond=0)
                diff_minutes = (tash_dt - slot_moment).total_seconds() / 60.0

                if diff_minutes > 20.0:
                    # Slot was from earlier while the bot was offline.
                    # Per requirements: "Do not publish multiple advertisements simultaneously to compensate for missed slots."
                    # "If the bot was offline, resume intelligently without flooding the channel."
                    missed_rec = ChannelPublishSchedule(
                        slot_date=today_str,
                        slot_time=s_time,
                        status="missed",
                        executed_at=utc_now(),
                    )
                    session.add(missed_rec)
                    await session.commit()
                    logger.info(
                        "Slot %s (%s) was missed while bot was offline. Marked as missed to prevent burst flooding.",
                        s_time,
                        today_str,
                    )
                    results.append({"slot": s_time, "status": "missed"})
                else:
                    # This slot is currently active (arrived within last 20 minutes)
                    res = await self.execute_slot(today_str, s_time)
                    results.append(res)
                    # Only execute one slot per check iteration
                    break

        return results

    async def _scheduler_loop(self) -> None:
        """Periodic background evaluation loop for publication schedule."""
        self._is_running = True
        logger.info("Channel publishing scheduler loop started (10 daily slots in Asia/Tashkent).")

        while self._is_running:
            try:
                await self.check_and_run_due_slots()
            except Exception as e:
                logger.error("Unhandled error in channel scheduler loop: %s", e, exc_info=True)

            try:
                await asyncio.sleep(20)  # Check every 20 seconds
            except asyncio.CancelledError:
                break

        self._is_running = False
        logger.info("Channel publishing scheduler loop stopped.")

    def start(self) -> None:
        """Start the background scheduler task."""
        if self._is_running:
            return
        self._task = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        """Gracefully stop the background scheduler task."""
        if not self._is_running:
            return
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Channel scheduler shut down.")

    async def get_schedule_status(self, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """Get summary of today's 10 publication slots for admin dashboard."""
        now_tash = datetime.now(timezone.utc).astimezone(TASHKENT_TZ)
        today_str = now_tash.strftime("%Y-%m-%d")

        if session is not None:
            return await self._get_schedule_status_internal(session, now_tash, today_str)
        else:
            async with AsyncSessionLocal() as s:
                return await self._get_schedule_status_internal(s, now_tash, today_str)

    async def _get_schedule_status_internal(
        self,
        session: AsyncSession,
        now_tash: datetime,
        today_str: str,
    ) -> Dict[str, Any]:
        rows = (
            await session.execute(
                select(ChannelPublishSchedule).where(
                    ChannelPublishSchedule.slot_date == today_str
                )
            )
        ).scalars().all()
        slot_map = {r.slot_time: r for r in rows}

        today_slots = []
        published_today = 0
        for s in self.schedule_times:
            rec = slot_map.get(s)
            status = rec.status if rec else ("due" if s <= now_tash.strftime("%H:%M") else "waiting")
            if status == "published":
                published_today += 1
            today_slots.append({
                "time": s,
                "status": status,
                "msg_id": rec.telegram_message_id if rec else None,
            })

        queue_stats = await queue_service.get_queue_stats(session)

        return {
            "tashkent_time": now_tash.strftime("%H:%M:%S"),
            "today_date": today_str,
            "is_within_window": self.is_within_publishing_window(now_tash),
            "published_today": published_today,
            "total_slots": len(self.schedule_times),
            "next_slot": self.get_next_scheduled_slot(now_tash),
            "slots": today_slots,
            "queue": queue_stats,
        }


channel_scheduler = ChannelScheduler()
