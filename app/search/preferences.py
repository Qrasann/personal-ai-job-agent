from __future__ import annotations

import re
from typing import Any

from app.domain.jobs import NormalizedJob
from app.domain.support_evidence import SUPPORT_KEYS, support_evidence

POLICY_VALUES = ("any", "prefer", "require", "exclude")
SEARCH_STRATEGIES = ("career_first", "relocation_first", "balanced")
DEFAULT_PRIORITY = 50
REMOTE_WORK_PRIORITY_BONUS = 30


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
    cfg.setdefault("search_strategy", "balanced")
    cfg.setdefault("relocation_queries", [])
    return cfg


def search_strategy(settings: dict | None) -> str:
    value = str(search_config(settings).get("search_strategy") or "balanced").casefold()
    return value if value in SEARCH_STRATEGIES else "balanced"


def discovery_queries(settings: dict | None, fallback: str = "") -> list[str]:
    """Return a stable, deduplicated query list for the selected strategy.

    Existing ``queries`` remain the career track for backwards compatibility.
    A relocation-only track falls back to them until the user explicitly adds
    broader relocation roles, so changing strategy can never disable discovery.
    """
    cfg = search_config(settings)
    career = [str(item).strip() for item in _list(cfg.get("queries")) if str(item).strip()]
    if not career and fallback.strip():
        career = [fallback.strip()]
    relocation = [
        str(item).strip()
        for item in _list(cfg.get("relocation_queries"))
        if str(item).strip()
    ]
    strategy = search_strategy(cfg)
    if strategy == "career_first":
        selected = career
    elif strategy == "relocation_first":
        selected = relocation or career
    else:
        selected = career + relocation
    return list(dict.fromkeys(selected))


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
    if job.source == "jobbank":
        # Explicit adapter evidence outranks incidental permit/LMIA terminology.
        support = (job.raw or {}).get("support_signals") or {}
        return {key: support.get(key) is True for key in SUPPORT_KEYS}
    # Metadata key names (including null/false values) are not posting evidence.
    evidence = support_evidence("\n".join((job.title or "", job.description or "")))
    for key in ("relocation", "visa_sponsorship"):
        value = getattr(job, key)
        if value is not None and evidence[key] is not False:
            evidence[key] = value
    return {key: evidence[key] is True for key in SUPPORT_KEYS}


def _is_remote_job(job: NormalizedJob) -> bool:
    mode = _norm_text(getattr(job, "work_mode", None))
    scope = _norm_text(getattr(job, "remote_scope", None))
    non_remote = r"\b(?:onsite|on-site|office only|no remote|not remote|не удаленн\w*|не дистанционн\w*)\b"
    if re.search(non_remote, mode):
        return False
    remote_mode = bool(
        re.search(
            r"\bremote\b|удаленн\w*|дистанционн\w*|telework|work from home|home office|\bwfh\b",
            mode,
        )
    )
    # A populated remote_scope is itself a remote-work signal. Values such as
    # "unspecified" describe unknown geographic eligibility, not worldwide
    # eligibility; they can still be prioritized for the user to inspect.
    remote_scope = bool(scope and scope not in {"unknown", "none", "n/a"})
    return remote_mode or remote_scope


def _policy(settings: dict | None, key: str) -> str:
    value = str(_dict(search_config(settings).get("relocation_preferences")).get(key, "any")).casefold()
    return value if value in POLICY_VALUES else "any"


def relocation_first_allows(job: NormalizedJob, settings: dict | None, *, current_country: str | None = None) -> bool:
    """Hide known domestic onsite roles from relocation lists and discovery."""
    if search_strategy(settings) != "relocation_first":
        return True
    home_country = _norm_code(current_country)
    return not (
        home_country
        and _norm_code(job.country) == home_country
        and not _is_remote_job(job)
        and search_config(settings).get("domestic_relocation") is not True
    )


def vacancy_allowed(job: NormalizedJob, settings: dict | None, *, current_country: str | None = None) -> bool:
    cfg = search_config(settings)
    job_country = _norm_code(job.country)
    home_country = _norm_code(current_country)
    # Relocation-first must not present an ordinary onsite job in the
    # candidate's current country as a relocation lead. Explicit remote roles
    # remain discoverable, and users can opt into domestic moves separately.
    if not relocation_first_allows(job, cfg, current_country=current_country):
        return False

    geo = _dict(cfg.get("geography"))
    if geo.get("configured"):
        worldwide = bool(geo.get("worldwide", False))
        current_city_enabled = bool(geo.get("include_current_city", True))
        other_cities = bool(geo.get("include_other_cities", False))
        other_countries = bool(geo.get("include_other_countries", True))
        current_city = _norm_text(str(cfg.get("local_city") or ""))
        selected_cities = {_norm_text(str(x)) for x in _list(cfg.get("selected_cities")) if str(x).strip()}
        selected_countries = {_norm_code(str(x)) for x in _list(cfg.get("target_countries")) if str(x).strip()}
        job_city = _norm_text(job.city)

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
    strategy = search_strategy(cfg)
    if _is_remote_job(job):
        score += REMOTE_WORK_PRIORITY_BONUS
    for key, present in _signals(job).items():
        if present:
            policy = _policy(cfg, key)
            if policy == "prefer":
                score += 20
            elif policy == "require":
                score += 30
            elif strategy == "relocation_first":
                score += 15
            elif strategy == "balanced":
                score += 5
    return score
