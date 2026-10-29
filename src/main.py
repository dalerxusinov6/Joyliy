"""Main application entrypoint orchestrating Bot, Monitor Worker, and REST API."""

import argparse
import asyncio
import logging
import os
import signal
import sys
import uvicorn

from src.config import settings
from src.database import init_db
from src.bot.bot_instance import create_bot_and_dispatcher
from src.services.monitor_worker import monitor_worker
from src.api.app import create_app
from src.api.routes import register_bot_webhook

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("joyliy")


async def run_application(mode: str = "all"):
    """Run specified components with graceful lifecycle management."""
    logger.info("Initializing Joyliy Apartment Platform (mode: %s)...", mode)

    # 1. Initialize Database schema
    await init_db()
    logger.info("Database schema initialized.")

    bot = None
    dp = None
    server = None

    tasks = []

    # 2. Setup Bot & Dispatcher if requested
    if mode in ("all", "bot"):
        bot, dp = create_bot_and_dispatcher()
        if bot and dp:
            monitor_worker.set_bot(bot)
            logger.info("Telegram Bot and Dispatcher configured.")
        else:
            logger.warning("Telegram Bot is disabled (valid BOT_TOKEN not configured).")

    # 3. Setup Monitor Worker if requested
    if mode in ("all", "worker"):
        monitor_worker.start()
        logger.info("Background Monitor Worker started.")

    # 4. Setup FastAPI Server if requested
    server_task = None
    if mode in ("all", "api"):
        app = create_app()
        config = uvicorn.Config(
            app=app,
            host=settings.HOST,
            port=settings.PORT,
            log_level=settings.LOG_LEVEL.lower(),
        )
        server = uvicorn.Server(config)
        server_task = asyncio.create_task(server.serve())
        logger.info("FastAPI web server bound to %s:%d", settings.HOST, settings.PORT)

    # Graceful shutdown handler
    stop_event = asyncio.Event()

    def handle_signal(*args):
        logger.info("Shutdown signal received. Initiating graceful shutdown...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            pass

    # 5. Start Telegram Bot (Webhook on Render/Cloud, Long-Polling locally)
    if mode in ("all", "bot") and dp and bot:
        # Determine whether to use webhook or long polling
        bot_mode = (os.getenv("BOT_MODE") or settings.BOT_MODE or "auto").lower()
        render_external_url = (
            os.getenv("RENDER_EXTERNAL_URL")
            or (settings.WEBSITE_URL if "onrender.com" in settings.WEBSITE_URL else None)
        )
        is_cloud_render = bool(
            os.getenv("RENDER")
            or os.getenv("RENDER_SERVICE_ID")
            or os.getenv("RENDER_INSTANCE_ID")
            or render_external_url
            or ("onrender.com" in settings.WEBSITE_URL)
            or (os.getenv("PORT") and os.getenv("PORT") != "8000")
        )

        use_webhook = (bot_mode == "webhook") or (bot_mode != "polling" and is_cloud_render)

        if use_webhook:
            register_bot_webhook(bot, dp)
            webhook_base = render_external_url or "https://joyliy.onrender.com"
            webhook_url = f"{webhook_base.rstrip('/')}/api/telegram-webhook"
            try:
                # Reset webhook and drop backlog to ensure clean webhook registration
                await bot.delete_webhook(drop_pending_updates=True)
                await asyncio.sleep(0.5)
                await bot.set_webhook(
                    url=webhook_url,
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"],
                )
                logger.info("Telegram Bot Webhook configured successfully: %s", webhook_url)
            except Exception as err:
                logger.error("Failed to set Telegram webhook: %s", err)
        else:
            logger.info("Starting Telegram Bot long-polling (local mode)...")
            async def run_bot_polling():
                # Reset webhook and drop backlog to ensure clean polling state
                try:
                    await bot.delete_webhook(drop_pending_updates=True)
                    logger.info("Telegram webhook deleted and pending updates cleared.")
                except Exception as e:
                    logger.warning("Could not delete webhook: %s", e)

                while not stop_event.is_set():
                    try:
                        logger.info("Starting aiogram dispatcher polling...")
                        await dp.start_polling(bot, handle_signals=False)
                    except Exception as exc:
                        exc_str = str(exc)
                        if "TelegramConflictError" in str(type(exc)) or "terminated by other getUpdates" in exc_str or "Conflict" in exc_str:
                            logger.warning("Telegram conflict detected (another bot instance running). Backing off for 15s...")
                            try:
                                await asyncio.wait_for(stop_event.wait(), timeout=15.0)
                            except asyncio.TimeoutError:
                                pass
                        else:
                            logger.warning("Telegram bot polling error (%s). Re-checking in 5s...", exc)
                            try:
                                await asyncio.wait_for(stop_event.wait(), timeout=5.0)
                            except asyncio.TimeoutError:
                                pass
            tasks.append(asyncio.create_task(run_bot_polling()))

    try:
        # Wait until stopped or primary task finishes
        if server_task:
            stop_task = asyncio.create_task(stop_event.wait())
            await asyncio.wait([server_task, stop_task], return_when=asyncio.FIRST_COMPLETED)
        elif tasks:
            stop_task = asyncio.create_task(stop_event.wait())
            await asyncio.wait(tasks + [stop_task], return_when=asyncio.FIRST_COMPLETED)
        else:
            await stop_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Shutting down components...")
        # Stop monitor worker
        await monitor_worker.stop()

        # Stop uvicorn server
        if server:
            server.should_exit = True

        # Close Telegram bot session
        if bot:
            await bot.session.close()

        logger.info("Joyliy Platform shutdown complete.")


def main():
    """CLI parser and main entry."""
    parser = argparse.ArgumentParser(description="Joyliy Apartment Rental Bot and Monitor")
    parser.add_argument(
        "--mode",
        choices=["all", "bot", "worker", "api"],
        default="all",
        help="Subsystem mode to run (default: all)",
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_application(mode=args.mode))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application exited.")


if __name__ == "__main__":
    main()

