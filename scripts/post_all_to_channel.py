"""Script to broadcast all listings in the database to the Telegram channel."""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.abspath("."))
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.listing import Listing
from src.services.notification_service import notification_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TARGET_CHANNEL = settings.CHANNEL_ID or "@joyliy_uz"


async def main():
    if not TARGET_CHANNEL:
        logger.error("Target channel is not configured in settings.CHANNEL_ID or TARGET_CHANNEL.")
        sys.exit(1)

    bot = Bot(token=settings.BOT_TOKEN)
    notification_service.set_bot(bot)

    logger.info("Connecting to database and fetching all listings...")
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Listing)
            .options(selectinload(Listing.classification))
            .order_by(Listing.id.asc())
        )
        res = await session.execute(stmt)
        listings = res.scalars().all()

    total = len(listings)
    logger.info("Found %d listings to broadcast to %s.", total, TARGET_CHANNEL)

    sent_count = 0
    failed_count = 0

    for idx, listing in enumerate(listings, start=1):
        try:
            logger.info(
                "[%d/%d] Sending ID %d: '%s' (%s, %s UZS)...",
                idx,
                total,
                listing.id,
                listing.title[:35],
                listing.district,
                listing.price_uzs,
            )
            success = await notification_service.send_to_channel(
                listing, channel_id=TARGET_CHANNEL
            )
            if success:
                sent_count += 1
            else:
                failed_count += 1

            # Polite pacing between posts to respect Telegram flood control (2.5s)
            await asyncio.sleep(2.5)

        except TelegramRetryAfter as e:
            wait_s = e.retry_after + 2
            logger.warning("Telegram flood control reached. Pausing for %d seconds...", wait_s)
            await asyncio.sleep(wait_s)
            # Retry this listing once
            try:
                success = await notification_service.send_to_channel(
                    listing, channel_id=TARGET_CHANNEL
                )
                if success:
                    sent_count += 1
            except Exception as retry_err:
                logger.error("Retry failed for ID %d: %s", listing.id, retry_err)
                failed_count += 1

        except Exception as err:
            logger.error("Error sending listing ID %d: %s", listing.id, err)
            failed_count += 1
            await asyncio.sleep(2.0)

    logger.info(
        "Broadcast completed! Total: %d, Successfully sent: %d, Failed: %d.",
        total,
        sent_count,
        failed_count,
    )
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
