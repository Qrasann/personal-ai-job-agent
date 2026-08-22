from __future__ import annotations

import html

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.candidates.bootstrap import bootstrap_user
from app.config import settings
from app.database import repository as repo
from app.candidates.fact_types import ALLOWED_EXPERIENCE_TYPES, experience_type_label, normalize_experience_type
from app.database.db import current_schema_version, expected_schema_version
from app.geo.countries import all_supported_countries, country_config, normalize_country
from app.services import apply_match, prepare_match, ingest_and_match, scan_for_user, scan_hh_chats, hh_client
from app.sources.adapters.telegram_ingest import parse_telegram_job
from app.sources.registry import build_source_plan
from app.version import current_version

router = Router()


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
        "🤖 <b>Personal AI Job Agent</b>\n\n"
        "Поиск: 🇷🇺 Россия + 🌍 international remote + ✈️ relocation.\n\n"
        "/role DevOps Engineer — выбрать основную роль\n"
        "/roleadd Linux Administrator — добавить роль\n"
        "/roles — показать роли\n"
        "/mode — включить/выключить направления поиска\n"
        "/settings — текущие настройки\n"
        "/scan — поиск сейчас\n"
        "/jobs — последние совпадения\n"
        "/sources — источники\n"
        "/facts — факты кандидата\n"
        "/resumes — варианты резюме\n"
        "/chats — проверить HH-переписку\n"
        "/pause /resume — остановить/запустить\n\n"
        "Перешли сюда пост с вакансией из Telegram — он попадёт в тот же pipeline. Сообщения рекрутера обрабатываются одинаково, независимо от того, человек это или recruiter-AI.",
        parse_mode="HTML",
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
        f"International remote: {'ON' if modes.get('remote_international', True) else 'OFF'}\n"
        f"Relocation: {'ON' if modes.get('relocation', True) else 'OFF'}\n"
        f"Мин. РФ зарплата: {minimum or 'не задана'} RUB net\n"
        f"Notify score: {cfg.get('notify_min_score', 65)}+"
    )
    await message.answer(text, parse_mode="HTML")


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
    profile, search = await _first_search(user.id)
    if not search:
        return
    parts = (message.text or "").split(maxsplit=1)
    current = search.settings or {}
    if len(parts) == 1:
        await message.answer("🎯 Локальные рынки: " + ", ".join(current.get("target_countries") or []) or "не заданы")
        return
    raw = parts[1].strip()
    values = [] if raw.casefold() == "clear" else [x.strip() for x in raw.split(",") if x.strip()]
    codes = []
    for value in values:
        code = normalize_country(value)
        if not code:
            await message.answer(f"❌ Неизвестная страна: {html.escape(value)}")
            return
        if code not in codes:
            codes.append(code)
    current["target_countries"] = codes
    await repo.update_search_settings(search.id, current)
    await message.answer("✅ Локальные рынки: " + (", ".join(codes) if codes else "очищены"))


@router.message(Command("sources"))
async def sources(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    targets = (search.settings or {}).get("target_countries") if search else []
    plan = build_source_plan(user.current_country or "RU", targets or [], include_international=True)
    lines = ["🧭 <b>Источники Personal Job Agent</b>"]
    for item in plan:
        flag = "✅" if item.implemented else "🧩"
        lines.append(f"{flag} {html.escape(item.name)} — {html.escape(item.scope)} — {html.escape(item.transport)}")
    lines.append("\n✅ = collector уже есть; 🧩 = источник зарегистрирован, нужен отдельный adapter.")
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
    await message.answer("🔎 Запускаю поиск по активным collectors для твоего геопрофиля.")
    summary = await scan_for_user(bot, user.id)
    source_bits = []
    for source_id, info in (summary.get("sources") or {}).items():
        if "error" in info:
            source_bits.append(f"• {html.escape(source_id)}: ошибка")
        else:
            cache = " (кэш)" if info.get("cache") else ""
            source_bits.append(f"• {html.escape(source_id)}: {int(info.get('found', 0))}{cache}")
    details = "\n".join(source_bits) or "• активных источников нет"
    await message.answer(
        "✅ <b>Проход поиска завершён</b>\n\n"
        + details
        + f"\n\nОбработано: {int(summary.get('processed', 0))}"
        + f"\nПрошли фильтр: {int(summary.get('qualified', 0))}"
        + f"\nНовых уведомлений: {int(summary.get('notified', 0))}"
        + f"\nДубликатов подавлено: {int(summary.get('duplicate', 0))}",
        parse_mode="HTML",
    )


@router.message(Command("jobs"))
async def jobs(message: Message) -> None:
    user = await _require_user(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    threshold = int(((search.settings or {}) if search else {}).get("notify_min_score", 65))
    rows = await repo.latest_matches(user.id, 10, min_score=threshold)
    if not rows:
        await message.answer("Пока совпадений нет. Запусти /scan.")
        return
    lines = ["🔥 <b>Последние совпадения</b>"]
    for match, job in rows:
        lines.append(f"{match.total_score}/100 — {html.escape(job.title)} — {html.escape(job.company)} — {match.status}")
    await message.answer("\n".join(lines), parse_mode="HTML")


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
        await repo.set_state(user.id, "manual_hh_reply", "")
        await message.answer("Отменено.")


@router.channel_post()
async def channel_post(message: Message, bot: Bot) -> None:
    text = message.text or message.caption or ""
    if not text.strip():
        return
    username = message.chat.username or str(message.chat.id)
    url = f"https://t.me/{message.chat.username}/{message.message_id}" if message.chat.username else ""
    job = parse_telegram_job(text, source_ref=f"channel:{username}:{message.message_id}", source_url=url)
    await ingest_and_match(bot, job)


@router.message(F.text)
async def generic_text(message: Message, bot: Bot) -> None:
    user = await _user(message)
    if not user:
        return
    pending = await repo.get_state(user.id, "manual_hh_reply", "")
    if pending:
        chat_id, _ = pending.split(":", 1)
        if str(message.chat.id) == settings.telegram_admin_chat_id.strip():
            await hh_client.send_chat_message(chat_id, message.text)
            await repo.set_state(user.id, "manual_hh_reply", "")
            await message.answer("✅ Сообщение отправлено в HH.")
        return

    # Forwarded Telegram vacancy: aiogram exposes forward_origin on modern Bot API.
    if getattr(message, "forward_origin", None) is not None:
        source_ref = f"forward:{message.chat.id}:{message.message_id}"
        job = parse_telegram_job(message.text, source_ref=source_ref)
        await ingest_and_match(bot, job, only_user_id=user.id)
        await message.answer("✅ Пересланный пост добавлен в общий pipeline и оценён для твоего профиля.")
