import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.candidates.bootstrap import bootstrap_user
from app.config import settings
from app.database.db import init_db
from app.services import scan_all, scan_hh_chats
from app.telegram.handlers import router


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
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
