"""Conservative, source-independent employer preference decisions."""
from __future__ import annotations

import re
import unicodedata

from app.knowledge.profile import load_profile

VALUES = {"allow", "warn", "block"}
LEGACY_INDUSTRY_EXCLUSIONS = frozenset({
    "betting", "gambling", "букмек", "букмекер", "казино", "casino",
    "igaming", "crypto casino", "crypto", "web3", "blockchain",
})

_CATEGORY_ALIASES = {
    "betting": "betting",
    "gambling": "betting",
    "bookmaking": "betting",
    "казино": "casino_igaming",
    "casino": "casino_igaming",
    "igaming": "casino_igaming",
    "crypto": "crypto_web3",
    "web3": "crypto_web3",
    "blockchain": "crypto_web3",
    "civilian_state_owned": "civilian_state_owned",
    "russian_military_defense": "russian_military_defense",
    "defense": "russian_military_defense",
    "military": "russian_military_defense",
    "verified_direct_war_tie": "verified_direct_war_tie",
    "russian_government_body": "russian_government_body",
}


def normalize_employer(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().replace("ё", "е")
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _defaults() -> dict:
    return (load_profile().get("search") or {}).get("employer_policy") or {}


def _exact_map(mapping: object) -> dict[str, str]:
    if not isinstance(mapping, dict):
        return {}
    return {normalize_employer(key): str(value).casefold() for key, value in mapping.items()}


def decision(company: str, industry_tags: object, settings: dict | None = None) -> tuple[str, str | None]:
    """Return (allow|warn|block, reason); only structured tags and exact names classify."""
    cfg = settings if isinstance(settings, dict) else {}
    defaults = _defaults()
    overrides = cfg.get("employer_policy_overrides")
    overrides = overrides if isinstance(overrides, dict) else {}
    name = normalize_employer(company)
    manual_employers = _exact_map(overrides.get("employers"))
    # Explicit employer choice is the owner's strongest rule.
    if name and manual_employers.get(name) in VALUES:
        value = manual_employers[name]
        return value, f"решение пользователя для работодателя: {value}"

    tags = industry_tags if isinstance(industry_tags, (list, tuple, set)) else []
    categories = list(dict.fromkeys(
        category for raw in tags
        if isinstance(raw, str)
        for category in [_CATEGORY_ALIASES.get(raw.strip().casefold())]
        if category
    ))
    category_overrides = overrides.get("categories")
    category_overrides = category_overrides if isinstance(category_overrides, dict) else {}
    category_defaults = defaults.get("categories") if isinstance(defaults.get("categories"), dict) else {}
    # A user's explicit category decision also supersedes owner defaults.
    manual_values = [
        str(category_overrides[category]).casefold()
        for category in categories
        if category in category_overrides and str(category_overrides[category]).casefold() in VALUES
    ]
    if "block" in manual_values:
        return "block", "решение пользователя для категории: block"
    if "allow" in manual_values:
        return "allow", "решение пользователя для категории: allow"
    if "warn" in manual_values:
        return "warn", "решение пользователя для категории: warn"

    default_employers = _exact_map(defaults.get("employers"))
    if name and default_employers.get(name) == "block":
        return "block", "работодатель в подтверждённом списке предпочтений владельца"

    choices = []
    for category in categories:
        value = str(category_overrides.get(category, category_defaults.get(category, "allow"))).casefold()
        if value in VALUES:
            choices.append((value, category))
    if "block" in {value for value, _ in choices}:
        value, category = next(pair for pair in choices if pair[0] == "block")
        return value, f"категория {category}: block"
    if "warn" in {value for value, _ in choices}:
        value, category = next(pair for pair in choices if pair[0] == "warn")
        return value, f"категория {category}: нужна ручная проверка"
    return "allow", None


def update_policy(settings: dict, kind: str, value: str, key: str | None = None) -> dict:
    """Return a copy with a user override; kind is category or employer."""
    normalized_value = value.casefold()
    if normalized_value not in VALUES | {"inherit"}:
        raise ValueError("Решение должно быть allow, warn, block или inherit.")
    if kind not in {"category", "employer"}:
        raise ValueError("Тип правила должен быть category или employer.")
    if not key or not key.strip():
        raise ValueError("Укажи категорию или точное имя работодателя.")
    if kind == "category" and key.strip().casefold() not in _defaults().get("categories", {}):
        raise ValueError("Неизвестная категория работодателя.")
    result = dict(settings or {})
    overrides = dict(result.get("employer_policy_overrides") or {})
    field = "categories" if kind == "category" else "employers"
    mapping = dict(overrides.get(field) or {})
    normalized_key = key.strip().casefold() if kind == "category" else key.strip()
    if normalized_value == "inherit":
        mapping.pop(normalized_key, None)
    else:
        mapping[normalized_key] = normalized_value
    overrides[field] = mapping
    result["employer_policy_overrides"] = overrides
    return result
