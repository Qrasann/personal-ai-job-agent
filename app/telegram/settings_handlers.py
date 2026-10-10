from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.database import repository as repo
from app.geo.countries import all_supported_countries, normalize_country
from app.search.preferences import SEARCH_STRATEGIES, discovery_queries, search_config, search_strategy
from app.sources.registry import IMPLEMENTED, build_source_plan
from app.telegram.settings_ui import countries_keyboard, geography_keyboard, next_policy, relocation_keyboard, settings_root_keyboard, source_keyboard, strategy_keyboard

router = Router(name="search-control")


async def _user_message(message: Message):
    return await repo.get_user_by_chat(message.chat.id)


async def _user_callback(callback: CallbackQuery):
    return await repo.get_user_by_chat(callback.message.chat.id)


async def _first_search(user_id: int):
    profile = await repo.active_profile(user_id)
    if not profile:
        return None, None
    searches = await repo.list_search_profiles(profile.id)
    return profile, searches[0] if searches else None


async def _search_for_kind(user_id: int, kind: str):
    profile = await repo.active_profile(user_id)
    if not profile:
        return None, None
    searches = await repo.list_search_profiles(profile.id)
    selected = next((item for item in searches if item.kind == kind), None)
    return profile, selected or (searches[0] if searches else None)


async def _save(search, cfg: dict):
    await repo.update_search_settings(search.id, cfg)
    search.settings = cfg


def _root_text(profile, settings: dict) -> str:
    cfg = search_config(settings)
    disabled = set(cfg.get("disabled_sources") or [])
    active = sorted(x for x in IMPLEMENTED if x not in disabled)
    return (
        "⚙️ <b>Search Control Center</b>\n\n"
        f"🎯 Роль: {html.escape(profile.target_role or '—')}\n"
        f"🧭 Стратегия: <b>{html.escape(search_strategy(cfg))}</b>\n"
        f"🔎 Источники: {html.escape(', '.join(active) or 'нет')}\n"
        f"🏙 Мой город: {html.escape(str(cfg.get('local_city') or 'не задан'))}\n"
        f"🏙 Доп. города: {html.escape(', '.join(cfg.get('selected_cities') or []) or 'нет')}\n"
        f"🌍 Страны: {html.escape(', '.join(cfg.get('target_countries') or []) or 'нет')}\n\n"
        "Приоритет 0–100 влияет на порядок обработки.\n"
        "Relocation policy: any → prefer → require → exclude.\n\n"
        "Доп. города: <code>/cities Москва, Санкт-Петербург</code>\n"
        "Relocation-роли: <code>/relocationroles warehouse, hotel staff</code>"
    )


@router.message(Command("settings"))
async def settings_command(message: Message) -> None:
    user = await _user_message(message)
    if not user:
        return
    profile, search = await _first_search(user.id)
    if not profile or not search:
        await message.answer("❌ Профиль поиска не найден.")
        return
    await message.answer(_root_text(profile, search.settings or {}), parse_mode="HTML", reply_markup=settings_root_keyboard())


@router.message(Command("cities"))
async def cities_command(message: Message) -> None:
    user = await _user_message(message)
    if not user:
        return
    _, search = await _first_search(user.id)
    if not search:
        return
    cfg = search_config(search.settings)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        await message.answer("🏙 Выбранные города: " + (", ".join(cfg.get("selected_cities") or []) or "нет"))
        return
    raw = parts[1].strip()
    cities = [] if raw.casefold() == "clear" else [x.strip() for x in raw.split(",") if x.strip()]
    cfg["selected_cities"] = list(dict.fromkeys(cities))
    geo = dict(cfg.get("geography") or {})
    geo["configured"] = True
    cfg["geography"] = geo
    await _save(search, cfg)
    await message.answer("✅ Города: " + (", ".join(cities) if cities else "очищены"))


@router.message(Command("relocationroles"))
async def relocation_roles_command(message: Message) -> None:
    user = await _user_message(message)
    if not user:
        return
    profile, search = await _search_for_kind(user.id, "relocation")
    if not search:
        return
    cfg = search_config(search.settings)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        roles = cfg.get("relocation_queries") or []
        await message.answer("✈️ Relocation-роли: " + (", ".join(roles) or "не заданы"))
        return
    raw = parts[1].strip()
    roles = [] if raw.casefold() == "clear" else [item.strip() for item in raw.split(",") if item.strip()]
    cfg["relocation_queries"] = list(dict.fromkeys(roles))
    await _save(search, cfg)
    active = discovery_queries(cfg, profile.target_role)
    await message.answer(
        "✅ Relocation-роли: " + (", ".join(roles) if roles else "очищены")
        + "\nАктивные запросы: " + (", ".join(active) or "нет")
    )


@router.message(Command("parallelsearch"))
async def parallel_search_command(message: Message) -> None:
    user = await _user_message(message)
    if not user:
        return
    profile = await repo.active_profile(user.id)
    if not profile:
        return
    parts = (message.text or "").split(maxsplit=1)
    action = parts[1].strip().casefold() if len(parts) > 1 else "status"
    if action not in {"on", "off", "status"}:
        await message.answer("Использование: /parallelsearch on|off|status")
        return
    if action != "status":
        await repo.configure_parallel_search_profiles(profile.id, enabled=action == "on")
    searches = await repo.list_search_profiles(profile.id)
    relocation_active = any(item.kind == "relocation" for item in searches)
    await message.answer(
        "🧭 Параллельный поиск: " + ("ON" if relocation_active else "OFF")
        + "\nАктивные профили: " + (", ".join(item.name for item in searches) or "нет")
        + "\nНастройте широкий трек через /relocationroles."
    )


