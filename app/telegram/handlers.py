from __future__ import annotations

import asyncio
import html
import json
import io
import time
import uuid
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.candidates.bootstrap import bootstrap_user
from app.candidates.importer import (
    MAX_DOCUMENT_BYTES, ResumeImportError, extract_resume_text,
    guess_language, propose_facts, resume_fingerprint, review_proposals,
)
from app.config import settings
from app.database import repository as repo
from app.candidates.fact_types import ALLOWED_EXPERIENCE_TYPES, experience_type_label, normalize_experience_type
from app.database.db import current_schema_version, expected_schema_version
from app.geo.countries import all_supported_countries, country_config, normalize_country
from app.services import apply_match, get_vacancy_comparison, get_vacancy_details, prepare_match, ingest_and_match, scan_for_user, scan_hh_chats, hh_client
from app.sources.adapters.telegram_ingest import parse_forwarded_job, parse_telegram_job
from app.sources.telegram_watch import change_subscription, consume_channel_post, consume_forwarded_job, render_subscriptions, retry_pending, watch_state
from app.telegram.vacancy_view import render_fact_comparison, render_job_details, render_jobs_list, render_queue_card
from app.telegram.source_display import manual_source_line
from app.telegram.ui import jobs_keyboard, review_keyboard, saved_keyboard, stretch_keyboard, vacancy_details_keyboard
from app.sources.registry import build_source_plan
from app.search.preferences import relocation_first_allows, source_enabled
from app.search.user_preferences import parse_salary_command, update_blacklist, update_salary
from app.version import current_version
from app.telegram.multicommand import (
    MultiCommandError,
    MultiCommandFilter,
    build_child_message,
    parse_multi_commands,
)

router = Router()
_ACTIVE_SCAN_TASKS: dict[int, asyncio.Task] = {}
_PENDING_RESUME_IMPORTS: dict[str, dict] = {}


async def _save_scan_dashboard(user_id: int, *, reset: bool = False, **values) -> None:
    current = {}
    if not reset:
        try:
            current = json.loads(await repo.get_state(user_id, "scan_dashboard", "{}"))
        except (TypeError, ValueError):
            pass
    current.update(values)
    await repo.set_state(user_id, "scan_dashboard", json.dumps(current, ensure_ascii=False))


async def _user(message: Message):
    return await repo.get_user_by_chat(message.chat.id)


async def _require_user(message: Message):
    user = await _user(message)
    if not user:
        await message.answer("⛔ Профиль ещё не зарегистрирован. Владелец использует /start; для нового пользователя — /register <код>.")
        return None
    return user


async def _first_search(user_id: int):
    profile = await repo.active_profile(user_id)
    if not profile:
        return None, None
    searches = await repo.list_search_profiles(profile.id)
    return profile, searches[0] if searches else None


async def _search_for_scope(user_id: int, scope: str):
    profile = await repo.active_profile(user_id)
    searches = await repo.list_search_profiles(profile.id) if profile else []
    search = next((item for item in searches if item.kind == scope), None)
    if not search and scope == "career" and len(searches) == 1:
        legacy = searches[0]
        if legacy.kind == "employment" and (legacy.settings or {}).get("search_strategy") != "relocation_first":
            search = legacy
    return search


def _missing_search_scope(scope: str) -> str:
    if scope == "relocation":
        return "❌ Профиль Relocation-first не активен. Включи его командой /parallelsearch on."
    return "❌ Профиль Career-first не найден среди активных поисков."

@router.message(MultiCommandFilter())
async def multi_command(message: Message, bot: Bot) -> None:
    try:
        commands = parse_multi_commands(message.text)
    except MultiCommandError as exc:
        await message.answer(
            f"❌ {html.escape(str(exc))}",
            parse_mode="HTML",
        )
        return

    if not commands:
        return

    for command_text in commands:
        child_message = build_child_message(
            message,
            command_text,
        )

        await router.propagate_event(
            "message",
            child_message,
            bot=bot,
        )

def _main_menu_text() -> str:
    return (
        "🤖 <b>Personal AI Job Agent</b>\n\n"
        "🔎 <b>Поиск и очереди</b>\n"
        "/scan — запустить поиск сейчас\n"
        "/scanstatus — состояние последнего сканирования\n"
        "/review — разобрать Good-вакансии\n"
        "/stretch — разобрать Stretch-вакансии\n"
        "/saved — сохранённые вакансии\n"
        "/jobs — совпадения по рейтингу\n"
        "/jobs career|relocation — отдельное направление\n"
        "/jobs relocation below — ручной просмотр ниже порога\n\n"
        "⚙️ <b>Настройки поиска</b>\n"
        "/roles — текущие роли\n"
        "/role DevOps Engineer — выбрать основную роль\n"
        "/roleadd Linux Administrator — добавить роль\n"
        "/mode — направления поиска\n"
        "/city Тверь — локальный город\n"
        "/domestic_relocation on|off — переезд по РФ\n"
        "/country — текущая страна\n"
        "/targets [all|career|relocation] GE[,CA] — рынки поиска\n"
        "/settings — текущие настройки\n\n"
        "/salary — зарплатные ориентиры\n"
        "/blacklist — исключаемые слова\n\n"
        "🧠 <b>Профиль и вакансии</b>\n"
        "/job 25 — подробности вакансии\n"
        "/compare 25 — сравнить вакансию с профилем\n"
        "/facts — факты кандидата\n"
        "/import — импортировать резюме PDF/DOCX/TXT\n"
        "/resumes — варианты резюме\n"
        "/sources — источники вакансий\n"
        "/channels — подписки на Telegram-каналы и статистика\n\n"
        "🤖 <b>Агент</b>\n"
        "/status — состояние агента\n"
        "/chats — проверить HH-переписку\n"
        "/pause /resume — остановить или возобновить поиск\n"
        "/help — показать это меню\n\n"
        "Перешли сюда пост с вакансией из Telegram — он попадёт в тот же pipeline."
    )

@router.message(CommandStart())
async def start(message: Message) -> None:
    existing = await _user(message)
    is_owner = not settings.telegram_admin_chat_id.strip() or str(message.chat.id) == settings.telegram_admin_chat_id.strip()
    if not existing and is_owner:
        existing, _ = await bootstrap_user(message.chat.id, message.from_user.full_name if message.from_user else "")
    if not existing:
        await message.answer(
            "🤖 Job Agent v3\n\nЭтот экземпляр уже работает в multi-user режиме, но самостоятельная регистрация выключена. "
            "Если владелец включил приглашения, используй /register <код>."
        )
        return
    await bootstrap_user(existing.telegram_chat_id, existing.display_name)
    await message.answer(_main_menu_text(), parse_mode="HTML")


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    await message.answer(_main_menu_text(), parse_mode="HTML")


