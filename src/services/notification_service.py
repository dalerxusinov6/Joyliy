"""Notification Engine for matching, filtering, and dispatching listings with rate limiting."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta, time
from typing import List, Optional
from aiogram import Bot
from aiogram.types import InputMediaPhoto
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramNetworkError,
)
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.models.user import User, UserSearchPreference
from src.models.listing import Listing, NotificationHistory, ListingClassification
from src.classification.types import ClassificationLabel
from src.bot.formatter import (
    format_listing_message,
    get_listing_inline_keyboard,
    format_channel_message,
    get_channel_inline_keyboard,
    TASHKENT_TZ,
)

logger = logging.getLogger(__name__)


def is_in_quiet_hours(
    pref: UserSearchPreference, now_dt: Optional[datetime] = None
) -> bool:
    """
    Check if the current time in Tashkent falls inside the user's configured quiet hours.
    Handles overnight spans (e.g. 23:00 to 08:00).
    """
    if not pref.quiet_hours_enabled:
        return False

    current_tashkent_dt = (now_dt or datetime.now(timezone.utc)).astimezone(TASHKENT_TZ)
    current_time = current_tashkent_dt.time()

    try:
        sh, sm = map(int, pref.quiet_hours_start.split(":"))
        eh, em = map(int, pref.quiet_hours_end.split(":"))
        start_time = time(sh, sm)
        end_time = time(eh, em)
    except Exception:
        # Fallback to defaults
        start_time = time(23, 0)
        end_time = time(8, 0)

    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        # Crosses midnight: e.g. 23:00 to 08:00
        return current_time >= start_time or current_time <= end_time


def matches_user_preference(listing: Listing, pref: UserSearchPreference) -> bool:
    """
    Evaluate whether a listing satisfies all user search preferences.
    """
    if not pref.notifications_enabled:
        return False

    # 1. District filter (empty list means all districts)
    if pref.districts:
        if not listing.district or listing.district not in pref.districts:
            return False

    # 2. Price filter
    if listing.price_uzs is not None:
        if pref.min_price is not None and listing.price_uzs < pref.min_price:
            return False
        if pref.max_price is not None and listing.price_uzs > pref.max_price:
            return False

    # 3. Room count filter (empty list means any room count)
    if pref.rooms:
        if listing.rooms is None or listing.rooms not in pref.rooms:
            return False

    # 4. Area filter
    if listing.area is not None:
        if pref.min_area is not None and listing.area < pref.min_area:
            return False
        if pref.max_area is not None and listing.area > pref.max_area:
            return False

    # 5. Owner-only and Agency inclusion
    classification = None
    if "classification" in listing.__dict__:
        classification = listing.__dict__["classification"]
    else:
        try:
            from sqlalchemy.orm.attributes import NO_VALUE
            from sqlalchemy.orm import inspect as sa_inspect
            insp = sa_inspect(listing)
            loaded = insp.attrs.classification.loaded_value
            if loaded is not NO_VALUE:
                classification = loaded
        except Exception:
            classification = None

    label = classification.label if classification else ClassificationLabel.NEEDS_REVIEW.value

    if pref.owner_only:
        if label != ClassificationLabel.LIKELY_OWNER.value:
            return False
    elif not pref.include_agency:
        if label == ClassificationLabel.LIKELY_AGENT.value:
            return False

    # 6. Max listing age: only applies when reliable publication timestamp exists
    if pref.max_listing_age_hours is not None and listing.publication_date is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=pref.max_listing_age_hours)
        if listing.publication_date < cutoff:
            return False

    return True


class NotificationService:
    """Handles dispatching notifications to matching users with flood control."""

    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot

    def set_bot(self, bot: Bot) -> None:
        self.bot = bot

    async def send_to_channel(
        self,
        listing: Listing,
        channel_id: Optional[str] = None,
        max_retries: int = 3,
    ) -> bool:
        """
        Send a new listing with image(s) to a Telegram channel.
        If multiple images exist, sends an album (media group), then the action button.
        If single image, sends a photo with inline keyboard.
        If no image, sends a text message with inline keyboard.
        """
        target = channel_id or settings.CHANNEL_ID
        if not target:
            return False
        if not self.bot:
            logger.warning("Bot instance not configured in NotificationService.")
            return False

        caption = format_channel_message(listing)
        reply_markup = get_channel_inline_keyboard(listing)
        images = [img for img in (listing.image_urls or []) if img and img.startswith("http")]

        for attempt in range(1, max_retries + 1):
            try:
                if len(images) > 1:
                    # Send media group (album) with caption on the first image
                    media = [
                        InputMediaPhoto(
                            media=url,
                            caption=caption if idx == 0 else None,
                            parse_mode="HTML",
                        )
                        for idx, url in enumerate(images[:8])  # OLX high-res photos (max 8)
                    ]
                    try:
                        await self.bot.send_media_group(chat_id=target, media=media)
                        # Send button below album
                        await self.bot.send_message(
                            chat_id=target,
                            text=f"👉 <b>{listing.title}</b>",
                            parse_mode="HTML",
                            reply_markup=reply_markup,
                        )
                        return True
                    except Exception as album_err:
                        logger.warning("Failed to send album to channel %s: %s, falling back to single photo", target, album_err)
                        if images:
                            await self.bot.send_photo(
                                chat_id=target,
                                photo=images[0],
                                caption=caption,
                                parse_mode="HTML",
                                reply_markup=reply_markup,
                            )
                            return True

                elif len(images) == 1:
                    try:
                        await self.bot.send_photo(
                            chat_id=target,
                            photo=images[0],
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup,
                        )
                        return True
                    except Exception as img_err:
                        logger.warning("Failed to send photo to channel %s: %s, falling back to text", target, img_err)
                        await self.bot.send_message(
                            chat_id=target,
                            text=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup,
                        )
                        return True
                else:
                    await self.bot.send_message(
                        chat_id=target,
                        text=caption,
                        parse_mode="HTML",
                        reply_markup=reply_markup,
                    )
                    return True

            except TelegramRetryAfter as e:
                wait_secs = e.retry_after + 1
                logger.warning("Flood control on channel %s: waiting %d s", target, wait_secs)
                await asyncio.sleep(wait_secs)
            except TelegramForbiddenError:
                logger.error("Bot is not an administrator with post permissions in channel %s", target)
                return False
            except TelegramBadRequest as e:
                logger.error("Telegram bad request posting to channel %s: %s", target, e)
                return False
            except Exception as e:
                logger.error("Error posting to channel %s (attempt %d/%d): %s", target, attempt, max_retries, e)
                if attempt < max_retries:
                    await asyncio.sleep(2.0 * attempt)
                else:
                    return False
        return False

    async def send_to_user_with_retry(
        self,
        telegram_id: int,
        listing: Listing,
        max_retries: int = 3,
    ) -> bool:
        """
        Send a listing message with retry logic for Telegram flood control.
        """
        if not self.bot:
            logger.error("Bot instance not configured in NotificationService.")
            return False

        message_text = format_listing_message(listing)
        reply_markup = get_listing_inline_keyboard(listing)

        # Attempt with image if available
        photo_url = listing.image_urls[0] if listing.image_urls else None

        for attempt in range(1, max_retries + 1):
            try:
                if photo_url:
                    try:
                        await self.bot.send_photo(
                            chat_id=telegram_id,
                            photo=photo_url,
                            caption=message_text,
                            reply_markup=reply_markup,
                        )
                        return True
                    except Exception as img_err:
                        # Fallback to plain text if photo fails (e.g. invalid url/format)
                        logger.debug("Photo send failed for %s, falling back to text: %s", photo_url, img_err)
                        await self.bot.send_message(
                            chat_id=telegram_id,
                            text=message_text,
                            reply_markup=reply_markup,
                        )
                        return True
                else:
                    await self.bot.send_message(
                        chat_id=telegram_id,
                        text=message_text,
                        reply_markup=reply_markup,
                    )
                    return True

            except TelegramRetryAfter as e:
                wait_secs = e.retry_after + 1
                logger.warning(
                    "Telegram flood control triggered. Waiting %d seconds before retry.",
                    wait_secs,
                )
                await asyncio.sleep(wait_secs)
            except TelegramForbiddenError:
                logger.info("Bot was blocked by user %d.", telegram_id)
                raise
            except TelegramBadRequest as e:
                logger.warning("Telegram bad request for chat %d: %s", telegram_id, e)
                return False
            except TelegramNetworkError as e:
                logger.warning("Network error sending to %d (attempt %d): %s", telegram_id, attempt, e)
                await asyncio.sleep(1.5 * attempt)
            except Exception as e:
                logger.error("Unexpected error delivering to %d: %s", telegram_id, e)
                return False

        return False

    async def dispatch_new_listing(
        self, session: AsyncSession, listing: Listing
    ) -> int:
        """
        Find all active users whose preferences match this new listing,
        and dispatch notifications while respecting quiet hours, deduplication, and rate limits.
        """
        # Step 1: Query all active users with their preferences
        stmt = (
            select(User)
            .join(UserSearchPreference, UserSearchPreference.user_id == User.id)
            .options(selectinload(User.preference))
            .where(
                and_(
                    User.is_active.is_(True),
                    UserSearchPreference.notifications_enabled.is_(True),
                )
            )
        )
        res = await session.execute(stmt)
        users = res.scalars().all()

        sent_count = 0
        now_utc = datetime.now(timezone.utc)

        # Rate limiter pace
        delay_between_msgs = 1.0 / max(1.0, settings.MAX_NOTIFICATIONS_PER_SECOND)

        for user in users:
            pref = user.preference
            if not pref:
                continue

            # Check quiet hours
            if is_in_quiet_hours(pref, now_utc):
                continue

            # Check search preferences match
            if not matches_user_preference(listing, pref):
                continue

            # Check deduplication: was this listing already sent to this user?
            check_stmt = select(NotificationHistory).where(
                and_(
                    NotificationHistory.user_id == user.id,
                    NotificationHistory.listing_id == listing.id,
                )
            )
            already_sent = (await session.execute(check_stmt)).scalar_one_or_none()
            if already_sent:
                continue

            # Send notification
            delivered = False
            error_msg = None

            try:
                delivered = await self.send_to_user_with_retry(
                    telegram_id=user.telegram_id,
                    listing=listing,
                )
            except TelegramForbiddenError:
                # User blocked bot; deactivate
                user.is_active = False
                error_msg = "Bot blocked by user"
            except Exception as e:
                error_msg = str(e)

            # Record in notification history (idempotent write)
            notif_rec = NotificationHistory(
                user_id=user.id,
                listing_id=listing.id,
                sent_at=now_utc,
                status="delivered" if delivered else "failed",
                error_message=error_msg,
            )
            session.add(notif_rec)
            await session.commit()

            if delivered:
                sent_count += 1

            # Conservative rate limiting
            await asyncio.sleep(delay_between_msgs)

        return sent_count


notification_service = NotificationService()
