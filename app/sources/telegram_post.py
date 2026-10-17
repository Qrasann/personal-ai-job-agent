"""Conservative metadata from explicit Telegram posting labels."""
from __future__ import annotations

import re
from app.geo.countries import normalize_country

_LABELS = {
    "title": re.compile(r"^(?:position|role|job title|vacancy|вакансия|должность|позиция)\s*:\s*(.+)$", re.I),
    "company": re.compile(r"^(?:company|employer|компания|работодатель)\s*:\s*(.+)$", re.I),
    "location": re.compile(r"^(?:location|country|локация|страна|место работы|город)\s*:\s*(.+)$", re.I),
    "work_mode": re.compile(r"^(?:work mode|work format|формат работы|формат)\s*:\s*(.+)$", re.I),
}
_CITIES = {"Yerevan": ("AM", r"\b(?:yerevan|ереван)\b"),
           "Tbilisi": ("GE", r"\b(?:tbilisi|тбилиси)\b"),
           "Batumi": ("GE", r"\b(?:batumi|батуми)\b")}
_COUNTRIES = {"AM": r"\b(?:armenia|армения|հայաստան)\b", "GE": r"\b(?:georgia|грузия|საქართველო)\b"}
_US_GEORGIA_CITY = re.compile(r"\b(?:atlanta|savannah|augusta|athens|macon|columbus)\s*,\s*georgia\b", re.I)

# Only explicit self-promotion/advertising headers are rejected. A vacancy may
# contain words such as "resume" or "advertising" in its requirements.
_NON_VACANCY_HEADER = re.compile(
    r"^\s*(?:#(?:реклама|advertisement|резюме|opentowork|ищуработу|lookingforwork)(?=\W|$)|"
    r"(?:реклама|резюме(?: кандидата)?|resume|ищу работу|ищу вакансию|"
    r"looking for (?:a )?job|my resume|мой опыт)\s*[:—-])",
    re.I,
)


def explicit_non_vacancy(text: str) -> bool:
    return bool(_NON_VACANCY_HEADER.match(text[:500]))


def post_fields(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    fields = {}
    for line in lines[:20]:
        line = line.lstrip("💼🏢📍🌍🧭 ")
        for key, pattern in _LABELS.items():
            found = pattern.fullmatch(line)
            if found:
                fields.setdefault(key, found[1].strip()[:240])
    candidates = [line for line in lines if not re.fullmatch(r"(?:#[\w]+\s*)+", line)
                  and line.casefold().rstrip(":") not in {"vacancy", "вакансия", "hiring", "we're hiring"}]
    fields["title"] = fields.get("title") or (candidates[0][:240] if candidates else "Telegram vacancy")
    location = fields.get("location", "")
    countries = {code for code, pattern in _COUNTRIES.items() if re.search(pattern, location, re.I)}
    cities = [(city, code) for city, (code, pattern) in _CITIES.items() if re.search(pattern, location, re.I)]
    countries.update(code for _, code in cities)
    if re.search(r"\b(?:USA|United States)\b", location, re.I) or re.search(r"\bUS\b", location):
        countries.add("US")
    if _US_GEORGIA_CITY.search(location):
        # The city disambiguates the US state, while the bare country word
        # would otherwise be read as GE. Preserve conflicting evidence as
        # unknown rather than calling this a Georgian-country vacancy.
        countries.add("US")
    normalized = normalize_country(location)
    if normalized:
        countries.add(normalized)
    fields["country"] = next(iter(countries)) if len(countries) == 1 else None
    fields["city"] = cities[0][0] if len(cities) == 1 and len(countries) == 1 else None
    mode = fields.get("work_mode", "").casefold()
    fields["work_mode"] = {"remote": "remote", "удаленно": "remote", "удалённо": "remote",
                           "hybrid": "hybrid", "гибрид": "hybrid", "onsite": "onsite", "офис": "onsite"}.get(mode)
    if fields["work_mode"] is None and re.search(r"\bhybrid\b", location, re.I):
        fields["work_mode"] = "hybrid"
    elif fields["work_mode"] is None and re.match(r"remote\b", location, re.I):
        fields["work_mode"] = "remote"
    return fields