@router.message(Command("register"))
async def register(message: Message) -> None:
    if await _user(message):
        await message.answer("✅ Ты уже зарегистрирован.")
        return
    if not settings.multi_user_registration:
        await message.answer("⛔ Регистрация новых пользователей отключена владельцем.")
        return
    parts = (message.text or "").split(maxsplit=1)
    code = parts[1].strip() if len(parts) > 1 else ""
    if not settings.registration_invite_code or code != settings.registration_invite_code:
        await message.answer("❌ Неверный invite code.")
        return
    user, _ = await bootstrap_user(message.chat.id, message.from_user.full_name if message.from_user else "")
    await message.answer(f"✅ Профиль создан. User ID: {user.id}. Теперь выполни /country и /targets.")


@router.message(Command("version"))
async def version(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    schema = await current_schema_version()
    expected = expected_schema_version()
    await message.answer(
        f"🤖 <b>Job Agent v{html.escape(current_version())}</b>\n"
        f"DB schema: <b>{schema}</b> / {expected}\n"
        f"Migration: {'✅ OK' if schema == expected else '⚠️ CHECK'}",
        parse_mode="HTML",
    )


@router.message(Command("status"))
async def status(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    st = await repo.stats(user.id)
    paused = await repo.get_state(user.id, "paused", "false") == "true"
    profile = await repo.active_profile(user.id)
    await message.answer(
        f"🤖 <b>JOB AGENT v{html.escape(current_version())}</b>\n\n"
        f"Статус: {'⏸ PAUSED' if paused else '🟢 ACTIVE'}\n"
        f"Профиль: {html.escape(profile.name if profile else '—')}\n"
        f"Основная роль: {html.escape(profile.target_role if profile else '—')}\n"
        f"Базовая страна: {html.escape(user.current_country or 'RU')}\n"
        f"Обработано вакансий: {st['matches']}\n"
        f"Подходящих/уведомлённых: {st['notified']}\n"
        f"Отфильтровано/дубликаты: {st['filtered']}\n"
        f"Откликов: {st['applications']}\n"
        f"LLM: {'ON' if settings.openai_api_key else 'fallback'}\n"
        f"HH поиск: PUBLIC/ANONYMOUS\n"
        f"HH private actions: {'ON' if hh_client.private_api_available else 'OFF'}\n"
        f"Auto apply: {'ON' if settings.auto_apply else 'OFF'}",
        parse_mode="HTML",
    )


@router.message(Command("pause"))
async def pause(message: Message) -> None:
    user = await _require_user(message)
    if user:
        await repo.set_state(user.id, "paused", "true")
        await message.answer("⏸ Автоматический поиск для твоего профиля остановлен.")


@router.message(Command("resume"))
async def resume_agent(message: Message) -> None:
    user = await _require_user(message)
    if user:
        await repo.set_state(user.id, "paused", "false")
        await message.answer("🟢 Автоматический поиск возобновлён.")


@router.message(Command("salary"))
async def salary_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    searches = await repo.list_search_profiles(profile.id) if profile else []
    if not searches:
        await message.answer("❌ Профиль поиска не найден.")
        return
    text = (message.text or "").strip()
    if len(text.split()) == 1:
        cfg = searches[0].settings or {}
        def show(key: str) -> str:
            values = cfg.get(f"{key}_salary") or (cfg.get("minimum_salary", {}) if key == "minimum" else {})
            return ", ".join(f"{currency} {amount:,}".replace(",", " ") for currency, amount in sorted(values.items())) or "не задана"
        await message.answer(
            "💰 Зарплатные ориентиры\n"
            f"Текущая: {show('current')}\nЖелаемая: {show('desired')}\nМесячный минимум для оценки: {show('minimum')}\n\n"
            "Формат: /salary current|desired|minimum USD 3000; очистить: /salary desired USD clear"
        )
        return
    try:
        kind, currency, amount = parse_salary_command(text)
    except ValueError as exc:
        await message.answer("❌ " + str(exc))
        return
    for search in searches:
        await repo.update_search_settings(search.id, update_salary(search.settings or {}, kind, currency, amount))
    await message.answer(f"✅ {'Очищено' if amount is None else 'Сохранено'}: {kind} {currency}" + (f" {amount:,}".replace(",", " ") if amount else ""))


@router.message(Command("blacklist"))
async def blacklist_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    searches = await repo.list_search_profiles(profile.id) if profile else []
    if not searches:
        await message.answer("❌ Профиль поиска не найден.")
        return
    parts = (message.text or "").split(maxsplit=2)
    cfg = searches[0].settings or {}
    if len(parts) == 1:
        terms = cfg.get("exclude_terms") or []
        await message.answer("🚫 Исключаемые слова: " + (", ".join(terms) or "нет") + "\nДобавить: /blacklist add <слово>\nУдалить: /blacklist remove <слово>\nОчистить: /blacklist clear")
        return
    action = parts[1].casefold()
    term = parts[2].strip() if len(parts) == 3 else ""
    if action not in {"add", "remove", "clear"} or (action != "clear" and not term):
        await message.answer("Формат: /blacklist add|remove <слово> или /blacklist clear")
        return
    for search in searches:
        await repo.update_search_settings(search.id, update_blacklist(search.settings or {}, action, term))
    await message.answer("✅ Blacklist обновлён.")


@router.message(Command("roles"))
async def roles(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile, search = await _first_search(user.id)
    queries = list((search.settings or {}).get("queries") or ([profile.target_role] if profile else []))
    await message.answer("🎯 <b>Ищу роли:</b>\n" + "\n".join(f"• {html.escape(x)}" for x in queries), parse_mode="HTML")


@router.message(Command("role"))
async def role(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile, search = await _first_search(user.id)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        queries = list((search.settings or {}).get("queries") or ([profile.target_role] if profile else []))
        await message.answer("Основная роль: " + html.escape(queries[0] if queries else "не задана"), parse_mode="HTML")
        return
    value = parts[1].strip()
    if not value:
        return
    cfg = dict(search.settings or {})
    cfg["queries"] = [value]
    await repo.update_search_settings(search.id, cfg)
    await repo.set_profile_target_role(profile.id, value)
    await message.answer(f"✅ Основная роль поиска: <b>{html.escape(value)}</b>.", parse_mode="HTML")


@router.message(Command("roleadd"))
async def roleadd(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile, search = await _first_search(user.id)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1 or not parts[1].strip():
        await message.answer("Использование: /roleadd Infrastructure Engineer")
        return
    value = parts[1].strip()
    cfg = dict(search.settings or {})
    queries = list(cfg.get("queries") or [profile.target_role])
    if value not in queries:
        queries.append(value)
    cfg["queries"] = queries
    await repo.update_search_settings(search.id, cfg)
    await message.answer(f"✅ Добавлена роль: <b>{html.escape(value)}</b>.", parse_mode="HTML")


@router.message(Command("mode"))
async def mode(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    cfg = dict(search.settings or {})
    modes = dict(cfg.get("modes") or {"local_ru": True, "remote_international": True, "relocation": True})
    parts = (message.text or "").split()
    aliases = {"local": "local_ru", "russia": "local_ru", "ru": "local_ru", "remote": "remote_international", "relocation": "relocation", "relocate": "relocation"}
    if len(parts) == 3:
        key = aliases.get(parts[1].casefold())
        value = parts[2].casefold()
        if not key or value not in {"on", "off"}:
            await message.answer("Использование: /mode local on|off, /mode remote on|off, /mode relocation on|off")
            return
        modes[key] = value == "on"
        cfg["modes"] = modes
        await repo.update_search_settings(search.id, cfg)
    lines = [
        "🧭 <b>Режимы поиска</b>",
        f"🇷🇺 Россия: {'ON' if modes.get('local_ru', True) else 'OFF'}",
        f"🌍 International remote: {'ON' if modes.get('remote_international', True) else 'OFF'}",
        f"✈️ Relocation: {'ON' if modes.get('relocation', True) else 'OFF'}",
    ]
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("settings"))
async def search_settings(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile, search = await _first_search(user.id)
    cfg = search.settings or {}
    modes = cfg.get("modes") or {}
    queries = cfg.get("queries") or [profile.target_role]
    minimum = (cfg.get("minimum_salary") or {}).get("RUB")
    text = (
        "⚙️ <b>Настройки поиска</b>\n\n"
        f"Роли: {html.escape(', '.join(queries))}\n"
        f"Россия: {'ON' if modes.get('local_ru', True) else 'OFF'}\n"
        f"Город: {html.escape(str(cfg.get('local_city') or 'не задан'))}\n"
        f"Переезд по РФ: {'ON' if cfg.get('domestic_relocation', False) else 'OFF'}\n"
        f"International remote: {'ON' if modes.get('remote_international', True) else 'OFF'}\n"
        f"Relocation: {'ON' if modes.get('relocation', True) else 'OFF'}\n"
        f"Мин. РФ зарплата: {minimum or 'не задана'} RUB net\n"
        f"Notify score: {cfg.get('notify_min_score', 65)}+"
    )
    await message.answer(text, parse_mode="HTML")



@router.message(Command("city"))
async def city(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    if not search:
        await message.answer("❌ Профиль поиска не найден.")
        return
    current = dict(search.settings or {})
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        await message.answer("🏙 Текущий город: " + str(current.get("local_city") or "не задан"))
        return
    value = parts[1].strip()
    if value.casefold() == "clear":
        current.pop("local_city", None)
        search.settings = current
        await repo.update_search_settings(search.id, current)
        await message.answer("✅ Локальный город очищен.")
        return
    current["local_city"] = value
    search.settings = current
    await repo.update_search_settings(search.id, current)
    await message.answer("✅ Локальный город: " + html.escape(value), parse_mode="HTML")


@router.message(Command("domestic_relocation"))
async def domestic_relocation(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    if not search:
        await message.answer("❌ Профиль поиска не найден.")
        return
    current = dict(search.settings or {})
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        state = "ON" if current.get("domestic_relocation", False) else "OFF"
        await message.answer("🚆 Переезд по РФ: " + state)
        return
    value = parts[1].strip().casefold()
    if value not in {"on", "off"}:
        await message.answer("Использование: /domestic_relocation on|off")
        return
    current["domestic_relocation"] = value == "on"
    search.settings = current
    await repo.update_search_settings(search.id, current)
    state = "ON" if current["domestic_relocation"] else "OFF"
    await message.answer("✅ Переезд по РФ: " + state)

@router.message(Command("country"))
async def country(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        supported = ", ".join(f"{c}={n}" for c, n in all_supported_countries())
        await message.answer(f"🌍 Сейчас: <b>{html.escape(user.current_country or 'не задано')}</b>\nНастроены: {html.escape(supported)}", parse_mode="HTML")
        return
    code = normalize_country(parts[1])
    if not code:
        await message.answer("❌ Такая страна пока не описана в data/countries.yaml.")
        return
    await repo.set_user_country(user.id, code)
    cfg = country_config(code) or {}
    await message.answer(f"✅ Текущая страна: <b>{html.escape(cfg.get('name', code))}</b> ({code}).", parse_mode="HTML")


@router.message(Command("targets"))
async def targets(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    if not profile:
        return
    searches = await repo.list_search_profiles(profile.id)
    if not searches:
        return
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) == 1:
        lines = [f"🎯 <b>{html.escape(item.name)}</b>: " + (", ".join((item.settings or {}).get("target_countries") or []) or "не заданы") for item in searches]
        await message.answer("\n".join(lines), parse_mode="HTML")
        return

    scope = "all"
    raw = parts[1].strip()
    if raw.casefold() in {"all", "career", "relocation"}:
        scope = raw.casefold()
        if len(parts) < 3:
            await message.answer("Использование: /targets [all|career|relocation] <GE[,CA]|clear>")
            return
        raw = parts[2].strip()
    values = [] if raw.casefold() == "clear" else [x.strip() for x in raw.split(",") if x.strip()]
    codes = []
    for value in values:
        code = normalize_country(value)
        if not code:
            await message.answer(f"❌ Неизвестная страна: {html.escape(value)}")
            return
        if code not in codes:
            codes.append(code)

    if scope == "all":
        selected_searches = searches
    else:
        expected_kind = "career" if scope == "career" else "relocation"
        selected_searches = [item for item in searches if item.kind == expected_kind]
        if not selected_searches and scope == "career" and len(searches) == 1:
            selected_searches = searches
        if not selected_searches:
            if scope == "relocation":
                await message.answer("❌ Профиль Relocation-first не активен. Включи его командой /parallelsearch on.")
            else:
                await message.answer("❌ Профиль Career-first не найден среди активных поисков.")
            return

    for search in selected_searches:
        current = dict(search.settings or {})
        current["target_countries"] = codes
        await repo.update_search_settings(search.id, current)
        search.settings = current
    target_names = ", ".join(item.name for item in selected_searches)
    await message.answer(
        f"✅ Локальные рынки для {target_names}: "
        + (", ".join(codes) if codes else "очищены")
    )


@router.message(Command("sources"))
async def sources(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    if not profile:
        return
    searches = await repo.list_search_profiles(profile.id)
    lines = ["🧭 <b>Источники Personal Job Agent</b>"]
    for search in searches:
        settings_map = search.settings or {}
        targets = settings_map.get("target_countries") or []
        plan = build_source_plan(user.current_country or "RU", targets, include_international=True)
        lines.append(f"\n<b>{html.escape(search.name)}</b> · рынки: {html.escape(', '.join(targets) or 'не заданы')}")
        for item in plan:
            if item.manual:
                lines.append(manual_source_line(item))
                continue
            if not item.implemented:
                flag = "🧩"
            elif not item.available:
                flag = "⚠️"
            else:
                flag = "✅" if source_enabled(settings_map, item.source_id) else "⏸"
            availability = f" · {item.availability_note}" if item.availability_note else ""
            name = html.escape(item.name)
            lines.append(f"{flag} {name} — {html.escape(item.scope)} — {html.escape(item.transport)}{html.escape(availability)}")
    lines.append("\n✅ = автоматический источник разрешён настройками; ⏸ = отключён; ⚠️ = временно приостановлен; 🧩 = adapter не подключён; 🔗 = ручной поиск по ссылке, бот источник не сканирует. Это не live health check и не подтверждение права на работу.")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("facts"))
async def facts(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    rows = await repo.list_facts(profile.id) if profile else []
    if not rows:
        await message.answer("Фактов пока нет.")
        return
    text = "🧠 <b>Candidate Facts</b>\n\n" + "\n".join(
        f"{f.id}. {html.escape(f.value[:300])} {experience_type_label(getattr(f, 'experience_type', None))}"
        for f in rows[:30]
    )
    await message.answer(text[:4096], parse_mode="HTML")


@router.message(Command("import"))
async def import_resume_command(message: Message) -> None:
    if not await _require_user(message):
        return
    await message.answer("Пришли резюме файлом PDF, DOCX или TXT (до 8 МБ). Перед сохранением покажу извлечённый текст и предложенные факты.")


@router.message(F.document)
async def import_resume_document(message: Message, bot: Bot) -> None:
    user = await _require_user(message)
    if not user:
        return
    document = message.document
    if not document:
        return
    if document.file_size and document.file_size > MAX_DOCUMENT_BYTES:
        await message.answer("❌ Размер файла превышает лимит 8 МБ.")
        return
    try:
        downloaded = await bot.download(document.file_id)
        if downloaded is None:
            raise ResumeImportError("Telegram не передал файл для чтения.")
        payload = downloaded.getvalue() if isinstance(downloaded, io.BytesIO) else downloaded.read()
        content = extract_resume_text(document.file_name or "", payload)
    except ResumeImportError as exc:
        await message.answer(f"❌ {html.escape(str(exc))}", parse_mode="HTML")
        return
    except Exception:
        await message.answer("❌ Не удалось получить файл из Telegram. Попробуй отправить его ещё раз.")
        return

    profile = await repo.active_profile(user.id)
    if not profile:
        await message.answer("❌ Активный профиль не найден.")
        return
    fingerprint = resume_fingerprint(content)
    resumes = await repo.list_resumes(profile.id)
    if any(resume.external_id == fingerprint for resume in resumes):
        await message.answer("ℹ️ Такое резюме уже импортировано в этот профиль.")
        return

    proposals = propose_facts(content)
    existing = await repo.list_facts(profile.id)
    review = review_proposals(proposals, existing)
    token = uuid.uuid4().hex[:12]
    _PENDING_RESUME_IMPORTS[token] = {
        "user_id": user.id, "profile_id": profile.id,
        "content": content, "fingerprint": fingerprint, "language": guess_language(content),
        "role": profile.target_role or "", "proposals": review.new,
        "overlaps": review.overlaps, "created_at": time.time(),
    }
    now = time.time()
    for old_token, pending in list(_PENDING_RESUME_IMPORTS.items()):
        if now - pending["created_at"] > 15 * 60:
            _PENDING_RESUME_IMPORTS.pop(old_token, None)

    lines = ["📄 <b>Проверка импорта</b>", "", f"Извлечено символов: {len(content)}", f"Язык: {guess_language(content)}"]
    if review.new:
        lines.extend(["", "Предлагаемые факты:"])
        for proposal in review.new[:12]:
            lines.append(f"• [{proposal.category}] {html.escape(proposal.value[:180])} — уверенность {proposal.confidence:.0%}")
        if len(review.new) > 12:
            lines.append(f"… и ещё {len(review.new) - 12}")
    else:
        lines.extend(["", "Новых фактов для добавления не найдено."])
    if review.duplicates:
        lines.append(f"Совпадающих фактов пропущено: {len(review.duplicates)}.")
    if review.overlaps:
        lines.append(f"Похожие на существующие факты помечены как пересечения ({len(review.overlaps)}); они не будут перезаписаны.")
    lines.extend(["", "Содержимое будет сохранено только после подтверждения."])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сохранить резюме", callback_data=f"rimp:resume:{token}")],
        [InlineKeyboardButton(text=f"Сохранить резюме и факты ({len(review.new)})", callback_data=f"rimp:facts:{token}")],
        [InlineKeyboardButton(text="Отмена", callback_data=f"rimp:cancel:{token}")],
    ])
    await message.answer("\n".join(lines)[:4096], parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rimp:"))
async def confirm_resume_import(callback: CallbackQuery) -> None:
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3:
        await callback.answer("Некорректная команда", show_alert=True)
        return
    action, token = parts[1], parts[2]
    pending = _PENDING_RESUME_IMPORTS.get(token)
    if not pending or time.time() - pending["created_at"] > 15 * 60:
        _PENDING_RESUME_IMPORTS.pop(token, None)
        await callback.answer("Предпросмотр истёк. Отправь документ заново.", show_alert=True)
        return
    user = await repo.get_user_by_chat(callback.message.chat.id) if callback.message else None
    if not user or user.id != pending["user_id"]:
        await callback.answer("Этот импорт предназначен другому профилю.", show_alert=True)
        return
    if action == "cancel":
        _PENDING_RESUME_IMPORTS.pop(token, None)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Импорт отменён")
        return
    if action not in {"resume", "facts"}:
        await callback.answer("Неизвестное действие", show_alert=True)
        return
    resumes = await repo.list_resumes(pending["profile_id"])
    if any(resume.external_id == pending["fingerprint"] for resume in resumes):
        _PENDING_RESUME_IMPORTS.pop(token, None)
        await callback.message.edit_text("ℹ️ Такое резюме уже импортировано.")
        await callback.answer()
        return
    item = await repo.add_resume(
        pending["profile_id"], f"Imported resume {datetime.now():%Y-%m-%d}",
        pending["language"], pending["role"], content=pending["content"],
        source="imported", external_id=pending["fingerprint"],
    )
    added = 0
    if action == "facts":
        for proposal in pending["proposals"]:
            await repo.add_fact(
                pending["profile_id"], proposal.value, category=proposal.category,
                key=proposal.category, experience_type="unknown",
                confidence=proposal.confidence, provenance="resume_import",
                evidence=f"resume_import section={proposal.section}; confidence={proposal.confidence:.2f}",
            )
            added += 1
    _PENDING_RESUME_IMPORTS.pop(token, None)
    await callback.message.edit_text(f"✅ Резюме #{item.id} сохранено." + (f" Добавлено фактов: {added}." if action == "facts" else " Факты не изменялись."))
    await callback.answer("Импорт завершён")


@router.message(Command("fact"))
async def fact(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    text = (message.text or "").strip()
    lower = text.casefold()
    profile = await repo.active_profile(user.id)
    if not profile:
        await message.answer("❌ Активный профиль не найден.")
        return

    if lower.startswith("/fact type "):
        parts = text.split()
        if len(parts) != 4 or not parts[2].isdigit():
            await message.answer(
                "Использование: /fact type <id> commercial|lab|learning|unknown"
            )
            return
        normalized_type = normalize_experience_type(parts[3])
        if not normalized_type:
            allowed = "|".join(ALLOWED_EXPERIENCE_TYPES)
            await message.answer(f"❌ Неизвестный тип. Допустимо: {allowed}")
            return
        ok = await repo.set_fact_experience_type(profile.id, int(parts[2]), normalized_type)
        await message.answer(
            f"✅ Факт #{parts[2]} теперь {experience_type_label(normalized_type)}."
            if ok
            else "❌ Такой факт не найден."
        )
        return

    if lower.startswith("/fact commercial ") or lower.startswith("/fact noncommercial "):
        parts = text.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.answer("Использование: /fact commercial <id> или /fact noncommercial <id>")
            return
        is_commercial = parts[1].casefold() == "commercial"
        ok = await repo.set_fact_commercial(profile.id, int(parts[2]), is_commercial)
        if not ok:
            await message.answer("❌ Такой факт не найден.")
            return
        if is_commercial:
            await message.answer(f"✅ Факт #{parts[2]} теперь [commercial].")
        else:
            await message.answer(
                f"✅ Факт #{parts[2]} теперь [unknown]. Уточни при необходимости: "
                f"/fact type {parts[2]} lab или /fact type {parts[2]} learning"
            )
        return

    prefix = "/fact add "
    if not lower.startswith(prefix):
        await message.answer(
            "Использование:\n"
            "/fact add <факт>\n"
            "/fact type <id> commercial|lab|learning|unknown\n"
            "/fact commercial <id> — совместимость со старыми версиями\n"
            "/fact noncommercial <id> — сбрасывает тип в unknown"
        )
        return
    value = text[len(prefix):].strip()
    if not value:
        return
    item = await repo.add_fact(profile.id, value, experience_type="unknown")
    await message.answer(
        f"✅ Добавлен факт #{item.id} [unknown]. "
        f"Укажи тип: /fact type {item.id} commercial|lab|learning"
    )


@router.message(Command("resumeadd"))
async def resumeadd(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    raw = (message.text or "").split(maxsplit=1)
    if len(raw) < 2:
        await message.answer("Использование: /resumeadd DevOps EN|en|DevOps Engineer")
        return
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) != 3 or not all(parts):
        await message.answer("Нужно три поля: имя|язык|роль. Например: /resumeadd DevOps EN|en|DevOps Engineer")
        return
    profile = await repo.active_profile(user.id)
    item = await repo.add_resume(profile.id, parts[0], parts[1], parts[2])
    await message.answer(f"✅ Резюме #{item.id} добавлено. Оно использует общую Candidate Facts базу.")


@router.message(Command("resumebindhh"))
async def resumebindhh(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    if len(parts) != 3 or not parts[1].isdigit():
        await message.answer("Использование: /resumebindhh <resume_id> <HH_RESUME_ID>")
        return
    profile = await repo.active_profile(user.id)
    ok = await repo.bind_resume_external(profile.id, int(parts[1]), "hh", parts[2])
    await message.answer("✅ HH resume привязан." if ok else "❌ Резюме не найдено в твоём профиле.")


@router.message(Command("resumes"))
async def resumes(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    rows = await repo.list_resumes(profile.id) if profile else []
    text = "📄 <b>Резюме</b>\n\n" + "\n".join(f"{r.id}. {html.escape(r.name)} — {html.escape(r.role)} — {r.language} — {r.source}" for r in rows)
    await message.answer(text, parse_mode="HTML")


@router.message(Command("scan"))
async def scan(message: Message, bot: Bot) -> None:
    user = await _require_user(message)
    if not user:
        return

    existing = _ACTIVE_SCAN_TASKS.get(user.id)
    if existing and not existing.done():
        await message.answer("⏳ Сканирование уже выполняется. /scanstatus покажет прогресс.")
        return
    task = asyncio.current_task()
    if task:
        _ACTIVE_SCAN_TASKS[user.id] = task

    progress = await message.answer(
        "⏳ Ищу вакансии по активным источникам…"
    )

    stage = "Ищу вакансии по активным источникам…"
    started = time.monotonic()

    async def update_progress(text: str) -> None:
        nonlocal stage
        stage = text[1:].strip() if text.startswith("⏳") else text
        await _save_scan_dashboard(user.id, status="running", stage=stage)

    async def heartbeat() -> None:
        frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        index = 0
        while True:
            elapsed = int(time.monotonic() - started)
            try:
                await progress.edit_text(f"{frames[index % len(frames)]} {stage}\n⏱ Прошло: {elapsed} сек.")
            except Exception:
                pass
            index += 1
            await asyncio.sleep(2)

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        await _save_scan_dashboard(user.id, reset=True, status="running", stage=stage, started_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
        summary = await scan_for_user(bot, user.id, progress_callback=update_progress, force_refresh=True)
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

        await _save_scan_dashboard(user.id, status="completed", stage="Готово", finished_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), summary=summary)
        source_bits = []

        for source_id, info in (summary.get("sources") or {}).items():
            if "error" in info:
                source_bits.append(
                    f"• {html.escape(source_id)}: ошибка"
                )
            elif "skipped" in info:
                source_bits.append(f"• {html.escape(source_id)}: пропущен")
            else:
                freshness = "кэш" if info.get("cache") else "live"
                partial_label = " · частично" if info.get("partial") else ""
                source_bits.append(
                    f"• {html.escape(source_id)}: "
                    f"{int(info.get('found', 0))} ({freshness}, {int(info.get('duration_ms', 0)) / 1000:.1f} с)"
                    + partial_label
                )

        details = (
            "\n".join(source_bits)
            or "• активных источников нет"
        )
        profile_bits = []
        for info in (summary.get("searches") or {}).values():
            profile_bits.append(
                f"• {html.escape(str(info.get('name') or 'Search'))}: "
                f"{int(info.get('processed', 0))} обработано, "
                f"{int(info.get('qualified', 0))} Good, "
                f"{int(info.get('stretch', 0))} Stretch"
            )
        profile_details = "\n\n<b>Профили поиска</b>\n" + "\n".join(profile_bits) if profile_bits else ""

        await progress.edit_text(
            "✅ <b>Проход поиска завершён</b>\n\n"
            + details
            + profile_details
            + f"\n\nОбработано: {int(summary.get('processed', 0))}"
            + f"\n🟢 Good: {int(summary.get('qualified', 0))}"
            + f"\n🟡 Stretch: {int(summary.get('stretch', 0))}"
            + f"\n⚪ Отфильтровано: {int(summary.get('filtered', 0))}"
            + f"\n📨 Новых уведомлений: {int(summary.get('notified', 0))}"
            + f"\nДубликатов подавлено: {int(summary.get('duplicate', 0))}",
            parse_mode="HTML",
        )
    except asyncio.CancelledError:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        await _save_scan_dashboard(user.id, status="cancelled", stage="Отменено", finished_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
        try:
            await progress.edit_text("⏹ Сканирование остановлено. Результаты уже обработанных источников сохранены.")
        except Exception:
            pass
    except Exception as exc:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        await _save_scan_dashboard(user.id, status="failed", stage=str(exc)[:500], finished_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
        await progress.edit_text(
            f"⚠ {html.escape(str(exc))}",
            parse_mode="HTML",
        )
    finally:
        if _ACTIVE_SCAN_TASKS.get(user.id) is task:
            _ACTIVE_SCAN_TASKS.pop(user.id, None)


@router.message(Command("scanstatus"))
async def scan_status(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    try:
        state = json.loads(await repo.get_state(user.id, "scan_dashboard", "{}"))
    except (TypeError, ValueError):
        state = {}
    if not state:
        await message.answer("Истории сканирования пока нет. Запусти /scan.")
        return
    summary = state.get("summary") or {}
    sources = []
    for name, info in (summary.get("sources") or {}).items():
        if info.get("error"):
            sources.append(f"• {html.escape(name)}: ошибка ({int(info.get('duration_ms', 0)) / 1000:.1f} с)")
        elif "skipped" in info:
            sources.append(f"• {html.escape(name)}: пропущен")
        else:
            partial_label = " · частично" if info.get("partial") else ""
            sources.append(f"• {html.escape(name)}: {int(info.get('found', 0))} вакансий ({int(info.get('duration_ms', 0)) / 1000:.1f} с)" + partial_label)
    await message.answer(
        f"📊 Сканирование: <b>{html.escape(str(state.get('status', 'неизвестно')))}</b>\n"
        f"Начато: {html.escape(str(state.get('started_at', '—')))}\n"
        f"Завершено: {html.escape(str(state.get('finished_at', '—')))}\n"
        f"Этап: {html.escape(str(state.get('stage', '—')))}\n"
        + ("\n".join(sources) if sources else "Источники ещё не завершили поиск."),
        parse_mode="HTML",
    )

def _pick_next_review(rows, current_match_id: int):
    for index, (match, job) in enumerate(rows):
        if match.id == current_match_id:
            next_index = index + 1
            return (next_index, rows[next_index]) if next_index < len(rows) else None
    return (0, rows[0]) if rows else None


def _pick_previous_review(rows, current_match_id: int):
    for index, (match, job) in enumerate(rows):
        if match.id == current_match_id:
            previous_index = index - 1
            return (previous_index, rows[previous_index]) if previous_index >= 0 else None
    return (len(rows) - 1, rows[-1]) if rows else None


def _render_review_card(match, job, position: int, total: int) -> str:
    return render_queue_card(
        match, job, header="📥 Разбор вакансий", lane="🟢 Good", position=position, total=total
    )


def _render_stretch_card(match, job, position: int, total: int) -> str:
    return render_queue_card(
        match, job, header="🟡 Stretch-вакансии", lane="🟡 Stretch", position=position, total=total
    )


def _render_saved_card(match, job, position: int, total: int) -> str:
    return render_queue_card(
        match, job, header="⭐ Сохранённые вакансии", lane="⭐ Saved", position=position, total=total
    )


async def _advance_stretch(callback, user_id: int, current_match_id: int) -> None:
    rows = await repo.stretch_matches(user_id, None)
    picked = _pick_next_review(rows, current_match_id)
    if not picked:
        await callback.message.edit_text("✅ Stretch-очередь разобрана — вакансий больше нет.")
        return
    index, (match, job) = picked
    await callback.message.edit_text(
        _render_stretch_card(match, job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=stretch_keyboard(match.id, job.id),
    )

async def _advance_review(callback, user_id: int, current_match_id: int) -> None:
    rows = await repo.review_matches(user_id, None)
    picked = _pick_next_review(rows, current_match_id)
    if not picked:
        await callback.message.edit_text("✅ Очередь разобрана — новых вакансий для review нет.")
        return
    index, (match, job) = picked
    await callback.message.edit_text(
        _render_review_card(match, job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=review_keyboard(match.id, job.id),
    )


@router.message(Command("review"))
async def review(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    rows = await repo.review_matches(user.id, None)
    if not rows:
        await message.answer("✅ Очередь разобрана — новых вакансий для review нет.")
        return
    match, job = rows[0]
    text = _render_review_card(match, job, 1, len(rows))
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=review_keyboard(match.id, job.id),
    )



@router.message(Command("stretch"))
async def stretch(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    rows = await repo.stretch_matches(user.id, None)
    if not rows:
        await message.answer("🟡 Stretch-вакансий пока нет.")
        return
    match, job = rows[0]
    await message.answer(
        _render_stretch_card(match, job, 1, len(rows)),
        parse_mode="HTML",
        reply_markup=stretch_keyboard(match.id, job.id),
    )
@router.message(Command("saved"))
async def saved(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    rows = await repo.saved_matches(user.id, None)
    if not rows:
        await message.answer("⭐ Сохранённых вакансий пока нет.")
        return
    match, job = rows[0]
    await message.answer(
        _render_saved_card(match, job, 1, len(rows)),
        parse_mode="HTML",
        reply_markup=saved_keyboard(match.id, job.id),
    )


@router.message(Command("jobs"))
async def jobs(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    options = [value.casefold() for value in (message.text or "").split()[1:]]
    scopes = [value for value in options if value in {"career", "relocation"}]
    if (
        any(value not in {"career", "relocation", "below"} for value in options)
        or len(options) != len(set(options))
        or len(scopes) > 1
    ):
        await message.answer("Использование: /jobs [career|relocation] [below]; карточка: /job <id>")
        return
    scope = scopes[0] if scopes else None
    show_below = "below" in options
    if scope:
        search = await _search_for_scope(user.id, scope)
        if not search:
            await message.answer(_missing_search_scope(scope))
            return
    else:
        _, search = await _first_search(user.id)
    threshold = int(((search.settings or {}) if search else {}).get("notify_min_score", 65))
    search_filter = {"search_profile_id": search.id} if scope else {}
    query_limit = 80 if scope == "relocation" else 10
    if show_below:
        rows = await repo.latest_matches(
            user.id,
            query_limit,
            include_filtered=True,
            min_score=1,
            max_score=threshold - 1,
            **search_filter,
        )
    else:
        rows = await repo.latest_matches(user.id, query_limit, min_score=threshold, **search_filter)
    if scope == "relocation" and search:
        rows = [
            (match, job)
            for match, job in rows
            if relocation_first_allows(job, search.settings, current_country=user.current_country)
        ][:10]
    if not rows:
        if show_below:
            await message.answer(
                f"Ниже порога {threshold} пока нет вакансий с ненулевым рейтингом для ручного просмотра."
            )
        else:
            if scope:
                label = "Career-first" if scope == "career" else "Relocation-first"
                await message.answer(
                    f"В {label} пока нет совпадений от {threshold}/100. Запусти /scan.\n"
                    f"Результаты ниже порога: /jobs {scope} below"
                )
            else:
                await message.answer("Пока совпадений нет. Запусти /scan.")
        return
    source_links = {}
    for _, job in rows:
        refs = []
        for source_id, source_name in (("himalayas", "Himalayas"), ("remotive", "Remotive")):
            ref = await repo.source_ref(job.id, source_id)
            if ref and ref.url:
                refs.append((ref.url, source_name))
        if refs:
            source_links[job.id] = refs
    await message.answer(
        render_jobs_list(
            rows,
            source_links=source_links,
            below_threshold=threshold if show_below else None,
            search_scope=scope,
        ),
        parse_mode="HTML",
        reply_markup=jobs_keyboard(rows, **search_filter),
    )


@router.message(Command("job"))
async def job_details(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return

    parts = (message.text or "").split()
    if (
        len(parts) not in {2, 3}
        or not parts[1].isdigit()
        or (len(parts) == 3 and parts[2].casefold() not in {"career", "relocation"})
    ):
        await message.answer(
            "Использование: /job <id> [career|relocation], например /job 25"
        )
        return
    search_filter = {}
    if len(parts) == 3:
        scope = parts[2].casefold()
        search = await _search_for_scope(user.id, scope)
        if not search:
            await message.answer(_missing_search_scope(scope))
            return
        search_filter = {"search_profile_id": search.id}

    progress = await message.answer(
        "⏳ Загружаю полное описание вакансии…"
    )

    try:
        payload = await get_vacancy_details(
            user.id,
            int(parts[1].strip()),
            **search_filter,
        )
        selected_id = getattr(payload.get("match"), "search_profile_id", None)
        if selected_id is not None:
            search_filter = {"search_profile_id": selected_id}
        await progress.edit_text(
            render_job_details(payload),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=vacancy_details_keyboard(
                payload["job"].id, **search_filter,
            ),
        )
    except Exception as exc:
        await progress.edit_text(
            f"⚠ {html.escape(str(exc))}",
            parse_mode="HTML",
        )

@router.message(Command("compare"))
async def compare_job(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return

    parts = (message.text or "").split()
    if (
        len(parts) not in {2, 3}
        or not parts[1].isdigit()
        or (len(parts) == 3 and parts[2].casefold() not in {"career", "relocation"})
    ):
        await message.answer(
            "Использование: /compare <id> [career|relocation], например /compare 24"
        )
        return
    search_filter = {}
    if len(parts) == 3:
        scope = parts[2].casefold()
        search = await _search_for_scope(user.id, scope)
        if not search:
            await message.answer(_missing_search_scope(scope))
            return
        search_filter = {"search_profile_id": search.id}

    progress = await message.answer(
        "⏳ Сравниваю требования вакансии с Candidate Facts…"
    )

    try:
        payload = await get_vacancy_comparison(
            user.id,
            int(parts[1].strip()),
            **search_filter,
        )
        await progress.edit_text(
            render_fact_comparison(payload),
            parse_mode="HTML",
        )
    except Exception as exc:
        await progress.edit_text(
            f"⚠ {html.escape(str(exc))}",
            parse_mode="HTML",
        )

@router.message(Command("chats"))
async def chats(message: Message, bot: Bot) -> None:
    user = await _require_user(message)
    if not user:
        return
    if not hh_client.private_api_available:
        await message.answer(
            "ℹ️ HH-поиск работает без applicant OAuth. Приватная переписка/автоответы HH сейчас отключены: "
            "для новых приложений соискательский API не считаем доступным. Чаты HH пока открывай вручную; "
            "Telegram-рекрутеров и другие доступные каналы будем подключать отдельно."
        )
        return
    if str(message.chat.id) != settings.telegram_admin_chat_id.strip():
        await message.answer("ℹ️ Приватный HH-коннектор привязан только к owner-профилю.")
        return
    await scan_hh_chats(bot)
    await message.answer("✅ HH-чаты проверены.")


async def _navigate_previous_queue(
    callback, queue_loader, renderer, keyboard_factory, first_message: str
) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    rows = await queue_loader(user.id, None)
    picked = _pick_previous_review(rows, match.id)
    if not picked:
        await callback.answer(first_message, show_alert=True)
        return
    index, (previous_match, job) = picked
    await callback.message.edit_text(
        renderer(previous_match, job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=keyboard_factory(previous_match.id, job.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("review_prev:"))
async def review_prev_callback(callback: CallbackQuery) -> None:
    await _navigate_previous_queue(
        callback, repo.review_matches, _render_review_card, review_keyboard, "Это первая вакансия"
    )


@router.callback_query(F.data.startswith("stretch_prev:"))
async def stretch_prev_callback(callback: CallbackQuery) -> None:
    await _navigate_previous_queue(
        callback, repo.stretch_matches, _render_stretch_card, stretch_keyboard, "Это первая Stretch-вакансия"
    )


@router.callback_query(F.data.startswith("saved_prev:"))
async def saved_prev_callback(callback: CallbackQuery) -> None:
    await _navigate_previous_queue(
        callback, repo.saved_matches, _render_saved_card, saved_keyboard, "Это первая сохранённая вакансия"
    )


@router.callback_query(F.data.startswith("stretch_next:"))
async def stretch_next_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    rows = await repo.stretch_matches(user.id, None)
    picked = _pick_next_review(rows, match.id)
    if not picked:
        await callback.answer("Больше Stretch-вакансий нет", show_alert=True)
        return
    index, (next_match, next_job) = picked
    await callback.message.edit_text(
        _render_stretch_card(next_match, next_job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=stretch_keyboard(next_match.id, next_job.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("stretch_skip:"))
async def stretch_skip_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    await repo.set_match_status(match.id, "skipped")
    await callback.answer("❌ Пропущено")
    await _advance_stretch(callback, user.id, match.id)


@router.callback_query(F.data.startswith("stretch_save:"))
async def stretch_save_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    await repo.set_match_status(match.id, "saved")
    await callback.answer("⭐ Сохранено")
    await _advance_stretch(callback, user.id, match.id)


@router.callback_query(F.data.startswith("saved_next:"))
async def saved_next_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    rows = await repo.saved_matches(user.id, None)
    picked = _pick_next_review(rows, match.id)
    if not picked:
        await callback.answer("Больше сохранённых вакансий нет", show_alert=True)
        return
    index, (next_match, job) = picked
    await callback.message.edit_text(
        _render_saved_card(next_match, job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=saved_keyboard(next_match.id, job.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("review_next:"))
async def review_next_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    rows = await repo.review_matches(user.id, None)
    picked = _pick_next_review(rows, match.id)
    if not picked:
        await callback.answer("Больше вакансий нет", show_alert=True)
        return
    index, (next_match, next_job) = picked
    await callback.message.edit_text(
        _render_review_card(next_match, next_job, index + 1, len(rows)),
        parse_mode="HTML",
        reply_markup=review_keyboard(next_match.id, next_job.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("review_skip:"))
async def review_skip_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    await repo.set_match_status(match.id, "skipped")
    await callback.answer("❌ Пропущено")
    await _advance_review(callback, user.id, match.id)


@router.callback_query(F.data.startswith("review_save:"))
async def review_save_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match = await repo.get_match(int(raw_id))
    if not match or match.user_id != user.id:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return
    await repo.set_match_status(match.id, "saved")
    await callback.answer("⭐ Сохранено")
    await _advance_review(callback, user.id, match.id)


@router.callback_query(F.data.startswith("details:"))
async def details_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    identifiers = callback.data.split(":")[1:]
    if len(identifiers) not in {1, 2} or not all(value.isdigit() for value in identifiers):
        await callback.answer("Некорректный ID вакансии", show_alert=True)
        return
    await callback.answer("Загружаю подробности…")
    try:
        search_filter = {"search_profile_id": int(identifiers[1])} if len(identifiers) == 2 else {}
        payload = await get_vacancy_details(user.id, int(identifiers[0]), **search_filter)
        selected_id = getattr(payload.get("match"), "search_profile_id", None)
        if selected_id is not None:
            search_filter = {"search_profile_id": selected_id}
        await callback.message.answer(
            render_job_details(payload),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=vacancy_details_keyboard(payload["job"].id, **search_filter),
        )
    except Exception as exc:
        await callback.message.answer(f"⚠️ {html.escape(str(exc))}", parse_mode="HTML")


@router.callback_query(F.data.startswith("compare:"))
async def compare_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return

    identifiers = callback.data.split(":")[1:]
    if len(identifiers) not in {1, 2} or not all(value.isdigit() for value in identifiers):
        await callback.answer(
            "Некорректный ID вакансии",
            show_alert=True,
        )
        return

    await callback.answer("Сравниваю с профилем…")

    try:
        search_filter = {"search_profile_id": int(identifiers[1])} if len(identifiers) == 2 else {}
        payload = await get_vacancy_comparison(
            user.id,
            int(identifiers[0]),
            **search_filter,
        )
        await callback.message.answer(
            render_fact_comparison(payload),
            parse_mode="HTML",
        )
    except Exception as exc:
        await callback.message.answer(
            f"⚠ {html.escape(str(exc))}",
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("skip:"))
async def skip_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    match_id = int(callback.data.split(":", 1)[1])
    match = await repo.get_match(match_id)
    if not match or match.user_id != user.id:
        await callback.answer("Не твой match", show_alert=True)
        return
    await repo.set_match_status(match_id, "skipped")
    await callback.answer("Пропущено")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("prepare:"))
async def prepare_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    match_id = int(callback.data.split(":", 1)[1])
    await callback.answer("Готовлю…")
    try:
        result = await prepare_match(match_id, user.id)
        job = result["job"]
        resume = result.get("resume")
        cover = result.get("cover_letter") or ""
        url = result.get("url") or ""
        text = (
            f"📝 <b>Отклик подготовлен</b>\n\n"
            f"<b>{html.escape(job.title)}</b> — {html.escape(job.company)}\n"
            f"Резюме: <b>{html.escape(resume.name if resume else 'не выбрано')}</b>\n\n"
            f"<b>Сопроводительное:</b>\n{html.escape(cover)}"
        )
        if url:
            text += f"\n\n<a href=\"{html.escape(url, quote=True)}\">Открыть вакансию и отправить вручную</a>"
        await callback.message.answer(text[:4096], parse_mode="HTML", disable_web_page_preview=True)
    except Exception as exc:
        await callback.message.answer(f"⚠️ {html.escape(str(exc))}", parse_mode="HTML")


@router.callback_query(F.data.startswith("apply:"))
async def apply_callback(callback: CallbackQuery, bot: Bot) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    match_id = int(callback.data.split(":", 1)[1])
    await callback.answer("Отправляю…")
    try:
        result = await apply_match(bot, match_id, user.id)
        await callback.message.answer("✅ Отклик обработан: " + html.escape(str(result.get("status", "sent"))), parse_mode="HTML")
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as exc:
        await callback.message.answer(f"⚠️ {html.escape(str(exc))}", parse_mode="HTML")


@router.callback_query(F.data.startswith("sendreply:"))
async def sendreply(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user or str(callback.message.chat.id) != settings.telegram_admin_chat_id.strip():
        return
    _, chat_id, msg_id = callback.data.split(":", 2)
    draft = await repo.get_state(user.id, f"draft:{chat_id}:{msg_id}", "")
    if not draft:
        await callback.answer("Черновик не найден", show_alert=True)
        return
    await hh_client.send_chat_message(chat_id, draft)
    await callback.answer("Отправлено")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("manual:"))
async def manual(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    _, chat_id, msg_id = callback.data.split(":", 2)
    await repo.set_state(user.id, "manual_hh_reply", f"{chat_id}:{msg_id}")
    await callback.answer()
    await callback.message.answer("📝 Следующее обычное сообщение будет отправлено в этот HH-чат. /cancel — отменить.")


@router.message(Command("cancel"))
async def cancel(message: Message) -> None:
    user = await _require_user(message)
    if user:
        active = _ACTIVE_SCAN_TASKS.get(user.id)
        if active and active is not asyncio.current_task() and not active.done():
            active.cancel()
            await repo.set_state(user.id, "manual_hh_reply", "")
            await message.answer("⏹ Останавливаю текущий скан. /scanstatus покажет его итог.")
            return
        await repo.set_state(user.id, "manual_hh_reply", "")
        await message.answer("Отменено.")


@router.channel_post()
async def channel_post(message: Message, bot: Bot) -> None:
    text = message.text or message.caption or ""
    if not text.strip():
        return
    await consume_channel_post(bot, chat_id=message.chat.id, username=message.chat.username,
                               message_id=message.message_id, text=text)


@router.message(Command("channels"))
async def channels(message: Message, bot: Bot) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    try:
        if len(parts) == 2 and parts[1] == "retry":
            await retry_pending(bot, user_id=user.id)
            state = await watch_state(user.id)
        elif len(parts) == 1 or (len(parts) == 2 and parts[1] in {"list", "stats"}):
            state = await watch_state(user.id)
        elif len(parts) in {3, 4}:
            state = await change_subscription(user.id, parts[1], parts[2], parts[3] if len(parts) == 4 else "both")
        else:
            raise ValueError("Используй /channels add @канал [career|relocation|both] или /channels on|off|remove @канал")
        # Render long watchlists in bounded chunks; no arbitrary Telegram HTML.
        text = render_subscriptions(state)
        for start in range(0, len(text), 3900):
            await message.answer(text[start:start + 3900], parse_mode=None)
    except (ValueError, RuntimeError) as exc:
        await message.answer(str(exc), parse_mode=None)


@router.message(F.text)
@router.message(F.caption, F.forward_origin)
async def generic_text(message: Message, bot: Bot) -> None:
    user = await _user(message)
    if not user:
        return
    pending = await repo.get_state(user.id, "manual_hh_reply", "")
    if pending:
        chat_id, _ = pending.split(":", 1)
        if message.text and str(message.chat.id) == settings.telegram_admin_chat_id.strip():
            await hh_client.send_chat_message(chat_id, message.text)
            await repo.set_state(user.id, "manual_hh_reply", "")
            await message.answer("✅ Сообщение отправлено в HH.")
        return

    # Forwarded Telegram vacancy: aiogram exposes forward_origin on modern Bot API.
    if getattr(message, "forward_origin", None) is not None:
        job = parse_forwarded_job(message.text or message.caption or "", chat_id=message.chat.id,
                                  message_id=message.message_id, origin=message.forward_origin)
        if not await consume_forwarded_job(bot, user.id, job):
            await message.answer("♻️ Этот пост канала уже обработан для твоего профиля.")
            return
        await message.answer("✅ Пересланный пост добавлен в общий pipeline и оценён для твоего профиля.")
