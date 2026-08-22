from __future__ import annotations

ALLOWED_EXPERIENCE_TYPES: tuple[str, ...] = (
    "commercial",
    "lab",
    "learning",
    "unknown",
)

_ALIASES: dict[str, str] = {
    "commercial": "commercial",
    "work": "commercial",
    "production": "commercial",
    "prod": "commercial",
    "коммерческий": "commercial",
    "коммерческое": "commercial",
    "работа": "commercial",
    "lab": "lab",
    "labs": "lab",
    "laboratory": "lab",
    "project": "lab",
    "personal": "lab",
    "лаба": "lab",
    "лаборатория": "lab",
    "проект": "lab",
    "learning": "learning",
    "study": "learning",
    "studying": "learning",
    "training": "learning",
    "учеба": "learning",
    "учёба": "learning",
    "обучение": "learning",
    "изучаю": "learning",
    "unknown": "unknown",
    "unspecified": "unknown",
    "неизвестно": "unknown",
    "неуказано": "unknown",
}


def normalize_experience_type(value: str | None) -> str | None:
    if value is None:
        return None
    key = " ".join(str(value).strip().casefold().split())
    return _ALIASES.get(key)


def experience_type_label(value: str | None) -> str:
    normalized = normalize_experience_type(value) or "unknown"
    return f"[{normalized}]"


def is_commercial_type(value: str | None) -> bool:
    return normalize_experience_type(value) == "commercial"
