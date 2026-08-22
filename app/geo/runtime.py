from app.database import repository as repo
from app.geo.countries import normalize_country
from app.knowledge.profile import load_profile


async def get_current_country() -> str | None:
    value = await repo.get_state("geo:current_country", "")
    if value:
        return normalize_country(value)
    raw = (load_profile().get("geography") or {}).get("current_country")
    return normalize_country(str(raw)) if raw else None


async def set_current_country(value: str) -> str:
    code = normalize_country(value)
    if not code:
        raise ValueError("Неизвестная или пока не настроенная страна")
    await repo.set_state("geo:current_country", code)
    return code


async def get_target_countries() -> list[str]:
    raw = await repo.get_state("geo:target_countries", "")
    if raw:
        return [x for x in raw.split(",") if normalize_country(x)]
    items = (load_profile().get("geography") or {}).get("target_countries") or []
    return [code for item in items if (code := normalize_country(str(item)))]


async def set_target_countries(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        code = normalize_country(value)
        if not code:
            raise ValueError(f"Неизвестная или пока не настроенная страна: {value}")
        if code not in normalized:
            normalized.append(code)
    await repo.set_state("geo:target_countries", ",".join(normalized))
    return normalized
