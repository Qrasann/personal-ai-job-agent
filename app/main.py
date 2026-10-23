import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import BotCommand, MenuButtonCommands, ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.candidates.bootstrap import bootstrap_user
from app.config import settings
from app.database import repository as repo
from app.database.db import init_db
from app.services import scan_all, scan_hh_chats, retry_job_notifications
from app.sources.telegram_watch import retry_telegram_watch
from app.telegram.handlers import router
from app.telegram.settings_handlers import router as settings_router
from app.telegram.ui import LEGACY_REPLY_KEYBOARD_REMOVED_STATE


logger = logging.getLogger(__name__)

TELEGRAM_RETRY_INITIAL_SECONDS = 5.0
TELEGRAM_RETRY_MAX_SECONDS = 60.0
STARTUP_SCAN_MISFIRE_GRACE_SECONDS = 300

BOT_COMMANDS = (
    BotCommand(command="menu", description="Главное меню"),
    BotCommand(command="scan", description="Запустить поиск"),
    BotCommand(command="scanstatus", description="Статус поиска"),
    BotCommand(command="review", description="Good-вакансии"),
    BotCommand(command="stretch", description="Stretch-вакансии"),
    BotCommand(command="saved", description="Сохранённые вакансии"),
    BotCommand(command="jobs", description="Все совпадения"),
    BotCommand(command="applications", description="Отклики и пакеты"),
    BotCommand(command="resumes", description="CV Studio"),
    BotCommand(command="facts", description="Профиль кандидата"),
    BotCommand(command="settings", description="Настройки поиска"),
    BotCommand(command="help", description="Все команды"),
)


async def configure_telegram_ui(bot: Bot) -> None:
    await bot.set_my_commands(BOT_COMMANDS)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def remove_legacy_reply_keyboards(bot: Bot) -> None:
    """Remove the obsolete persistent keyboard once for every active user."""
    for user in await repo.list_active_users():
        if await repo.get_state(user.id, LEGACY_REPLY_KEYBOARD_REMOVED_STATE, "false") == "true":
            continue
        try:
            await bot.send_message(
                user.telegram_chat_id,
                "✅ Старая нижняя панель скрыта. Используй кнопку Menu или /menu.",
                reply_markup=ReplyKeyboardRemove(),
            )
        except Exception as exc:
            logger.warning(
                "Could not remove legacy Telegram keyboard for user %s (%s)",
                user.id,
                type(exc).__name__,
            )
            continue
        await repo.set_state(user.id, LEGACY_REPLY_KEYBOARD_REMOVED_STATE, "true")


def _schedule_jobs(scheduler: AsyncIOScheduler, bot: Bot) -> None:
    scheduler.add_job(
        scan_all,
        "interval",
        minutes=settings.search_interval_minutes,
        args=[bot],
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(),
        misfire_grace_time=STARTUP_SCAN_MISFIRE_GRACE_SECONDS,
    )
    scheduler.add_job(retry_telegram_watch, "interval", minutes=1, args=[bot],
                      id="telegram_watch_retry", max_instances=1, coalesce=True)
    scheduler.add_job(
        retry_job_notifications, "interval", minutes=1, args=[bot],
        id="job_alert_retry", max_instances=1, coalesce=True,
        next_run_time=datetime.now(),
    )
    if settings.hh_private_api_enabled and settings.hh_access_token:
        scheduler.add_job(
            scan_hh_chats,
            "interval",
            minutes=settings.hh_chat_interval_minutes,
            args=[bot],
            max_instances=1,
            coalesce=True,
        )


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
                "Telegram API unavailable (%s); retrying in %.0fs",
                type(exc).__name__,
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
    dp.include_router(settings_router)
    dp.include_router(router)

    scheduler = AsyncIOScheduler()
    _schedule_jobs(scheduler, bot)

    try:
        await wait_for_telegram(bot)
        await configure_telegram_ui(bot)
        await remove_legacy_reply_keyboards(bot)
        scheduler.start()
        await dp.start_polling(bot, close_bot_session=False)
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
