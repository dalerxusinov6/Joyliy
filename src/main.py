"""Main application entrypoint orchestrating Bot, Monitor Worker, and REST API."""

import argparse
import asyncio
import logging
import signal
import sys
import uvicorn

from src.config import settings
from src.database import init_db
from src.bot.bot_instance import create_bot_and_dispatcher
from src.services.monitor_worker import monitor_worker
from src.api.app import create_app

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
        monitor_worker.set_bot(bot)
        logger.info("Telegram Bot and Dispatcher configured.")

    # 3. Setup Monitor Worker if requested
    if mode in ("all", "worker"):
        monitor_worker.start()
        logger.info("Background Monitor Worker started.")

    # 4. Setup FastAPI Server if requested
    if mode in ("all", "api"):
        app = create_app()
        config = uvicorn.Config(
            app=app,
            host=settings.HOST,
            port=settings.PORT,
            log_level=settings.LOG_LEVEL.lower(),
        )
        server = uvicorn.Server(config)
        tasks.append(asyncio.create_task(server.serve()))
        logger.info("FastAPI web server bound to %s:%d", settings.HOST, settings.PORT)

    # 5. Start Telegram Polling if bot is active
    if mode in ("all", "bot") and dp and bot:
        logger.info("Starting Telegram Bot long-polling...")
        tasks.append(asyncio.create_task(dp.start_polling(bot)))

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
            # Signal handling on non-POSIX platforms
            pass

    try:
        # Wait until stopped or tasks finish
        if tasks:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
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

