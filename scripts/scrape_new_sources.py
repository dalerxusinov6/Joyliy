"""Script to scrape and ingest listings from joymee.uz and realt24.uz into Joyliy."""

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot

from src.config import settings
from src.database import AsyncSessionLocal
from src.providers.joymee_http import JoymeeHttpListingProvider
from src.providers.realt24_http import Realt24HttpListingProvider
from src.services.listing_service import listing_service
from src.services.notification_service import notification_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def main():
    bot = None
    if settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
        notification_service.set_bot(bot)
        logger.info("Bot initialized for channel broadcasts (%s).", settings.CHANNEL_ID)

    joymee_provider = JoymeeHttpListingProvider(max_pages=2, max_items=25)
    realt24_provider = Realt24HttpListingProvider(max_pages=2, max_items=25)

    providers = [joymee_provider, realt24_provider]

    total_scraped = 0
    total_new = 0
    total_broadcast = 0

    async with AsyncSessionLocal() as session:
        for provider in providers:
            logger.info("==========================================")
            logger.info("Scraping from %s...", provider.name)
            logger.info("==========================================")

            try:
                raw_items = await provider.fetch_listings()
                logger.info("Successfully fetched %d items from %s", len(raw_items), provider.name)
                total_scraped += len(raw_items)

                for item in raw_items:
                    try:
                        listing, is_new = await listing_service.ingest_raw_listing(session, item)
                        if is_new:
                            total_new += 1
                            logger.info(
                                " [NEW] %s | %s | %s UZS | %s | %s",
                                item.source,
                                item.title[:35],
                                item.price_uzs,
                                item.district,
                                item.contact_phone or "No phone",
                            )

                            # Broadcast to channel if configured
                            if bot and settings.CHANNEL_ID:
                                try:
                                    await notification_service.send_to_channel(listing)
                                    total_broadcast += 1
                                    logger.info(" Broadcasted listing %d to channel %s", listing.id, settings.CHANNEL_ID)
                                    await asyncio.sleep(2.0)  # Gentle rate limit for Telegram
                                except Exception as bc_err:
                                    logger.warning("Failed to broadcast listing %d: %s", listing.id, bc_err)
                        else:
                            logger.debug(" [EXISTS] %s", item.canonical_url)
                    except Exception as ing_err:
                        logger.error("Error ingesting item %s: %s", item.canonical_url, ing_err)

            except Exception as prov_err:
                logger.error("Provider %s failed: %s", provider.name, prov_err, exc_info=True)

    if bot:
        await bot.session.close()

    logger.info("==========================================")
    logger.info("Scrape Summary:")
    logger.info("  Total scraped: %d", total_scraped)
    logger.info("  Newly ingested: %d", total_new)
    logger.info("  Broadcasted to channel: %d", total_broadcast)
    logger.info("==========================================")


if __name__ == "__main__":
    asyncio.run(main())