@router.callback_query(F.data == "cfg:strategy")
async def strategy_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    if not user:
        return
    _, search = await _first_search(user.id)
    await callback.message.edit_text(
        "🧭 <b>Стратегия поиска</b>\n"
        "Career-first использует карьерные запросы.\n"
        "Relocation-first использует relocation-роли и выше ставит вакансии с подтверждаемыми сигналами поддержки.\n"
        "Balanced запускает оба набора. Unknown не считается отказом.",
        parse_mode="HTML",
        reply_markup=strategy_keyboard(search.settings or {}),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cfg:strategy:"))
async def strategy_set_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    value = callback.data.split(":", 2)[2]
    if not user or value not in SEARCH_STRATEGIES:
        return
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    cfg["search_strategy"] = value
    await _save(search, cfg)
    await strategy_callback(callback)


@router.callback_query(F.data == "cfg:root")
async def root_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    if not user:
        return
    profile, search = await _first_search(user.id)
    await callback.message.edit_text(_root_text(profile, search.settings or {}), parse_mode="HTML", reply_markup=settings_root_keyboard())
    await callback.answer()


@router.callback_query(F.data == "cfg:sources")
async def sources_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    if not user:
        return
    _, search = await _first_search(user.id)
    plan = build_source_plan(user.current_country or "RU", (search.settings or {}).get("target_countries") or [], include_international=True)
    ids = sorted({x.source_id for x in plan if x.implemented} | set(IMPLEMENTED))
    await callback.message.edit_text("🔎 <b>Источники</b>\nСлева — включить/исключить, ⭐ — приоритет.", parse_mode="HTML", reply_markup=source_keyboard(ids, search.settings or {}))
    await callback.answer()


@router.callback_query(F.data.startswith("cfg:src:"))
async def source_toggle(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    source_id = callback.data.split(":", 2)[2]
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    disabled = set(cfg.get("disabled_sources") or [])
    disabled.remove(source_id) if source_id in disabled else disabled.add(source_id)
    cfg["disabled_sources"] = sorted(disabled)
    await _save(search, cfg)
    await sources_callback(callback)


@router.callback_query(F.data.startswith("cfg:srcp:"))
async def source_priority_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    source_id = callback.data.split(":", 2)[2]
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    priorities = dict(cfg.get("source_priorities") or {})
    priorities[source_id] = (int(priorities.get(source_id, 50)) + 25) % 125
    cfg["source_priorities"] = priorities
    await _save(search, cfg)
    await sources_callback(callback)


@router.callback_query(F.data == "cfg:geo")
async def geo_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    _, search = await _first_search(user.id)
    await callback.message.edit_text("🌍 <b>География</b>\nРежимы можно комбинировать.", parse_mode="HTML", reply_markup=geography_keyboard(search.settings or {}))
    await callback.answer()


@router.callback_query(F.data.startswith("cfg:geo:"))
async def geo_toggle(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    key = callback.data.split(":", 2)[2]
    defaults = {"include_current_city": True, "include_other_cities": False, "include_other_countries": True, "worldwide": False}
    if key not in defaults:
        return
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    geo = dict(cfg.get("geography") or {})
    geo["configured"] = True
    geo[key] = not bool(geo.get(key, defaults[key]))
    cfg["geography"] = geo
    await _save(search, cfg)
    await geo_callback(callback)


@router.callback_query(F.data == "cfg:countries")
async def countries_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    _, search = await _first_search(user.id)
    await callback.message.edit_text("🌐 <b>Страны</b>\nМожно выбрать несколько и задать приоритет.", parse_mode="HTML", reply_markup=countries_keyboard(list(all_supported_countries()), search.settings or {}))
    await callback.answer()


@router.callback_query(F.data.startswith("cfg:country:"))
async def country_toggle(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    code = normalize_country(callback.data.split(":", 2)[2])
    if not code:
        return
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    selected = list(cfg.get("target_countries") or [])
    selected.remove(code) if code in selected else selected.append(code)
    cfg["target_countries"] = selected
    geo = dict(cfg.get("geography") or {})
    geo["configured"] = True
    cfg["geography"] = geo
    await _save(search, cfg)
    await countries_callback(callback)


@router.callback_query(F.data.startswith("cfg:cp:"))
async def country_priority_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    code = callback.data.split(":", 2)[2].upper()
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    priorities = dict(cfg.get("country_priorities") or {})
    priorities[code] = (int(priorities.get(code, 50)) + 25) % 125
    cfg["country_priorities"] = priorities
    await _save(search, cfg)
    await countries_callback(callback)


@router.callback_query(F.data == "cfg:reloc")
async def relocation_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    _, search = await _first_search(user.id)
    await callback.message.edit_text("✈️ <b>Relocation / Visa</b>\nany — не фильтровать; prefer — выше; require — обязательно; exclude — исключить.", parse_mode="HTML", reply_markup=relocation_keyboard(search.settings or {}))
    await callback.answer()


@router.callback_query(F.data.startswith("cfg:rel:"))
async def relocation_policy_callback(callback: CallbackQuery) -> None:
    user = await _user_callback(callback)
    key = callback.data.split(":", 2)[2]
    _, search = await _first_search(user.id)
    cfg = search_config(search.settings)
    prefs = dict(cfg.get("relocation_preferences") or {})
    prefs[key] = next_policy(str(prefs.get(key, "any")))
    cfg["relocation_preferences"] = prefs
    await _save(search, cfg)
    await relocation_callback(callback)
