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
from aiogram.types import CallbackQuery, Message
from aiogram.types import BufferedInputFile

from app.search.source_summary import render_filter_reason_counts, render_source_dashboard, scan_outcome, select_scan_dashboard
from app.sources.diagnostics import classify_source_error, legacy_diagnostic

from app.candidates.bootstrap import bootstrap_user
from app.candidates.import_review import plan_fact_import
from app.candidates.importer import (
    MAX_DOCUMENT_BYTES, ResumeImportError, extract_resume_text,
    guess_language, propose_facts, resume_fingerprint, review_proposals,
)
from app.config import settings
from app.database import repository as repo
from app.database import notification_delivery as delivery_repo
from app.domain.application_package import snapshot_vacancy
from app.domain.text_limits import utf16_length
from app.domain.employer_policy import LEGACY_INDUSTRY_EXCLUSIONS, update_policy as update_employer_policy
from app.candidates.fact_types import ALLOWED_EXPERIENCE_TYPES, experience_type_label, normalize_experience_type
from app.database.db import current_schema_version, expected_schema_version
from app.geo.countries import all_supported_countries, country_config, normalize_country
from app.knowledge.profile import load_profile
from app.matching.language_fit import normalize_cefr
from app.agents.interview import build_interview_plan
from app.services import ScanAlreadyRunning, apply_match, get_resume_diff, get_vacancy_comparison, get_vacancy_details, prepare_match, coordinated_scan_for_user, scan_hh_chats, hh_client
from app.sources.adapters.telegram_ingest import parse_forwarded_job
from app.sources.telegram_watch import change_subscription, consume_channel_post, consume_forwarded_job, render_subscriptions, retry_pending, watch_state
from app.telegram.vacancy_view import render_application_export, render_application_history, render_application_package, render_applications, render_fact_comparison, render_interview_plan, render_job_section, render_job_summary, render_jobs_list, render_queue_card, render_resume_diff
from app.telegram.resume_import_view import render_import_preview, render_import_conflict
from app.telegram.source_display import manual_source_line
from app.telegram.ui import jobs_keyboard, main_reply_keyboard, review_keyboard, saved_keyboard, scan_status_details_keyboard, scan_status_keyboard, stretch_keyboard, vacancy_details_keyboard, vacancy_section_keyboard
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
# Candidate data and account actions belong to private chats. Channel posts
# use their own observer and remain available to the selected-channel watcher.
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
_ACTIVE_SCAN_TASKS: dict[int, asyncio.Task] = {}
_PENDING_RESUME_IMPORTS: dict[str, dict] = {}
_RESUME_IMPORT_TTL_SECONDS = 15 * 60
_MAX_PENDING_RESUME_IMPORTS = 64
_MAX_PENDING_RESUME_IMPORTS_PER_USER = 8


def _store_pending_resume_import(token: str, pending: dict) -> None:
    """Bound in-memory CV previews by age, per-owner count and total count."""
    now = time.time()
    for old_token, old in list(_PENDING_RESUME_IMPORTS.items()):
        created = old.get("created_at", 0)
        if not isinstance(created, (int, float)) or now - created > _RESUME_IMPORT_TTL_SECONDS:
            _PENDING_RESUME_IMPORTS.pop(old_token, None)

    owner = pending["user_id"]
    while True:
        owned = [
            (key, value) for key, value in _PENDING_RESUME_IMPORTS.items()
            if value.get("user_id") == owner
        ]
        if len(owned) < _MAX_PENDING_RESUME_IMPORTS_PER_USER and len(_PENDING_RESUME_IMPORTS) < _MAX_PENDING_RESUME_IMPORTS:
            break
        candidates = owned if len(owned) >= _MAX_PENDING_RESUME_IMPORTS_PER_USER else list(_PENDING_RESUME_IMPORTS.items())
        oldest = min(candidates, key=lambda item: item[1].get("created_at", 0))[0]
        _PENDING_RESUME_IMPORTS.pop(oldest, None)
    _PENDING_RESUME_IMPORTS[token] = pending


