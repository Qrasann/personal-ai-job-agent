from functools import lru_cache
from pathlib import Path
import yaml

COUNTRIES_PATH = Path("data/countries.yaml")


@lru_cache(maxsize=1)
def load_country_catalog(path: Path | None = None) -> dict:
    with open(path or COUNTRIES_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def normalize_country(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    catalog = load_country_catalog().get("countries", {})
    upper = raw.upper()
    if upper in catalog:
        return upper
    lowered = raw.casefold()
    for code, cfg in catalog.items():
        names = [cfg.get("name", ""), *(cfg.get("aliases") or [])]
        if any(str(name).casefold() == lowered for name in names):
            return code
    return None


def country_config(code: str) -> dict | None:
    normalized = normalize_country(code)
    if not normalized:
        return None
    cfg = dict(load_country_catalog().get("countries", {}).get(normalized, {}))
    cfg["code"] = normalized
    return cfg


def local_sources(code: str) -> list[dict]:
    cfg = country_config(code)
    if not cfg:
        return []
    return list(cfg.get("local_sources") or [])


def all_supported_countries() -> list[tuple[str, str]]:
    rows = []
    for code, cfg in load_country_catalog().get("countries", {}).items():
        rows.append((code, cfg.get("name", code)))
    return sorted(rows)
