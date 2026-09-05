import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.candidates.bootstrap import bootstrap_user
from app.config import settings
from app.database.db import init_db
from app.services import scan_all, scan_hh_chats
from app.telegram.handlers import router


logger = logging.getLogger(__name__)

TELEGRAM_RETRY_INITIAL_SECONDS = 5.0
TELEGRAM_RETRY_MAX_SECONDS = 60.0


async def wait_for_telegram(
    bot: Bot,
    *,
    initial_delay: float = TELEGRAM_RETRY_INITIAL_SECONDS,
    max_delay: float = TELEGRAM_RETRY_MAX_SECONDS,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> None:
    """Wait until Telegram API is reachable without killing the app process.

    Only transient Telegram network errors are retried. Authentication and
    other API errors still fail fast so configuration problems stay visible.
    """
    delay = initial_delay
    attempts = 0

    while True:
        try:
            await bot.me()
            if attempts:
                logger.info(
                    "Telegram API reachable after %d retry attempt(s)",
                    attempts,
                )
            return
        except TelegramNetworkError as exc:
            attempts += 1
            logger.warning(
                "Telegram API unavailable: %s; retrying in %.0fs",
                exc,
                delay,
            )
            await sleep(delay)
            delay = min(delay * 2, max_delay)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    await init_db()
    if settings.telegram_admin_chat_id.strip():
        await bootstrap_user(settings.telegram_admin_chat_id.strip(), "Owner")

    bot = Bot(settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(scan_all, "interval", minutes=settings.search_interval_minutes, args=[bot], max_instances=1, coalesce=True, next_run_time=datetime.now())
    if settings.hh_private_api_enabled and settings.hh_access_token:
        scheduler.add_job(scan_hh_chats, "interval", minutes=settings.hh_chat_interval_minutes, args=[bot], max_instances=1, coalesce=True)

    try:
        await wait_for_telegram(bot)
        scheduler.start()
        await dp.start_polling(bot, close_bot_session=False)
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