def _render_search_profiles(searches: dict, *, limit: int = 900) -> str:
    if limit <= 0:
        return ""
    lines = []
    for info in searches.values():
        line = (
            f"• {html.escape(str(info.get('name') or 'Search')[:80])}: "
            f"{int(info.get('processed', 0))} обработано, "
            f"{int(info.get('qualified', 0))} Good, "
            f"{int(info.get('stretch', 0))} Stretch, "
            f"{int(info.get('filtered', 0))} ниже scoring, "
            f"{int(info.get('preference_filtered', 0))} исключено настройками"
        )
        reasons = render_filter_reason_counts(
            info.get("preference_exclusion_reasons"),
            info.get("scoring_exclusion_reasons"),
        )
        if reasons:
            line += "\n  Основные причины: " + html.escape(reasons)
        if utf16_length("\n".join(lines + [line])) > limit:
            suffix = "… Остальные профили сохранены в диагностике."
            if utf16_length(suffix) > limit:
                return "…"
            while lines and utf16_length("\n".join(lines + [suffix])) > limit:
                lines.pop()
            lines.append(suffix)
            break
        lines.append(line)
    return "\n".join(lines)


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
        "/employerpolicy — ALLOW/WARN/BLOCK для категории или точного работодателя\n\n"
        "🧠 <b>Профиль и вакансии</b>\n"
        "/job 25 — подробности вакансии\n"
        "/compare 25 — сравнить вакансию с профилем\n"
        "/resumediff 25 [resume_id] — сверить CV с вакансией\n"
        "/prepare 25 [career|relocation] — подготовить и сохранить пакет\n"
        "/interview 25 [career|relocation] — практические задания по вакансии\n"
        "/applications — сохранённые пакеты и отклики\n"
        "/application &lt;id&gt; &lt;status|history|export&gt; — статус, история или экспорт\n"
        "/english [A1–C2|unknown] — уровень английского\n"
        "/facts — факты кандидата\n"
        "/import — импортировать резюме PDF/DOCX/TXT\n"
        "/resumes — варианты резюме\n"
        "/sources — источники вакансий\n"
        "/channels — подписки на Telegram-каналы и статистика\n\n"
        "🤖 <b>Агент</b>\n"
        "/status — состояние агента\n"
        "/delivery — журнал доставки уведомлений о вакансиях\n"
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
    await message.answer(
        _main_menu_text(),
        parse_mode="HTML",
        reply_markup=main_reply_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    await message.answer(
        _main_menu_text(),
        parse_mode="HTML",
        reply_markup=main_reply_keyboard(),
    )


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


@router.message(Command("delivery"))
async def delivery_status_command(message: Message) -> None:
    """Show per-user notification state without exposing vacancy content."""
    user = await _require_user(message)
    if not user:
        return
    try:
        entries = await delivery_repo.recent_job_notification_journal(user.id)
    except Exception:
        await message.answer("⚠️ Журнал доставки временно недоступен.")
        return
    if not entries:
        await message.answer("📬 Журнал уведомлений пока пуст.")
        return
    status_labels = {
        "sent": "✅ доставлено",
        "retry": "🔁 ожидает повтора",
        "sending": "⏳ отправляется / ожидает подтверждения",
    }
    lines = ["📬 <b>Журнал доставки вакансий</b>"]
    for entry in entries:
        label = status_labels.get(entry["status"], "⚠️ неизвестно")
        lines.append(
            f"#{html.escape(str(entry['match_id']))}: {label} "
            f"· попыток {html.escape(str(entry['attempts']))}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


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
        f"Английский: {html.escape(getattr(profile, 'english_level', '') or 'не указан')}\n"
        f"Базовая страна: {html.escape(user.current_country or 'RU')}\n"
        f"Обработано вакансий: {st['matches']}\n"
        f"Подходящих/уведомлённых: {st['notified']}\n"
        f"Отфильтровано/дубликаты: {st['filtered']}\n"
        f"Откликов: {st['applications']}\n"
        f"LLM: {'ON' if settings.openai_api_key else 'fallback'}\n"
        f"HH поиск: PUBLIC/ANONYMOUS\n"
        f"HH private actions: {'ON' if hh_client.private_api_available else 'OFF'}\n"
        "Автоотклик: не реализован; отправка только вручную"
        + (" (AUTO_APPLY=true сейчас не запускает отклики)" if settings.auto_apply else ""),
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
    parts = text.split()
    if len(parts) == 3 and parts[1].casefold() == "strict":
        enabled_text = parts[2].casefold()
        if enabled_text not in {"on", "off"}:
            await message.answer("Формат: /salary strict on|off")
            return
        enabled = enabled_text == "on"
        for search in searches:
            updated = dict(search.settings or {})
            if enabled:
                updated["strict_salary_floor"] = True
            else:
                updated.pop("strict_salary_floor", None)
            await repo.update_search_settings(
                search.id, updated,
            )
        await message.answer(
            "✅ Строгий зарплатный фильтр " + ("включён." if enabled else "выключен.")
            + " Исключаются только вакансии с подтверждённой структурированной "
            "зарплатой известного периода ниже месячного минимума; неизвестные валюты, "
            "периоды и неполные данные остаются в выдаче."
        )
        return
    if len(text.split()) == 1:
        cfg = searches[0].settings or {}
        def show(key: str) -> str:
            values = cfg.get(f"{key}_salary") or (cfg.get("minimum_salary", {}) if key == "minimum" else {})
            return ", ".join(f"{currency} {amount:,}".replace(",", " ") for currency, amount in sorted(values.items())) or "не задана"
        await message.answer(
            "💰 Зарплатные ориентиры для оценки совпадения\n"
            f"Текущая: {show('current')}\nЖелаемая: {show('desired')}\nМесячный минимум для оценки: {show('minimum')}\n\n"
            f"Строгий фильтр: {'включён' if cfg.get('strict_salary_floor') is True else 'выключен'}\n"
            "Обычный минимум только влияет на оценку и не скрывает вакансии. "
            "Строгий режим удаляет только структурированные зарплаты известного периода, "
            "подтверждённо ниже минимума. Неизвестный период остаётся в выдаче. "
            "Суммы только в тексте объявления не пересчитываются и не сравниваются.\n\n"
            "Формат: /salary current|desired|minimum USD 3000; очистить: /salary desired USD clear; "
            "строгий фильтр: /salary strict on|off"
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
        terms = [str(term) for term in (cfg.get("exclude_terms") or []) if str(term).casefold() not in LEGACY_INDUSTRY_EXCLUSIONS]
        await message.answer("🚫 Исключаемые слова: " + (", ".join(terms) or "нет") + "\nОтраслевые решения: /employerpolicy\nДобавить: /blacklist add <слово>\nУдалить: /blacklist remove <слово>\nОчистить: /blacklist clear")
        return
    action = parts[1].casefold()
    term = parts[2].strip() if len(parts) == 3 else ""
    if action not in {"add", "remove", "clear"} or (action != "clear" and not term):
        await message.answer("Формат: /blacklist add|remove <слово> или /blacklist clear")
        return
    for search in searches:
        await repo.update_search_settings(search.id, update_blacklist(search.settings or {}, action, term))
    await message.answer("✅ Blacklist обновлён.")


@router.message(Command("employerpolicy"))
async def employer_policy_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    searches = await repo.list_search_profiles(profile.id) if profile else []
    if not searches:
        await message.answer("❌ Профиль поиска не найден.")
        return
    parts = (message.text or "").split(maxsplit=3)
    settings = searches[0].settings or {}
    defaults = (load_profile().get("search") or {}).get("employer_policy") or {}
    if len(parts) == 1:
        overrides = settings.get("employer_policy_overrides") or {}
        await message.answer(
            "Политика работодателей (ALLOW/WARN/BLOCK). Категории: "
            + ", ".join(f"{key}={value}" for key, value in (defaults.get("categories") or {}).items())
            + "\nРучные решения: " + html.escape(str(overrides))
            + "\n/employerpolicy category <категория> <allow|warn|block|inherit>"
            + "\n/employerpolicy employer <allow|warn|block|inherit> <точное имя работодателя>"
        )
        return
    if len(parts) < 4:
        await message.answer("Формат: /employerpolicy category <категория> <решение> или /employerpolicy employer <решение> <точное имя>")
        return
    kind = parts[1].casefold()
    if kind == "category":
        key, value = parts[2], parts[3].strip()
    elif kind == "employer":
        value, key = parts[2].casefold(), parts[3].strip()
    else:
        await message.answer("Тип правила: category или employer.")
        return
    try:
        update_employer_policy(settings, kind, value, key)
        for search in searches:
            await repo.update_search_settings(search.id, update_employer_policy(search.settings or {}, kind, value, key))
    except ValueError as exc:
        await message.answer("❌ " + str(exc))
        return
    await message.answer("✅ Решение сохранено для всех поисковых профилей.")


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


@router.message(Command("english"))
async def english_level(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    if not profile:
        await message.answer("Профиль кандидата не найден.")
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        current = profile.english_level or "не указан"
        await message.answer(
            f"Английский в профиле: <b>{html.escape(current)}</b>. "
            "Изменить: /english B2; очистить: /english unknown.",
            parse_mode="HTML",
        )
        return

    raw_level = parts[1].strip()
    if raw_level.casefold() in {"unknown", "clear", "неизвестно", "не указан"}:
        await repo.set_profile_english_level(profile.id, "")
        await message.answer("✅ Уровень английского очищен; сравнение будет показывать неизвестно.")
        return

    normalized = normalize_cefr(raw_level)
    if normalized is None:
        await message.answer("Укажи CEFR-уровень A1, A1+, A2, A2+, B1, B1+, B2, B2+, C1, C1+ или C2.")
        return

    await repo.set_profile_english_level(profile.id, normalized)
    await message.answer(f"✅ Английский в профиле: <b>{normalized}</b>.", parse_mode="HTML")


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
        f"Ориентир зарплаты для оценки: {minimum or 'не задан'} RUB net (не фильтр)\n"
        f"Строгий зарплатный фильтр: {'ON' if cfg.get('strict_salary_floor') is True else 'OFF'}\n"
        "Неизвестный зарплатный период строгим фильтром не сравнивается.\n"
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
    pending = {
        "user_id": user.id, "profile_id": profile.id,
        "content": content, "fingerprint": fingerprint, "language": guess_language(content),
        "role": profile.target_role or "", "proposals": review.new,
        "overlaps": review.overlaps, "choices": {}, "duplicates_count": len(review.duplicates),
        "created_at": time.time(),
    }
    _store_pending_resume_import(token, pending)

    text, keyboard = render_import_preview(pending, token)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rchoice:"))
async def choose_resume_fact(callback: CallbackQuery) -> None:
    parts = (callback.data or "").split(":")
    if len(parts) != 4 or not parts[2].isascii() or not parts[2].isdigit() or len(parts[2]) > 2:
        await callback.answer("Некорректный выбор", show_alert=True)
        return
    _, token, index_text, action = parts
    pending = _PENDING_RESUME_IMPORTS.get(token)
    if not pending or time.time() - pending["created_at"] > _RESUME_IMPORT_TTL_SECONDS:
        await callback.answer("Предпросмотр истёк. Отправь документ заново.", show_alert=True)
        return
    user = await repo.get_user_by_chat(callback.message.chat.id) if callback.message else None
    if not user or user.id != pending["user_id"]:
        await callback.answer("Этот импорт предназначен другому профилю.", show_alert=True)
        return
    if _PENDING_RESUME_IMPORTS.get(token) is not pending:
        await callback.answer("Импорт уже обрабатывается.", show_alert=True)
        return
    index = int(index_text)
    try:
        if action == "summary":
            text, keyboard = render_import_preview(pending, token)
        else:
            # Validate the target before changing an in-memory decision.
            render_import_conflict(pending, token, index)
            if action in {"add", "update", "keep"}:
                choices = {**pending.get("choices", {}), index: action}
                plan_fact_import(pending["proposals"], pending["overlaps"], choices)
                pending["choices"] = choices
            elif action != "show":
                raise ValueError("Неизвестный выбор.")
            text, keyboard = render_import_conflict(pending, token, index)
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("rimp:"))
async def confirm_resume_import(callback: CallbackQuery) -> None:
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3:
        await callback.answer("Некорректная команда", show_alert=True)
        return
    action, token = parts[1], parts[2]
    pending = _PENDING_RESUME_IMPORTS.get(token)
    if not pending or time.time() - pending["created_at"] > _RESUME_IMPORT_TTL_SECONDS:
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
    if action == "review":
        if _PENDING_RESUME_IMPORTS.get(token) is not pending:
            await callback.answer("Импорт уже обрабатывается.", show_alert=True)
            return
        try:
            text, keyboard = render_import_conflict(pending, token)
        except ValueError as exc:
            await callback.answer(str(exc), show_alert=True)
            return
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        return
    if action not in {"resume", "facts"}:
        await callback.answer("Неизвестное действие", show_alert=True)
        return
    plan = plan_fact_import(pending["proposals"], pending["overlaps"], pending.get("choices"))
    # Claim the preview before the first persistence await. Two Telegram callback
    # deliveries must not save the same resume/facts concurrently.
    if _PENDING_RESUME_IMPORTS.pop(token, None) is None:
        await callback.answer("Импорт уже обрабатывается. Проверь /resumes.", show_alert=True)
        return
    facts = [
        {"category": proposal.category, "value": proposal.value,
         "confidence": proposal.confidence, "section": proposal.section}
        for proposal in plan.additions
    ] if action == "facts" else []
    replacements = [
        {"existing_id": overlap.existing_id, "expected_value": overlap.existing_value,
         "category": overlap.proposal.category, "value": overlap.proposal.value,
         "confidence": overlap.proposal.confidence, "section": overlap.proposal.section}
        for overlap in plan.replacements
    ] if action == "facts" else []
    try:
        resumes = await repo.list_resumes(pending["profile_id"])
        if any(resume.external_id == pending["fingerprint"] for resume in resumes):
            await callback.message.edit_text("ℹ️ Такое резюме уже импортировано.")
            await callback.answer()
            return
        item = await repo.add_imported_resume_with_facts(
            pending["profile_id"], f"Imported resume {datetime.now():%Y-%m-%d}",
            pending["language"], pending["role"], pending["content"],
            pending["fingerprint"], facts, replacements=replacements,
        )
    except repo.FactUpdateConflict as exc:
        _PENDING_RESUME_IMPORTS.setdefault(token, pending)
        await callback.answer(str(exc), show_alert=True)
        return
    except repo.ResumeImportExists as exc:
        _PENDING_RESUME_IMPORTS.pop(token, None)
        await callback.message.edit_text(
            f"ℹ️ Такое резюме уже импортировано (#{exc.resume_id}). Проверь /resumes."
        )
        await callback.answer("Импорт уже выполнен")
        return
    except Exception:
        # The repository operation is transactional. Retain the one-time preview
        # so a transient DB failure can be retried without re-uploading the file.
        _PENDING_RESUME_IMPORTS.setdefault(token, pending)
        await callback.answer("Не удалось сохранить импорт. Попробуй ещё раз.", show_alert=True)
        return
    added = len(facts)
    _PENDING_RESUME_IMPORTS.pop(token, None)
    await callback.message.edit_text(f"✅ Резюме #{item.id} сохранено." + (f" Добавлено фактов: {added}. Обновлено: {len(replacements)}." if action == "facts" else " Факты не изменялись."))
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

    async def mark_started() -> None:
        await _save_scan_dashboard(user.id, reset=True, status="running", stage=stage, started_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))

    try:
        summary = await coordinated_scan_for_user(bot, user.id, progress_callback=update_progress, force_refresh=True, on_start=mark_started)
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

        outcome = scan_outcome(summary)
        await _save_scan_dashboard(user.id, status=outcome, stage="Готово" if outcome == "completed" else "Завершено с неполными результатами", finished_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), summary=summary)
        details = render_source_dashboard(summary.get("sources") or {}) or "• активных источников нет"
        profile_bits = _render_search_profiles(summary.get("searches") or {})
        profile_details = "\n\n<b>Профили поиска</b>\n" + profile_bits if profile_bits else ""

        await progress.edit_text(
            ("✅ <b>Проход поиска завершён</b>\n\n" if outcome == "completed" else "⚠️ <b>Поиск завершён с неполными результатами</b>\n\n")
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
    except ScanAlreadyRunning:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        await progress.edit_text("⏳ Поиск уже выполняется в другом процессе. Проверь /scanstatus позже.")
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
        issue = classify_source_error(exc, stage="scan")
        await _save_scan_dashboard(user.id, status="failed", stage=issue["code"], finished_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
        await progress.edit_text(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
            parse_mode="HTML",
        )
    finally:
        if _ACTIVE_SCAN_TASKS.get(user.id) is task:
            _ACTIVE_SCAN_TASKS.pop(user.id, None)


async def _scan_dashboard_for_user(user_id: int) -> dict:
    try:
        state = json.loads(await repo.get_state(user_id, "scan_dashboard", "{}"))
    except (TypeError, ValueError):
        state = {}
    try:
        scheduled = json.loads(await repo.get_state(user_id, "scheduled_scan_dashboard", "{}"))
    except (TypeError, ValueError):
        scheduled = {}
    return select_scan_dashboard(state, scheduled)


def _scan_status_summary(state: dict) -> str:
    summary = state.get("summary") or {}
    sources = summary.get("sources") or {}
    health = {"success": 0, "partial": 0, "failed": 0, "skipped": 0}
    for info in sources.values():
        status = info.get("status")
        if status not in health:
            status = "failed" if info.get("error") else "skipped" if info.get("skipped") else "partial" if info.get("partial") else "success"
        health[status] += 1
    status = str(state.get("status", "неизвестно"))
    if status == "completed" and summary:
        status = scan_outcome(summary)
    title = "Плановый поиск" if state.get("kind") == "scheduled" else "Поиск"
    lines = [f"📊 <b>{title}: {html.escape(status)}</b>"]
    if sources:
        lines.append(
            f"Источники: ✅ {health['success']} · ⚠️ {health['partial']} · "
            f"❌ {health['failed']} · ⏸ {health['skipped']}"
        )
    elif state.get("status") == "running":
        lines.append("Источники ещё не завершили поиск.")
    lines.append(
        f"🟢 Good: {int(summary.get('qualified', 0))} · "
        f"🟡 Stretch: {int(summary.get('stretch', 0))} · "
        f"📨 Новых: {int(summary.get('notified', 0))}"
    )
    lines.append(f"Обработано: {int(summary.get('processed', 0))}")
    if state.get("status") == "running":
        lines.append("Этап: " + html.escape(str(state.get("stage") or "выполняется")[:120]))
    else:
        finished = str(state.get("finished_at") or "")
        if finished:
            lines.append("Завершено: " + html.escape(finished[:40]))
    return "\n".join(lines)


def _scan_status_details(state: dict) -> str:
    state = dict(state)
    if state.get("status") == "failed":
        state["stage"] = legacy_diagnostic(state.get("stage"))["code"]
    summary = state.get("summary") or {}
    if state.get("status") == "completed" and summary:
        state["status"] = scan_outcome(summary)
    sources = render_source_dashboard(summary.get("sources") or {})
    profiles = _render_search_profiles(summary.get("searches") or {})
    return (
        ("📊 Плановое сканирование: <b>" if state.get("kind") == "scheduled" else "📊 Сканирование: <b>")
        + f"{html.escape(str(state.get('status', 'неизвестно')))}</b>\n"
        f"Начато: {html.escape(str(state.get('started_at', '—')))}\n"
        f"Завершено: {html.escape(str(state.get('finished_at', '—')))}\n"
        f"Этап: {html.escape(str(state.get('stage', '—')))}\n"
        + (sources if sources else "Источники ещё не завершили поиск.")
        + ("\n\n<b>Профили поиска</b>\n" + profiles if profiles else "")
    )


@router.message(Command("scanstatus"))
async def scan_status(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    state = await _scan_dashboard_for_user(user.id)
    if not state:
        await message.answer("Истории сканирования пока нет. Запусти /scan.")
        return
    await message.answer(
        _scan_status_summary(state),
        parse_mode="HTML",
        reply_markup=scan_status_keyboard(),
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
            render_job_summary(payload),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=vacancy_details_keyboard(
                payload["job"].id, **search_filter,
            ),
        )
    except Exception as exc:
        issue = classify_source_error(exc, stage="detail_request")
        await progress.edit_text(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
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
        issue = classify_source_error(exc, stage="processing")
        await progress.edit_text(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
            parse_mode="HTML",
        )

@router.message(Command("interview"))
async def interview_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    if (
        len(parts) not in {2, 3}
        or not parts[1].isdigit()
        or (len(parts) == 3 and parts[2].casefold() not in {"career", "relocation"})
    ):
        await message.answer("Использование: /interview <vacancy_id> [career|relocation]")
        return
    search_filter = {}
    if len(parts) == 3:
        scope = parts[2].casefold()
        search = await _search_for_scope(user.id, scope)
        if not search:
            await message.answer(_missing_search_scope(scope))
            return
        search_filter = {"search_profile_id": search.id}
    progress = await message.answer("⏳ Готовлю задания по требованиям вакансии…")
    try:
        payload = await get_vacancy_comparison(user.id, int(parts[1]), **search_filter)
        plan = build_interview_plan(payload["comparison"])
        await progress.edit_text(
            render_interview_plan(payload["job"], plan),
            parse_mode="HTML",
        )
    except Exception as exc:
        issue = classify_source_error(exc, stage="processing")
        await progress.edit_text(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
            parse_mode="HTML",
        )


@router.message(Command("resumediff"))
async def resume_diff_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    if (
        len(parts) not in {2, 3}
        or not parts[1].isdigit()
        or (len(parts) == 3 and not parts[2].isdigit())
    ):
        await message.answer("Использование: /resumediff <vacancy_id> [resume_id]")
        return
    progress = await message.answer("⏳ Сверяю требования с выбранным резюме и Candidate Facts…")
    try:
        payload = await get_resume_diff(
            user.id,
            int(parts[1]),
            **({"resume_id": int(parts[2])} if len(parts) == 3 else {}),
        )
        await progress.edit_text(render_resume_diff(payload), parse_mode="HTML")
    except Exception as exc:
        issue = classify_source_error(exc, stage="processing")
        await progress.edit_text(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
            parse_mode="HTML",
        )


async def _prepare_saved_preview(match_id: int, user_id: int) -> str:
    existing = await repo.prepared_application_for_match(match_id, user_id)
    if existing is not None:
        return (
            f"ℹ Черновик отклика #{existing.id} уже сохранён; новый дубликат не создан. "
            f"Проверь /applications или экспортируй: /application {existing.id} export"
        )
    result = await prepare_match(match_id, user_id)
    preview = render_application_package(result)
    application, created = await repo.save_prepared_application(
        match_id=match_id, user_id=user_id,
        job_id=result["job"].id,
        source_id=str(result.get("source") or "manual")[:64],
        source_application_id=None,
        external_url=str(result.get("url") or "") or None,
        resume_id=result["resume"].id if result.get("resume") else None,
        resume_snapshot=str(result["resume"].content or "") if result.get("resume") else "",
        resume_external_id=(
            str(result["resume"].external_id)[:256]
            if result.get("resume") and result["resume"].external_id
            else None
        ),
        vacancy_snapshot=snapshot_vacancy(
            result["job"], source_id=result.get("source"),
            source_job_id=result.get("source_job_id"), source_url=result.get("url"),
            relocation_evidence=result.get("relocation_evidence"),
        ),
        message=str(result.get("cover_letter") or ""),
    )
    if not created:
        return (
            f"ℹ Черновик отклика #{application.id} уже сохранён; новый дубликат не создан. "
            f"Проверь /applications или экспортируй: /application {application.id} export"
        )
    return preview + f"\n\n💾 Черновик письма сохранён как отклик #{application.id}. /applications"


def _prepare_error_text(exc: Exception, *, package_saved: bool) -> str:
    issue = classify_source_error(exc, stage="processing")
    text = f"⚠ {html.escape(issue['message'])} Код: {issue['code']}."
    if package_saved:
        return text + " Пакет сохранён; открой /applications. Повторная подготовка нового пакета не создаст дубликат."
    return text + " Проверь /applications перед повтором."


@router.message(Command("prepare"))
async def prepare_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    if (
        len(parts) not in {2, 3}
        or not parts[1].isdigit()
        or (len(parts) == 3 and parts[2].casefold() not in {"career", "relocation"})
    ):
        await message.answer("Использование: /prepare <vacancy_id> [career|relocation]")
        return
    search_filter = {}
    if len(parts) == 3:
        scope = parts[2].casefold()
        search = await _search_for_scope(user.id, scope)
        if not search:
            await message.answer(_missing_search_scope(scope))
            return
        search_filter = {"search_profile_id": search.id}
    progress = await message.answer("⏳ Готовлю пакет для твоей проверки…")
    try:
        match = await repo.get_match_for_user_job(user.id, int(parts[1]), **search_filter)
        if not match:
            await progress.edit_text("❌ Вакансия не найдена среди твоих совпадений в выбранном поиске.")
            return
        preview = await _prepare_saved_preview(match.id, user.id)
    except Exception as exc:
        await progress.edit_text(
            _prepare_error_text(exc, package_saved=False),
            parse_mode="HTML",
        )
        return
    try:
        await progress.edit_text(preview, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await message.answer(
            "⚠ Пакет уже сохранён, но Telegram не показал подтверждение. "
            "Проверь /applications; повторная подготовка нового пакета не создаст дубликат."
        )


@router.message(Command("applications"))
async def applications_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    applications = await repo.list_applications(user.id, limit=12)
    await message.answer(render_applications(applications), parse_mode="HTML")


@router.message(Command("application"))
async def application_status_command(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    parts = (message.text or "").split()
    if len(parts) != 3 or not parts[1].isdigit():
        await message.answer(
            "Использование: /application <id> history|export|reviewed|submitted|interview|offer|rejected|withdrawn"
        )
        return
    status = parts[2].casefold()
    if status == "export":
        application = await repo.get_application(user.id, int(parts[1]))
        if not application:
            await message.answer("❌ Отклик не найден в твоём профиле.")
            return
        events = await repo.application_status_history(user.id, application.id)
        content = render_application_export(application, events).encode("utf-8")
        if len(content) > MAX_DOCUMENT_BYTES:
            await message.answer("❌ Пакет превышает безопасный размер экспорта 8 MiB.")
            return
        await message.answer_document(
            BufferedInputFile(content, filename=f"application-{application.id}.txt"),
            caption=f"Пакет #{application.id}. Содержимое сохранено на момент подготовки.",
        )
        return
    if status == "history":
        events = await repo.application_status_history(user.id, int(parts[1]))
        await message.answer(
            "❌ Отклик не найден в твоём профиле."
            if events is None
            else render_application_history(events),
            parse_mode="HTML",
        )
        return
    if status not in repo.MANUAL_APPLICATION_STATUSES:
        await message.answer(
            "Допустимые статусы: reviewed, submitted, interview, offer, rejected, withdrawn"
        )
        return
    updated = await repo.set_application_status(user.id, int(parts[1]), status)
    await message.answer(
        "✅ Статус обновлён вручную."
        if updated
        else "❌ Отклик не найден в твоём профиле."
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
            render_job_summary(payload),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=vacancy_details_keyboard(payload["job"].id, **search_filter),
        )
    except Exception as exc:
        issue = classify_source_error(exc, stage="detail_request")
        await callback.message.answer(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}", parse_mode="HTML"
        )


def _jobtab_identifiers(data: str) -> tuple[str, int, int | None] | None:
    parts = data.split(":")
    if len(parts) not in {3, 4} or parts[0] != "jobtab":
        return None
    section = parts[1]
    if section not in {"summary", "req", "desc", "terms", "competition", "source"}:
        return None
    if not all(value.isdigit() for value in parts[2:]):
        return None
    return section, int(parts[2]), int(parts[3]) if len(parts) == 4 else None


@router.callback_query(F.data.startswith("jobtab:"))
async def jobtab_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    identifiers = _jobtab_identifiers(callback.data)
    if identifiers is None:
        await callback.answer("Некорректная кнопка вакансии", show_alert=True)
        return
    section, job_id, search_profile_id = identifiers
    try:
        search_filter = {"search_profile_id": search_profile_id} if search_profile_id is not None else {}
        payload = await get_vacancy_details(user.id, job_id, **search_filter)
        selected_id = getattr(payload.get("match"), "search_profile_id", None)
        if selected_id is not None:
            search_profile_id = selected_id
        text = render_job_summary(payload) if section == "summary" else render_job_section(payload, section)
        keyboard = (
            vacancy_details_keyboard(job_id, search_profile_id=search_profile_id)
            if section == "summary"
            else vacancy_section_keyboard(job_id, search_profile_id=search_profile_id)
        )
        await callback.message.edit_text(
            text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard
        )
        await callback.answer()
    except Exception as exc:
        issue = classify_source_error(exc, stage="detail_request")
        await callback.answer(f"{issue['message']} ({issue['code']})", show_alert=True)


@router.callback_query(F.data.startswith("scanstatus:"))
async def scan_status_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    mode = callback.data.split(":", 1)[1]
    if mode not in {"summary", "details"}:
        await callback.answer("Некорректная кнопка", show_alert=True)
        return
    state = await _scan_dashboard_for_user(user.id)
    if not state:
        await callback.answer("Истории поиска пока нет", show_alert=True)
        return
    await callback.message.edit_text(
        _scan_status_details(state) if mode == "details" else _scan_status_summary(state),
        parse_mode="HTML",
        reply_markup=scan_status_details_keyboard() if mode == "details" else scan_status_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def main_menu_callback(callback: CallbackQuery) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    await callback.message.edit_text(
        "🤖 <b>Главное меню</b>\n"
        "/scan — новый поиск · /scanstatus — состояние\n"
        "/review — Good · /stretch — Stretch · /saved — сохранённые\n"
        "/jobs career — Career-first · /jobs relocation — Relocation-first\n"
        "/help — все команды",
        parse_mode="HTML",
    )
    await callback.answer()


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
        issue = classify_source_error(exc, stage="processing")
        await callback.message.answer(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}",
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
    raw_id = callback.data.split(":", 1)[1]
    if not raw_id.isdigit():
        await callback.answer("Некорректный ID", show_alert=True)
        return
    match_id = int(raw_id)
    await callback.answer("Готовлю…")
    try:
        preview = await _prepare_saved_preview(match_id, user.id)
    except Exception as exc:
        issue = classify_source_error(exc, stage="processing")
        await callback.message.answer(
            f"⚠ {html.escape(issue['message'])} Код: {issue['code']}. Проверь /applications перед повтором.",
            parse_mode="HTML",
        )
        return
    try:
        await callback.message.answer(
            preview,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception:
        await callback.message.answer(
            "⚠ Пакет уже сохранён, но Telegram не показал подтверждение. "
            "Проверь /applications; повторная подготовка нового пакета не создаст дубликат."
        )


@router.callback_query(F.data.startswith("apply:"))
async def apply_callback(callback: CallbackQuery, bot: Bot) -> None:
    user = await repo.get_user_by_chat(callback.message.chat.id)
    if not user:
        return
    raw_match_id = (callback.data or "").partition(":")[2]
    if not raw_match_id.isdecimal() or len(raw_match_id) > 18 or int(raw_match_id) <= 0:
        await callback.answer("Неверный идентификатор отклика.", show_alert=True)
        return
    match_id = int(raw_match_id)
    await callback.answer("Отправляю…")
    try:
        result = await apply_match(bot, match_id, user.id)
        status = result.get("status")
        if status == "sent":
            text = f"✅ HH подтвердил отправку отклика. Запись #{result.get('application_id', '?')} в /applications."
        elif status == "external":
            text = (
                "↗ HH направил на внешнюю форму работодателя. "
                "Отклик ещё не подтверждён как отправленный: заверши его вручную. "
                f"Запись #{result.get('application_id', '?')} сохранена в /applications; "
                "адрес перехода доступен в экспорте через /application <id> export."
            )
        else:
            text = (
                "⚠️ Статус отправки HH неизвестен. Перед повтором проверь кабинет HH "
                "и /applications, чтобы не отправить повторный отклик."
            )
        await callback.message.answer(text, parse_mode=None)
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as exc:
        # Only our own predictable user-facing RuntimeErrors may be shown.
        # Provider, database and parser exceptions may carry sensitive details.
        safe_prefixes = (
            "Match не найден",
            "HH private applicant API доступен только owner-профилю",
            "Вакансия не найдена",
            "Для этой вакансии нет HH-источника",
            "HH private applicant API отключён",
            "Для выбранного профиля нет HH resume ID",
            "HH owner не найден или отключён",
            "Повторный HH-отклик заблокирован:",
            "HH не подтвердил результат попытки #",
            "Статус HH попытки #",
        )
        detail = str(exc)
        if isinstance(exc, RuntimeError) and detail.startswith(safe_prefixes):
            message = detail
        else:
            issue = classify_source_error(exc, stage="processing")
            message = (
                "Не удалось завершить HH-отклик. Проверь /applications "
                f"и кабинет HH перед повтором. Код: {issue['code']}."
            )
        await callback.message.answer(
            "⚠️ " + html.escape(message), parse_mode="HTML",
        )


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
    if str(callback.message.chat.id) != settings.telegram_admin_chat_id.strip():
        await callback.answer("HH-переписка доступна только владельцу.", show_alert=True)
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
                               message_id=message.message_id, text=text, published_at=message.date)


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
        if str(message.chat.id) != settings.telegram_admin_chat_id.strip():
            await repo.set_state(user.id, "manual_hh_reply", "")
            await message.answer("HH-переписка доступна только владельцу. Ожидающий ответ отменён.")
            return
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
