from __future__ import annotations

import re
from typing import Any

from app.domain.jobs import NormalizedJob

POLICY_VALUES = ("any", "prefer", "require", "exclude")
DEFAULT_PRIORITY = 50


def _dict(value: Any) -> dict:
    return dict(value) if isinstance(value, dict) else {}


def _list(value: Any) -> list:
    return list(value) if isinstance(value, (list, tuple)) else []


def _norm_text(value: str | None) -> str:
    return " ".join((value or "").casefold().replace("ё", "е").split())


def _norm_code(value: str | None) -> str:
    return (value or "").strip().upper()


def search_config(settings: dict | None) -> dict:
    cfg = dict(settings or {})
    cfg.setdefault("enabled_sources", [])
    cfg.setdefault("disabled_sources", [])
    cfg.setdefault("source_priorities", {})
    cfg.setdefault("target_countries", [])
    cfg.setdefault("country_priorities", {})
    cfg.setdefault("city_priorities", {})
    cfg.setdefault("selected_cities", [])
    cfg.setdefault("geography", {})
    cfg.setdefault("relocation_preferences", {})
    return cfg


def source_enabled(settings: dict | None, source_id: str) -> bool:
    cfg = search_config(settings)
    enabled = {str(x) for x in _list(cfg.get("enabled_sources"))}
    disabled = {str(x) for x in _list(cfg.get("disabled_sources"))}
    if source_id in disabled:
        return False
    return not enabled or source_id in enabled


def _priority(mapping: dict, key: str) -> int:
    try:
        return max(0, min(100, int(mapping.get(key, DEFAULT_PRIORITY))))
    except (TypeError, ValueError):
        return DEFAULT_PRIORITY


def source_priority(settings: dict | None, source_id: str) -> int:
    return _priority(_dict(search_config(settings).get("source_priorities")), source_id)


def country_priority(settings: dict | None, country: str | None) -> int:
    return _priority(_dict(search_config(settings).get("country_priorities")), _norm_code(country))


def city_priority(settings: dict | None, city: str | None) -> int:
    raw = {_norm_text(str(k)): v for k, v in _dict(search_config(settings).get("city_priorities")).items()}
    return _priority(raw, _norm_text(city))


def _signals(job: NormalizedJob) -> dict[str, bool]:
    text = _norm_text(" ".join([job.title or "", job.description or "", str(job.raw or "")]))
    return {
        "relocation": job.relocation is True or bool(re.search(r"\brelocat(?:e|ion)\b|релокац|переезд", text)),
        "visa_sponsorship": job.visa_sponsorship is True or bool(re.search(r"visa sponsorship|sponsor(?:ing)? visa|визов|рабоч(?:ая|ую) виз", text)),
        "work_permit": bool(re.search(r"work permit|right to work|разрешени.{0,12}на работу", text)),
        "relocation_package": bool(re.search(r"relocation package|relocation assistance|релокационн.{0,12}пакет|оплачива.{0,12}переезд", text)),
        "immigration_support": bool(re.search(r"immigration support|immigration assistance|visa support|помощ.{0,12}(?:виз|иммиграц|переезд)", text)),
    }


def _policy(settings: dict | None, key: str) -> str:
    value = str(_dict(search_config(settings).get("relocation_preferences")).get(key, "any")).casefold()
    return value if value in POLICY_VALUES else "any"


def vacancy_allowed(job: NormalizedJob, settings: dict | None, *, current_country: str | None = None) -> bool:
    cfg = search_config(settings)
    geo = _dict(cfg.get("geography"))
    if geo.get("configured"):
        worldwide = bool(geo.get("worldwide", False))
        current_city_enabled = bool(geo.get("include_current_city", True))
        other_cities = bool(geo.get("include_other_cities", False))
        other_countries = bool(geo.get("include_other_countries", True))
        current_city = _norm_text(str(cfg.get("local_city") or ""))
        selected_cities = {_norm_text(str(x)) for x in _list(cfg.get("selected_cities")) if str(x).strip()}
        selected_countries = {_norm_code(str(x)) for x in _list(cfg.get("target_countries")) if str(x).strip()}
        job_country = _norm_code(job.country)
        job_city = _norm_text(job.city)
        home_country = _norm_code(current_country)

        if not worldwide and job_country:
            if home_country and job_country == home_country:
                if current_city and job_city == current_city:
                    if not current_city_enabled:
                        return False
                elif job_city and job_city in selected_cities:
                    pass
                elif job_city and not other_cities:
                    return False
            elif job_country in selected_countries:
                pass
            elif not other_countries:
                return False

    signals = _signals(job)
    for key in signals:
        policy = _policy(cfg, key)
        if policy == "require" and not signals[key]:
            return False
        if policy == "exclude" and signals[key]:
            return False
    return True


def job_priority(job: NormalizedJob, settings: dict | None, *, current_country: str | None = None) -> int:
    cfg = search_config(settings)
    score = source_priority(cfg, job.source) + country_priority(cfg, job.country) + city_priority(cfg, job.city)
    if _norm_code(job.country) in {_norm_code(str(x)) for x in _list(cfg.get("target_countries"))}:
        score += 20
    local_city = _norm_text(str(cfg.get("local_city") or ""))
    if local_city and _norm_text(job.city) == local_city:
        score += 15
    for key, present in _signals(job).items():
        if present:
            policy = _policy(cfg, key)
            if policy == "prefer":
                score += 20
            elif policy == "require":
                score += 30
    return score
