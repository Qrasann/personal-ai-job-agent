import re
from bs4 import BeautifulSoup
from app.knowledge.profile import load_profile


def clean_html(text: str | None) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def _salary(vacancy: dict) -> tuple[int | None, int | None, str | None, bool | None]:
    salary = vacancy.get("salary_range") or vacancy.get("salary") or {}
    return salary.get("from"), salary.get("to"), salary.get("currency"), salary.get("gross")


def score_vacancy(vacancy: dict) -> tuple[int, str]:
    profile = load_profile()
    search = profile["search"]
    title = vacancy.get("name", "")
    description = clean_html(vacancy.get("description"))
    text = f"{title} {description}".lower()

    reasons: list[str] = []
    score = 45

    for term in search.get("exclude_terms", []):
        if term.lower() in text:
            return 0, f"Исключено правилом: {term}"

    title_low = title.lower()
    if "devops" in title_low:
        score += 20
        reasons.append("DevOps в названии")
    elif "infrastructure" in title_low or "linux" in title_low:
        score += 12
        reasons.append("подходящая Infrastructure/Linux роль")
    elif "system administrator" in title_low or "системн" in title_low:
        score += 5
        reasons.append("смежная системная роль")

    strong_hits = [t for t in search.get("strong_terms", []) if t.lower() in text]
    preferred_hits = [t for t in search.get("preferred_terms", []) if t.lower() in text]
    score += min(20, len(set(strong_hits)) * 4)
    score += min(10, len(set(preferred_hits)) * 2)
    if strong_hits:
        reasons.append("совпадения: " + ", ".join(sorted(set(strong_hits))[:6]))

    exp = (vacancy.get("experience") or {}).get("id", "")
    if exp in {"noExperience", "between1And3"}:
        score += 8
        reasons.append("подходящий уровень опыта")
    elif exp in {"between3And6", "moreThan6"}:
        score -= 18
        reasons.append("требуется более высокий опыт")

    work_format = " ".join((x.get("name", "") + " " + x.get("id", "")) for x in (vacancy.get("work_format") or []))
    schedule = " ".join(str((vacancy.get("schedule") or {}).get(k, "")) for k in ("id", "name"))
    combined = (work_format + " " + schedule).lower()
    if any(x in combined for x in ["remote", "удален", "hybrid", "гибрид"]):
        score += 7
        reasons.append("remote/hybrid")

    salary_from, salary_to, currency, gross = _salary(vacancy)
    minimum = int(search.get("minimum_salary_net_rub", 0))
    if currency == "RUR" and salary_from:
        approx_net_from = int(salary_from * 0.87) if gross else int(salary_from)
        if approx_net_from >= minimum:
            score += 10
            reasons.append("зарплата не ниже минимума")
        elif approx_net_from < minimum * 0.8:
            score -= 15
            reasons.append("зарплата заметно ниже минимума")

    if re.search(r"\b(senior|lead|principal|architect)\b", text):
        score -= 20
        reasons.append("senior/lead признаки")

    return max(0, min(100, score)), "; ".join(reasons) or "базовый матч"
