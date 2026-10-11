from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.search.preferences import POLICY_VALUES, SEARCH_STRATEGIES, search_config, search_strategy


def settings_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧭 Стратегия поиска", callback_data="cfg:strategy")],
        [InlineKeyboardButton(text="🔎 Источники", callback_data="cfg:sources"), InlineKeyboardButton(text="🌍 География", callback_data="cfg:geo")],
        [InlineKeyboardButton(text="✈️ Релокация", callback_data="cfg:reloc")],
    ])


def strategy_keyboard(settings: dict) -> InlineKeyboardMarkup:
    current = search_strategy(settings)
    labels = {
        "career_first": "Career-first",
        "relocation_first": "Relocation-first",
        "balanced": "Balanced",
    }
    rows = [
        [InlineKeyboardButton(
            text=("✅ " if value == current else "▫️ ") + labels[value],
            callback_data=f"cfg:strategy:{value}",
        )]
        for value in SEARCH_STRATEGIES
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Настройки", callback_data="cfg:root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def source_keyboard(source_ids: list[str], settings: dict) -> InlineKeyboardMarkup:
    cfg = search_config(settings)
    disabled = set(cfg.get("disabled_sources") or [])
    priorities = cfg.get("source_priorities") or {}
    rows = []
    for source_id in source_ids:
        rows.append([
            InlineKeyboardButton(text=("✅ " if source_id not in disabled else "❌ ") + source_id, callback_data=f"cfg:src:{source_id}"),
            InlineKeyboardButton(text=f"⭐ {int(priorities.get(source_id, 50))}/100", callback_data=f"cfg:srcp:{source_id}"),
        ])
    rows.append([InlineKeyboardButton(text="⬅️ Настройки", callback_data="cfg:root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def geography_keyboard(settings: dict) -> InlineKeyboardMarkup:
    geo = dict(search_config(settings).get("geography") or {})
    defaults = {"include_current_city": True, "include_other_cities": False, "include_other_countries": True, "worldwide": False}
    def mark(key: str) -> str:
        return "✅" if bool(geo.get(key, defaults[key])) else "❌"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{mark('include_current_city')} Мой город", callback_data="cfg:geo:include_current_city")],
        [InlineKeyboardButton(text=f"{mark('include_other_cities')} Другие города", callback_data="cfg:geo:include_other_cities")],
        [InlineKeyboardButton(text=f"{mark('include_other_countries')} Другие страны", callback_data="cfg:geo:include_other_countries")],
        [InlineKeyboardButton(text=f"{mark('worldwide')} Весь мир", callback_data="cfg:geo:worldwide")],
        [InlineKeyboardButton(text="🌐 Выбрать страны", callback_data="cfg:countries")],
        [InlineKeyboardButton(text="⬅️ Настройки", callback_data="cfg:root")],
    ])


def countries_keyboard(countries: list[tuple[str, str]], settings: dict) -> InlineKeyboardMarkup:
    cfg = search_config(settings)
    selected = {str(x).upper() for x in (cfg.get("target_countries") or [])}
    priorities = cfg.get("country_priorities") or {}
    rows = []
    for code, name in countries:
        rows.append([
            InlineKeyboardButton(text=("✅ " if code in selected else "➕ ") + f"{code} {name}", callback_data=f"cfg:country:{code}"),
            InlineKeyboardButton(text=f"⭐ {int(priorities.get(code, 50))}/100", callback_data=f"cfg:cp:{code}"),
        ])
    rows.append([InlineKeyboardButton(text="⬅️ География", callback_data="cfg:geo")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def relocation_keyboard(settings: dict) -> InlineKeyboardMarkup:
    prefs = search_config(settings).get("relocation_preferences") or {}
    labels = {
        "relocation": "✈️ Relocation",
        "visa_sponsorship": "🛂 Visa sponsorship",
        "work_permit": "📄 Work permit",
        "relocation_package": "📦 Relocation package",
        "immigration_support": "🤝 Immigration support",
    }
    rows = [[InlineKeyboardButton(text=f"{label}: {prefs.get(key, 'any')}", callback_data=f"cfg:rel:{key}")] for key, label in labels.items()]
    rows.append([InlineKeyboardButton(text="⬅️ Настройки", callback_data="cfg:root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def next_policy(value: str) -> str:
    try:
        index = POLICY_VALUES.index(value)
    except ValueError:
        index = 0
    return POLICY_VALUES[(index + 1) % len(POLICY_VALUES)]
