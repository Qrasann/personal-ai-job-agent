from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from urllib.parse import urlsplit

from app.domain.job_text import clean_html_text, extract_experience, format_salary, repair_mojibake
from app.domain.remote_evidence import remote_residence_requirement, restricted_remote_scope
from app.domain.support_evidence import existing_work_authorization_required, support_evidence
from app.domain.vacancy_availability import vacancy_availability_lines
from app.matching.engine import non_actionable_role_reason


def _clip(value: str, limit: int) -> str:
    text = value or ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _safe_http_url(value: object, *, max_length: int = 600) -> str | None:
    """Return a navigable HTTP(S) URL without credentials or malformed authority."""
    if not isinstance(value, str):
        return None
    url = value.strip()
    if not url or len(url) > max_length or any(ord(char) < 33 or ord(char) == 127 for char in url):
        return None
    try:
        parsed = urlsplit(url)
        # Accessing .port validates malformed/out-of-range port syntax.
        parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme.casefold() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        return None
    return url


def _escape_clipped(value: str, limit: int) -> str:
    """Bound encoded text without cutting an HTML entity."""
    if len(html.escape(value)) <= limit:
        return html.escape(value)
    low, high = 0, len(value)
    while low < high:
        middle = (low + high + 1) // 2
        if len(html.escape(value[:middle] + "…")) <= limit:
            low = middle
        else:
            high = middle - 1
    return html.escape(value[:low] + "…")


def _escape_with_utf16_limit(value: str, units: int) -> str:
    """Escape text without exceeding Telegram's UTF-16 entity length budget."""
    value = value or ""
    if units <= 0:
        return ""

    def length(text: str) -> int:
        return len(text.encode("utf-16-le")) // 2

    if length(html.escape(value)) <= units:
        return html.escape(value)
    low, high = 0, len(value)
    while low < high:
        middle = (low + high + 1) // 2
        candidate = html.escape(value[:middle] + "…")
        if length(candidate) <= units:
            low = middle
        else:
            high = middle - 1
    return html.escape(value[:low] + "…") if low else ""


def _location(job, details: dict) -> str:
    return str(details.get("city") or job.city or job.country or "не указана")


def _experience(job, details: dict) -> str:
    direct = clean_html_text(str(details.get("experience") or ""))
    if direct:
        return direct
    return extract_experience(str(details.get("description") or job.description or "")) or "не указан"


def _work_mode(job, details: dict) -> str:
    return clean_html_text(str(details.get("work_mode") or job.work_mode or "")) or "не указан"


def _remote_scope(job, details: dict) -> str:
    scope = clean_html_text(
        str(details.get("remote_scope") or getattr(job, "remote_scope", None) or "")
    ).strip()
    work_mode = _work_mode(job, details).casefold()
    is_remote = any(value in work_mode for value in ("remote", "удалён", "удален"))
    normalized_scope = scope.casefold()
    unknown_scope = normalized_scope in {"", "unknown", "unspecified", "none", "n/a"}
    if not is_remote and unknown_scope:
        return ""
    requirement = remote_residence_requirement(str(details.get("description") or job.description or ""))
    if requirement:
        # Re-evaluate the complete text for old cached worldwide rows too.
        prefix = ""
        if restricted_remote_scope(scope) and not requirement.casefold().startswith(scope.rstrip("…").casefold()):
            prefix = _clip(scope, 45) + "; "
        return f"{prefix}в описании: {_clip(requirement, 100)}; найм в вашей стране нужно подтвердить"
    if normalized_scope in {"worldwide", "global", "anywhere"}:
        return "по всему миру указано источником; возможность найма в вашей стране нужно подтвердить"
    if unknown_scope:
        return "страны найма не указаны источником; проверьте доступность из вашей страны"
    return f"{scope} указано источником; возможность найма в вашей стране нужно подтвердить"


def _timezone_restrictions(details: dict) -> str:
    values = details.get("timezone_restrictions")
    if not isinstance(values, list):
        return ""
    known: list[str] = []
    for value in values[:32]:
        if not isinstance(value, str):
            continue
        text = " ".join(clean_html_text(value).split())
        if not text or text.casefold() in {"unknown", "unspecified", "none", "n/a"}:
            continue
        text = _clip(text, 64)
        if text not in known:
            known.append(text)
    return _clip(", ".join(known), 220)


def _salary(job, details: dict, fallback_salary_text: str = "") -> str:
    # The search-card text can contain a fuller salary range than the vacancy
    # page itself, so let format_salary compare both sources. Put the saved
    # search-card text first because salary_fragment returns the first credible
    # currency-bearing amount.
    salary_text = " ".join(
        part
        for part in (
            str(fallback_salary_text or ""),
            str(details.get("salary_text") or ""),
        )
        if part
    )
    formatted = format_salary(
        details.get("salary_from") if details.get("salary_from") is not None else job.salary_from,
        details.get("salary_to") if details.get("salary_to") is not None else job.salary_to,
        details.get("salary_currency") or job.salary_currency,
        fallback_text=salary_text,
        period=details.get("salary_period") or getattr(job, "salary_period", None),
    )
    if formatted != "не указана":
        return formatted
    evidence = details.get("source_salary_text")
    if isinstance(evidence, str):
        text = " ".join(clean_html_text(evidence[:2000]).split())
        if text:
            return "по источнику: " + _clip(text, 240)
    return formatted


def _published(value: str) -> str:
    text = clean_html_text(value)
    if not text:
        return ""
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is not None and parsed.utcoffset() is not None:
        return parsed.astimezone(UTC).strftime("%d.%m.%Y %H:%M UTC")
    if "T" not in text and " " not in text:
        return parsed.strftime("%d.%m.%Y")
    return parsed.strftime("%d.%m.%Y %H:%M") + " (часовой пояс не указан)"


def _mobility_evidence_lines(job, description: str) -> list[str]:
    evidence = support_evidence("\n".join((str(getattr(job, "title", "") or ""), description)))
    for key in ("visa_sponsorship", "relocation"):
        stored = getattr(job, key, None)
        if stored is not None and evidence[key] is not False:
            evidence[key] = stored

    authorization_required = existing_work_authorization_required(description)
    country = str(getattr(job, "country", "") or "").upper()
    has_evidence = authorization_required or any(value is not None for value in evidence.values())
    if country in {"RU", "RUSSIA", "РОССИЯ"} and not has_evidence:
        return []

    def label(value: bool | None, *, offered: str, refused: str) -> str:
        if value is True:
            return offered
        if value is False:
            return refused
        return "не подтверждено вакансией"

    return [
        "",
        "🧭 <b>Право на работу и переезд</b>",
        "🛂 Visa sponsorship: " + label(
            evidence["visa_sponsorship"],
            offered="явно предлагается",
            refused="явно не предоставляется",
        ),
        "📦 Помощь с переездом: " + label(
            evidence["relocation"],
            offered="явно предлагается",
            refused="явно не предоставляется",
        ),
        "📄 Помощь с разрешением на работу: " + label(
            evidence["work_permit"],
            offered="явно предлагается",
            refused="явно не предоставляется",
        ),
        (
            "⚖️ Предварительное право на работу: явно требуется"
            if authorization_required
            else "⚖️ Предварительное право на работу: явного требования не найдено"
        ),
        "Эти строки передают текст вакансии и не подтверждают личную юридическую eligibility.",
    ]


def _relocation_evidence_lines(evidence: dict) -> list[str]:
    fields = evidence.get("fields") if isinstance(evidence, dict) else None
    if not isinstance(fields, dict):
        return []
    labels = {
        "work_country": "Страна работы по источнику",
        "citizenship_or_residence_restriction": "Ограничение гражданства/проживания",
        "existing_work_authorization_required": "Предварительное право на работу",
        "visa_sponsorship": "Visa sponsorship",
        "relocation_assistance": "Помощь с релокацией",
        "housing_provided": "Обеспечение жильём",
        "language_requirement": "Языковое требование",
        "start_timing": "Текст о сроках выхода",
    }
    present = [(key, fields.get(key)) for key in labels if isinstance(fields.get(key), dict)]
    if not present:
        return []
    captured = str(evidence.get("captured_at") or "")[:25]
    lines = ["", "🔎 <b>Условия с provenance источника</b>"]
    for key, item in present:
        status = item.get("status")
        value = item.get("value")
        excerpt = str(item.get("excerpt") or "").strip()
        if status == "unknown":
            if item.get("confidence") in {"conflicting_text", "ambiguous_text"}:
                detail = (
                    "противоречивые утверждения в источнике"
                    if item.get("confidence") == "conflicting_text"
                    else "неоднозначная формулировка источника"
                )
                if excerpt:
                    detail += " — “" + html.escape(excerpt[:100]) + "”"
            else:
                detail = "неизвестно по доступному тексту"
        elif key == "work_country":
            detail = html.escape(str(value or "неизвестно")[:100]) + " (сообщено источником)"
            if excerpt and excerpt != str(value or ""):
                detail += " — “" + html.escape(excerpt[:100]) + "”"
        elif key in {"visa_sponsorship", "relocation_assistance", "existing_work_authorization_required"}:
            detail = "да" if value is True else "нет" if value is False else "неизвестно"
        elif key == "housing_provided":
            detail = "предоставляется" if value is True else "явно не предоставляется" if value is False else "неизвестно"
            if excerpt:
                detail += " — “" + html.escape(excerpt[:100]) + "”"
        elif key == "language_requirement":
            interpretation = item.get("interpretation") if isinstance(item.get("interpretation"), dict) else {}
            requirements = interpretation.get("requirements")
            if isinstance(requirements, list) and requirements:
                parts = []
                for requirement_item in requirements[:8]:
                    if not isinstance(requirement_item, dict):
                        continue
                    requirement = str(requirement_item.get("requirement") or "unspecified")
                    name = html.escape(str(requirement_item.get("language") or "язык не определён"))
                    status_text = {
                        "required": "требуется", "preferred": "предпочтительно",
                        "unspecified": "условие не уточнено", "conflicting": "противоречивые условия",
                    }.get(requirement, "условие не уточнено")
                    level = str(requirement_item.get("cefr") or "")
                    if level:
                        status_text += " · CEFR " + html.escape(level)
                    parts.append(name + ": " + status_text)
                detail = "; ".join(parts) or "условие не уточнено"
            else:
                detail = "язык не определён · условие не уточнено"
            if excerpt:
                detail += " — “" + html.escape(excerpt[:100]) + "”"
        elif key == "citizenship_or_residence_restriction":
            interpretation = item.get("interpretation") if isinstance(item.get("interpretation"), dict) else {}
            scope = str(interpretation.get("scope") or "unspecified")
            detail = {
                "citizenship": "ограничение по гражданству (текст источника)",
                "residence": "ограничение по месту проживания (текст источника)",
                "citizenship_and_residence": "текст упоминает гражданство и проживание",
                "unspecified": "требует ручной проверки",
            }.get(scope, "требует ручной проверки")
            if excerpt:
                detail += " — “" + html.escape(excerpt[:100]) + "”"
        elif key == "start_timing":
            interpretation = item.get("interpretation") if isinstance(item.get("interpretation"), dict) else {}
            kind = str(interpretation.get("kind") or "observed_text")
            detail = {
                "immediate": "вакансия говорит о немедленном старте",
                "relative_window": "вакансия указывает относительный срок",
                "stated_date": "вакансия указывает дату",
                "notice_period": "указан notice period",
                "negotiable": "срок назван договорным",
                "observed_text": "фрагмент для проверки",
            }.get(kind, "фрагмент для проверки")
            if excerpt:
                detail += " — “" + html.escape(excerpt[:100]) + "”"
        else:
            detail = "фрагмент для проверки: “" + html.escape(excerpt[:100]) + "”"
        if key in {"citizenship_or_residence_restriction", "visa_sponsorship", "relocation_assistance", "existing_work_authorization_required"} and excerpt:
            detail += " — “" + html.escape(excerpt[:100]) + "”"
        source_id_text = str(item.get("source_id") or "unknown")[:40]
        source_url = _safe_http_url(item.get("source_url"))
        source_id = (
            f'<a href="{html.escape(source_url, quote=True)}">{html.escape(source_id_text)}</a>'
            if source_url else html.escape(source_id_text)
        )
        item_date = html.escape(str(item.get("captured_at") or captured)[:25])
        confidence = html.escape(str(item.get("confidence") or "unknown")[:24])
        lines.append(
            f"• {html.escape(labels[key])}: {detail} "
            f"<i>({source_id}; {item_date}; {confidence})</i>"
        )
    return lines


def relocation_followup_lines(evidence: dict) -> list[str]:
    """Actionable questions from missing source evidence, without eligibility claims."""
    fields = evidence.get("fields") if isinstance(evidence, dict) else None
    if not isinstance(fields, dict):
        return []
    topics = (
        ("work_country", "страну фактической работы"),
        ("existing_work_authorization_required", "требуется ли действующее право на работу"),
        ("visa_sponsorship", "доступен ли visa sponsorship"),
        ("citizenship_or_residence_restriction", "страны гражданства и проживания для найма"),
        ("relocation_assistance", "помощь с переездом"),
        ("housing_provided", "предоставление жилья"),
        ("language_requirement", "требования к языку"),
        ("start_timing", "срок выхода"),
    )
    missing = [
        label for key, label in topics
        if isinstance(fields.get(key), dict) and fields[key].get("status") == "unknown"
    ]
    if not missing:
        return []
    suffix = f"; и ещё {len(missing) - 3} условий" if len(missing) > 3 else ""
    return ["", "📋 Перед откликом уточни у работодателя: " + "; ".join(missing[:3]) + suffix + "."]


def render_queue_card(
    match,
    job,
    *,
    header: str,
    lane: str,
    position: int,
    total: int,
) -> str:
    stale_good_reason = non_actionable_role_reason(job) if "good" in lane.casefold() else None
    if stale_good_reason:
        lane = "⚠️ Требует повторной проверки"
    title = _clip(repair_mojibake(str(getattr(job, "title", "") or "")), 120)
    company = _clip(repair_mojibake(str(getattr(job, "company", "") or "")), 100)
    salary = format_salary(
        getattr(job, "salary_from", None),
        getattr(job, "salary_to", None),
        getattr(job, "salary_currency", None),
        period=getattr(job, "salary_period", None),
    )

    location = repair_mojibake(
        str(getattr(job, "city", None) or getattr(job, "country", None) or "не указана")
    )
    work_mode = repair_mojibake(str(getattr(job, "work_mode", None) or "не указан"))

    description = clean_html_text(str(getattr(job, "description", "") or ""))
    experience = extract_experience(description) or "не указан"
    remote_scope = clean_html_text(str(getattr(job, "remote_scope", "") or ""))
    published = _published(str(getattr(job, "published_at", "") or "")) or "не указана"
    title_and_description = f"{title}\n{description}".casefold()
    unpaid = any(token in title_and_description for token in (
        "volunteer", "voluntary", "unpaid", "волонтёр", "волонтер", "неоплачиваем",
    ))
    paid = "нет — явно волонтёрская/неоплачиваемая" if unpaid else (
        "зарплата раскрыта" if salary != "не указана" else "не подтверждено источником"
    )
    applicants = getattr(job, "applicant_count", None)
    applicant_text = (
        str(applicants)
        if isinstance(applicants, int) and not isinstance(applicants, bool) and applicants >= 0
        else "Нет открытых данных"
    )

    lines = [
        f"<b>{html.escape(header)} · {html.escape(lane)} · {position} из {total}</b>",
        f"<b>{html.escape(title)}</b> — {html.escape(company or 'Компания не указана')}",
        f"📍 {html.escape(location)} · 🏠 {html.escape(work_mode)}",
        f"🌍 Найм: {html.escape(remote_scope or 'география найма не подтверждена')}",
        f"💰 {html.escape(salary)} · Оплачиваемость: {html.escape(paid)}",
        f"🕒 Опыт: {html.escape(experience)} · 📅 {html.escape(published)}",
        f"👥 Отклики: {html.escape(applicant_text)}",
        (
            "🎯 Сохранённая оценка может быть устаревшей; актуальные правила исключают эту роль."
            if stale_good_reason else f"🎯 Match: <b>{getattr(match, 'total_score', 0)}/100</b>"
        ),
    ]

    reason = _concise_match_reason(match)
    if reason:
        lines.append(f"💡 {html.escape(reason)}")
    if stale_good_reason:
        lines.append(f"🔎 Причина проверки: {html.escape(stale_good_reason)}")
    lines.append("🛂 Иностранный найм: только по подтверждённым условиям работодателя; неизвестное не является разрешением.")
    return "\n".join(lines)


def _job_card_values(payload: dict) -> dict:
    job = payload["job"]
    details = payload.get("details") or {}
    description = clean_html_text(str(details.get("description") or job.description or ""))
    return {
        "job": job,
        "match": payload["match"],
        "details": details,
        "description": description,
        "title": _clip(repair_mojibake(str(details.get("title") or job.title or "")), 140),
        "company": _clip(repair_mojibake(str(details.get("company") or job.company or "")), 120),
        "salary": _salary(job, details, str(payload.get("fallback_salary_text") or "")),
        "experience": _experience(job, details),
        "location": _clip(_location(job, details), 160),
        "work_mode": _clip(_work_mode(job, details), 140),
        "remote_scope": _clip(_remote_scope(job, details), 220),
        "published": _published(str(details.get("published_at") or job.published_at or "")),
        "source": str(payload.get("source") or "unknown").upper(),
    }


def _applicant_count_lines(payload: dict, details: dict) -> list[str]:
    value = details.get("applicant_count")
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        return ["👥 Отклики: <b>Нет открытых данных</b>", "Просмотры и другие счётчики не считаются откликами."]
    source = str(details.get("applicant_count_source") or payload.get("source") or "источник")
    safe_source_url = _safe_http_url(source)
    source_display = (
        f'<a href="{html.escape(safe_source_url, quote=True)}">официальная страница</a>'
        if safe_source_url else html.escape(_clip(source, 120))
    )
    observed = str(details.get("applicant_count_observed_at") or payload.get("source_observed_at") or "")
    suffix = f" · проверено {_published(observed)}" if observed else ""
    return [f"👥 Подтверждённых откликов: <b>{value}</b>", f"Источник: {source_display}{html.escape(suffix)}"]


def _concise_match_reason(match) -> str:
    raw = repair_mojibake(str(getattr(match, "reason", "") or ""))
    technical_prefixes = ("режим ", "техника ", "география ", "зарплата ", "релокация ")
    useful = [
        part.strip() for part in raw.split(";")
        if part.strip() and not part.strip().casefold().startswith(technical_prefixes)
    ]
    return _clip("; ".join(useful[:2]), 240)


def render_job_summary(payload: dict) -> str:
    value = _job_card_values(payload)
    match = value["match"]
    reason = _concise_match_reason(match)
    lines = [
        f"🔥 <b>#{value['job'].id} · {html.escape(value['title'])}</b>",
        html.escape(value["company"] or "Компания не указана"),
        f"📍 {html.escape(value['location'])} · 🏠 {html.escape(value['work_mode'])}",
        f"🌍 Найм: {html.escape(value['remote_scope'] or 'география найма не указана')}",
        f"💰 {html.escape(value['salary'])}",
        f"🕒 Опыт: {html.escape(value['experience'])}",
        f"📅 {html.escape(value['published'] or 'дата не указана')}",
        f"🎯 Match: <b>{getattr(match, 'total_score', 0)}/100</b>",
    ]
    if reason:
        lines.append("💡 " + html.escape(reason))
    lines.extend(_applicant_count_lines(payload, value["details"])[:1])
    lines.append("Выбери раздел ниже — технические детали не занимают основной экран.")
    return "\n".join(lines)


def render_job_section(payload: dict, section: str) -> str:
    value = _job_card_values(payload)
    job, match, details = value["job"], value["match"], value["details"]
    heading = f"<b>#{job.id} · {html.escape(value['title'])}</b>"
    if section == "req":
        lines = [heading, "📌 <b>Требования</b>", f"Опыт: {html.escape(value['experience'])}"]
        applicant_location = clean_html_text(str(details.get("applicant_location") or ""))
        lines.append("География кандидата: " + html.escape(applicant_location or value["remote_scope"] or "не указана"))
        lines.append("Совпадающие и недостающие навыки: кнопка «Сравнить с профилем» на краткой карточке.")
        return "\n".join(lines)
    if section == "desc":
        description = _escape_with_utf16_limit(value["description"], 3200)
        return "\n".join([heading, "📝 <b>Описание</b>", description or "Описание не предоставлено источником."])
    if section == "terms":
        lines = [
            heading, "💼 <b>Условия найма</b>",
            f"💰 {html.escape(value['salary'])}",
            f"📍 {html.escape(value['location'])} · 🏠 {html.escape(value['work_mode'])}",
            f"🌍 Remote scope: {html.escape(value['remote_scope'] or 'не подтверждён')}",
        ]
        lines.extend(_mobility_evidence_lines(job, value["description"]))
        lines.extend(_relocation_evidence_lines(payload.get("relocation_evidence") or {}))
        lines.append("Remote worldwide сам по себе не подтверждает право работать из любой страны.")
        return "\n".join(lines)
    if section == "competition":
        lines = [heading, "👥 <b>Конкуренция</b>", *_applicant_count_lines(payload, details)]
        competition = (getattr(match, "recommendation_scores", None) or {}).get("competition") or {}
        if competition.get("score") is not None:
            lines.append(f"Мягкая оценка Job Agent: {competition['score']}/100")
        evidence = str(competition.get("evidence") or "")
        if evidence:
            lines.append("Основание: " + html.escape(_clip(evidence, 300)))
        return "\n".join(lines)
    if section == "source":
        lines = [heading, "🌐 <b>Источник</b>", f"Провайдер: {html.escape(value['source'])}"]
        source_job_id = str(payload.get("source_job_id") or "").strip()
        if source_job_id:
            lines.append("ID у источника: " + html.escape(_clip(source_job_id, 100)))
        observed = str(payload.get("source_observed_at") or "")
        if observed:
            lines.append("Проверено: " + html.escape(_published(observed)))
        url = _safe_http_url(payload.get("url"))
        if url:
            lines.append(f'<a href="{html.escape(url, quote=True)}">Открыть оригинал вакансии</a>')
        warning = str(payload.get("warning") or "")
        if warning:
            lines.append("⚠️ " + html.escape(_clip(warning, 250)))
        return "\n".join(lines)
    raise ValueError("Unsupported vacancy section")

def render_jobs_list(
    rows: list[tuple[object, object]],
    *,
    source_links: dict[int, str | tuple[str, str] | list[tuple[str, str]]] | None = None,
    below_threshold: int | None = None,
    search_scope: str | None = None,
) -> str:
    if below_threshold is None:
        lines = ["🔥 <b>Совпадения по рейтингу</b>", ""]
    else:
        lines = [
            f"🔎 <b>Ниже порога {int(below_threshold)} · ручной просмотр</b>",
            "Рейтинг ниже обычного порога; право на работу и условия переезда не подтверждены автоматически.",
            "",
        ]
    if search_scope:
        label = "Career-first" if search_scope == "career" else "Relocation-first"
        lines.insert(1, f"🧭 <b>{label}</b>")
    source_links = source_links or {}
    for match, job in rows:
        title = _clip(repair_mojibake(job.title or ""), 90)
        company = _clip(repair_mojibake(job.company or ""), 70)
        salary = format_salary(
            job.salary_from,
            job.salary_to,
            job.salary_currency,
            period=getattr(job, "salary_period", None),
        )
        experience = extract_experience(job.description)
        meta = [f"💰 {salary}"]
        if job.city or job.country:
            meta.append(f"📍 {repair_mojibake(job.city or job.country or '')}")
        if job.work_mode:
            meta.append(f"🏠 {repair_mojibake(job.work_mode)}")
        if experience:
            meta.append(f"🕒 {experience}")
        lines.append(f"<b>#{job.id} · {match.total_score}/100</b> — {html.escape(title)}")
        if company:
            lines.append(html.escape(company))
        source_info = source_links.get(job.id)
        if isinstance(source_info, str):
            source_items = [(source_info, "Himalayas")]
        elif isinstance(source_info, tuple) and len(source_info) == 2:
            source_items = [source_info]
        elif isinstance(source_info, list):
            source_items = source_info
        else:
            source_items = []
        if source_items:
            anchors = [
                f'<a href="{html.escape(safe_url, quote=True)}">{html.escape(name)}</a>'
                for url, name in source_items
                if (safe_url := _safe_http_url(url)) and name
            ]
            if anchors:
                lines.append("🌐 Источник: " + " · ".join(anchors))
        lines.append(html.escape(" · ".join(meta)))
        lines.append(f"Подробнее: /job {job.id}" + (f" {search_scope}" if search_scope else ""))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_job_details(payload: dict) -> str:
    job = payload["job"]
    match = payload["match"]
    details = payload.get("details") or {}
    source = str(payload.get("source") or "unknown").upper()
    url = _safe_http_url(payload.get("url")) or ""
    warning = str(payload.get("warning") or "")
    fallback_salary_text = str(payload.get("fallback_salary_text") or "")

    title = _clip(repair_mojibake(str(details.get("title") or job.title or "")), 140)
    company = _clip(repair_mojibake(str(details.get("company") or job.company or "")), 120)
    description_full = clean_html_text(str(details.get("description") or job.description or ""))
    description = _clip(description_full, 2250)
    salary = _salary(job, details, fallback_salary_text)
    experience = _experience(job, details)
    location = _clip(_location(job, details), 160)
    work_mode = _clip(_work_mode(job, details), 140)
    remote_scope = _clip(_remote_scope(job, details), 220)
    timezone_restrictions = _timezone_restrictions(details)
    applicant_location = _clip(clean_html_text(str(details.get("applicant_location") or "")), 140)
    published_at = _published(str(details.get("published_at") or job.published_at or ""))

    lines = [
        f"🔥 <b>#{job.id} · {html.escape(title)}</b>",
        html.escape(company or "Компания не указана"),
        "",
        f"🎯 Match: <b>{match.total_score}/100</b>",
        f"🌐 Источник: <b>{html.escape(source)}</b>",
        f"💰 {html.escape(salary)}",
        f"📍 {html.escape(location)}",
        f"🏠 {html.escape(work_mode)}",
        f"🕒 {html.escape(experience)}",
    ]
    if payload.get("search_profile_name"):
        lines.insert(4, "🧭 Профиль: " + html.escape(_clip(str(payload["search_profile_name"]), 100)))
    if remote_scope:
        lines.append(f"🌍 География remote: {html.escape(remote_scope)}")
    if timezone_restrictions:
        lines.append(f"⏱ Часовые пояса по источнику: {html.escape(timezone_restrictions)}")
    if applicant_location:
        lines.append(f"👥 Доступно для: {html.escape(applicant_location)}")
    if published_at:
        lines.append(f"📅 Опубликована: {html.escape(_clip(published_at, 80))}")
    source_job_id = str(payload.get("source_job_id") or "").strip()
    if source_job_id:
        lines.append(f"🆔 ID у источника: {html.escape(_clip(source_job_id, 100))}")
    observed_at = str(payload.get("source_observed_at") or "")
    try:
        observed_date = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        observed_date = None
    if observed_date is not None and observed_date.utcoffset() is not None:
        lines.append(f"🔎 Источник обнаружен: {_published(observed_at)}")
    if source == "HIMALAYAS" or "availability" in details:
        lines.extend(html.escape(line) for line in vacancy_availability_lines(details))

    lines.extend(_mobility_evidence_lines(job, description_full))
    lines.extend(_relocation_evidence_lines(payload.get("relocation_evidence") or {}))
    lines.extend(relocation_followup_lines(payload.get("relocation_evidence") or {}))

    if description:
        lines.extend(["", "📝 <b>Описание вакансии</b>", html.escape(description)])

    lines.extend([
        "",
        "📊 <b>Оценка Job Agent</b>",
        f"Technical: {match.technical_score}/100",
        f"Geography: {match.geography_score}/100",
        f"Salary: {match.salary_score}/100",
        f"Relocation: {match.relocation_score}/100",
    ])
    recommendation_scores = getattr(match, "recommendation_scores", None) or {}
    if recommendation_scores:
        labels = {
            "growth": "Рост", "fast_exit": "Быстрый выход",
            "interview_risk": "Риск интервью", "remote": "Удалёнка",
            "security": "Безопасность", "infrastructure": "Инфраструктура",
            "competition": "Конкуренция",
        }
        lines.extend(["", "🧭 <b>Recommendation v2</b>"])
        for key, label in labels.items():
            item = recommendation_scores.get(key) or {}
            value = item.get("score")
            display = f"{value}/100" if value is not None else "н/д"
            evidence = str(item.get("evidence") or "")
            lines.append(f"{html.escape(label)}: {display}" + (f" — {html.escape(_clip(evidence, 140))}" if evidence else ""))
        lines.append("Конкуренция н/д означает, что публичный источник не дал числа кандидатов.")
    if match.reason:
        lines.extend(["", f"💡 {html.escape(_clip(repair_mojibake(match.reason), 450))}"])
    if warning:
        lines.extend(["", f"⚠️ {html.escape(_clip(warning, 250))}"])
    if url:
        lines.extend(["", f'<a href="{html.escape(url, quote=True)}">🔗 Открыть оригинал вакансии</a>'])

    rendered = "\n".join(lines)
    rendered_units = len(rendered.encode("utf-16-le")) // 2
    if rendered_units > 3900 and description:
        escaped_description = html.escape(description)
        fixed = rendered.replace(escaped_description, "", 1)
        target = 3900 - len(fixed.encode("utf-16-le")) // 2
        rendered = rendered.replace(
            escaped_description, _escape_with_utf16_limit(description, target), 1
        )
    return rendered


def render_fact_comparison(payload: dict) -> str:
    job = payload["job"]
    comparison = payload["comparison"]
    language_fit = payload.get("language_fit")
    facts_by_id = {
        int(fact.id): fact
        for fact in payload.get("facts", [])
        if getattr(fact, "id", None) is not None
    }

    title = _clip(repair_mojibake(str(job.title or "")), 120)

    status_groups = (
        ("commercial", "✅ <b>Коммерческий опыт</b>"),
        ("lab", "🧪 <b>Lab / personal projects</b>"),
        ("learning", "📚 <b>Изучается</b>"),
        ("unknown", "❔ <b>Тип опыта не указан</b>"),
        ("missing", "❌ <b>Не подтверждено Candidate Facts</b>"),
    )

    importance_groups = (
        ("required", "🟥 <b>Обязательные требования</b>"),
        ("preferred", "🟨 <b>Желательно / будет плюсом</b>"),
        ("unknown", "⬜ <b>Прочие технические сигналы</b>"),
    )

    lines = [
        "🧩 <b>Сравнение с профилем</b>",
        f"#{job.id} · {html.escape(title)}",
        "",
    ]
    rendered_fact_references = False

    if comparison.total == 0 and language_fit is None:
        lines.extend([
            "Технические требования из поддерживаемого словаря не найдены.",
            "",
            "Это не означает, что требований в вакансии нет — "
            "детерминированный анализатор пока не распознал их.",
        ])
        return "\n".join(lines)

    if comparison.total:
        lines.append(
            f"📌 Найдено в Candidate Facts: "
            f"<b>{comparison.present}/{comparison.total}</b>"
        )
    else:
        lines.append("Технические требования из поддерживаемого словаря не найдены.")
    alternative_groups = (
        comparison.alternative_groups + comparison.preferred_alternative_groups
    )
    if alternative_groups:
        groups = "; ".join(
            " или ".join(html.escape(skill) for skill in group)
            for group in alternative_groups
        )
        lines.append(
            f"ℹ Альтернативы для технической оценки: {groups}. "
            "Числа выше показывают отдельные упоминания навыков."
        )

    for importance, importance_heading in importance_groups:
        items = comparison.items_for_importance(importance)

        if not items:
            continue

        present = comparison.present_for_importance(importance)
        total = comparison.total_for_importance(importance)

        lines.extend([
            "",
            f"{importance_heading}: <b>{present}/{total}</b>",
        ])

        for status, status_heading in status_groups:
            matched = [
                item.skill
                for item in items if item.status == status
            ]

            if not matched:
                continue

            lines.extend(["", status_heading])
            for item in items:
                if item.status != status:
                    continue
                line = f"• {html.escape(item.skill)}"
                references = []
                for fact_id in item.fact_ids:
                    fact = facts_by_id.get(fact_id)
                    if fact is None:
                        continue
                    provenance = str(getattr(fact, "provenance", "") or "").strip()
                    reference = f"факт #{fact_id}"
                    if provenance:
                        reference += f" · {html.escape(_clip(provenance, 32))}"
                    references.append(reference)
                if references:
                    rendered_fact_references = True
                    line += " <i>(" + "; ".join(references) + ")</i>"
                lines.append(line)

    if rendered_fact_references:
        lines.extend(["", "ID фактов можно проверить и изменить командами /facts и /fact."])

    if language_fit is not None:
        candidate = language_fit.candidate_level or "не указан"
        status_text = {
            "meets": "✅ уровень профиля соответствует",
            "below": "⚠️ уровень профиля ниже указанного",
            "unknown": "❔ уровень профиля не указан или не распознан",
        }[language_fit.status]
        lines.extend([
            "",
            "🌐 <b>Явный уровень английского</b>",
            f"Уровень вакансии: <b>{html.escape(language_fit.required_level)}</b>",
            "Статус: " + {
                "required": "явно требуется",
                "preferred": "указан как преимущество",
                "unspecified": "не уточнён",
            }[language_fit.requirement],
            f"Профиль: <b>{html.escape(candidate)}</b> — {status_text}.",
            f"Источник: {html.escape(language_fit.evidence)}",
            "Уровень языка показан отдельно и пока не меняет техническую оценку.",
        ])

    if comparison.total:
        lines.extend([
            "",
            "ℹ <i>Важность берётся из структуры вакансии. "
            "Тип опыта берётся только из Candidate Facts. "
            "Lab/learning не считаются коммерческим опытом.</i>",
        ])

    return "\n".join(lines)


def render_resume_diff(payload: dict) -> str:
    job = payload["job"]
    resume = payload["resume"]
    diff = payload["resume_diff"]
    headings = (
        ("supported_in_resume", "✅ Есть в Candidate Facts и в резюме"),
        ("supported_missing_from_resume", "📝 Есть в Candidate Facts, но не найдено в резюме"),
        ("resume_only_unconfirmed", "⚠️ Есть в резюме, но не найдено в Candidate Facts"),
        ("missing_from_both", "❌ Не найдено ни в резюме, ни в Candidate Facts"),
    )
    title = _clip(repair_mojibake(str(job.title or "")), 120)
    lines = [
        "🧾 <b>Сверка резюме с вакансией</b>",
        f"#{job.id} · {html.escape(title)}",
        f"Резюме: <b>{html.escape(_clip(str(resume.name or ''), 100))}</b> (ID {resume.id})",
        "",
    ]
    alternative_groups = diff.get("alternative_groups") or ()
    has_detected_requirements = any(diff.get(key) for key, _ in headings) or bool(alternative_groups)
    if not has_detected_requirements:
        lines.append("Поддерживаемый словарь не распознал в вакансии технические требования.")
    else:
        for key, heading in headings:
            skills = diff.get(key) or ()
            if skills:
                lines.extend([heading, "• " + ", ".join(html.escape(skill) for skill in skills), ""])
        if alternative_groups:
            lines.extend(["🔀 Альтернативные требования (достаточно одного варианта)"])
            lines.extend("• " + html.escape(_alternative_group_summary(item)) for item in alternative_groups)
            lines.append("")
    lines.append(
        "Это автоматическая сверка известных технических терминов: она не редактирует резюме "
        "и не подтверждает опыт. Проверяй каждое изменение перед отправкой."
    )
    return "\n".join(lines)


def render_application_package(payload: dict) -> str:
    job = payload["job"]
    resume = payload.get("resume")
    diff = payload.get("resume_diff") or {}
    title = _clip(repair_mojibake(str(job.title or "")), 120)
    company = _clip(repair_mojibake(str(job.company or "")), 100)
    lines = [
        "📝 <b>Черновик пакета отклика</b>",
        _escape_clipped(title, 300) + (f" — {_escape_clipped(company, 200)}" if company else ""),
        f"Резюме: <b>{_escape_clipped(_clip(str(resume.name or ''), 100), 200)}</b> (ID {resume.id})"
        if resume else "Резюме: не выбрано",
        "",
        "<b>Проверь перед отправкой</b>",
    ]
    if not resume:
        lines.append("• Выбери и сохрани подходящее резюме через /resumes.")
    if diff.get("supported_missing_from_resume"):
        skills = ", ".join(html.escape(skill) for skill in diff["supported_missing_from_resume"])
        lines.append(f"• В Candidate Facts есть, в CV не найдено: {skills}. Добавляй только после своей проверки.")
    if diff.get("resume_only_unconfirmed"):
        skills = ", ".join(html.escape(skill) for skill in diff["resume_only_unconfirmed"])
        lines.append(f"• В CV есть, в Candidate Facts нет: {skills}. Проверь точность этих формулировок.")
    if diff.get("missing_from_both"):
        skills = ", ".join(html.escape(skill) for skill in diff["missing_from_both"])
        lines.append(f"• Не найдено в CV и Candidate Facts: {skills}. Не добавляй без подтверждённого опыта.")
    alternative_groups = diff.get("alternative_groups") or ()
    for item in alternative_groups:
        lines.append("• Альтернатива: " + html.escape(_alternative_group_summary(item)))
    recognized_skills = any(diff.get(key) for key in (
        "supported_in_resume", "supported_missing_from_resume",
        "resume_only_unconfirmed", "missing_from_both",
    ))
    has_alternative_discrepancy = any(
        item.get("status") != "confirmed" or item.get("unconfirmed_resume_options")
        for item in alternative_groups
    )
    if not recognized_skills and not alternative_groups:
        lines.append(
            "• Технические требования из поддерживаемого словаря не распознаны. "
            "Проверь полный текст вакансии вручную."
        )
    elif not has_alternative_discrepancy and not any(diff.get(key) for key in (
        "supported_missing_from_resume", "resume_only_unconfirmed", "missing_from_both",
    )):
        lines.append("• По распознанным навыкам дополнительных расхождений нет.")
    source_url = _safe_http_url(payload.get("url"))
    safe_link = source_url is not None
    if safe_link:
        url = html.escape(source_url, quote=True)
        if len(url.encode("utf-16-le")) // 2 <= 900:
            link_line = f'<a href="{url}">Открыть вакансию для ручной отправки</a>'
        else:
            link_line = f"• Ссылка слишком длинная для предпросмотра; открой /job {job.id} перед откликом."
    else:
        link_line = "• Прямая ссылка на источник не сохранена; найди вакансию вручную перед откликом."
    tail = []
    source = str(payload.get("source") or "").strip()
    source_job_id = str(payload.get("source_job_id") or "").strip()
    if source or source_job_id:
        selected = html.escape(_clip(source, 64)) if source else "источник не записан"
        provider_id = f" · ID {html.escape(_clip(source_job_id, 80))}" if source_job_id else ""
        tail.append(f"Выбранная публикация: {selected}{provider_id}")
    tail.append(link_line)
    tail.extend(_mobility_evidence_lines(job, str(getattr(job, "description", "") or "")))
    evidence_snapshot = payload.get("relocation_evidence")
    if isinstance(evidence_snapshot, dict) and evidence_snapshot.get("schema") == "relocation_evidence_v1":
        captured = html.escape(str(evidence_snapshot.get("captured_at") or "unknown")[:25])
        tail.extend(["", f"🧾 Снимок условий источника сохранён ({captured}); точные цитаты и provenance доступны в экспорте."])
    else:
        tail.extend(["", "🧾 Структурированный снимок условий источника не записан; не считай текущий текст историческим подтверждением."])
    tail.extend([
        "",
        "<b>Черновик сопроводительного</b>",
        _escape_with_utf16_limit(_clip(str(payload.get("cover_letter") or ""), 1600), 900)
        or "Черновик отсутствует.",
        "",
        "Черновик не отправлен. Проверь факты, язык и содержание и отправь сам.",
    ])
    notice = f"… Предпросмотр сокращён. Полная сверка: /resumediff {job.id}; вакансия: /job {job.id}."
    def units(value: str) -> int:
        return len(value.encode("utf-16-le")) // 2

    budget = 3700 - units("\n".join(tail)) - units(notice) - 2
    kept, used, omitted = [], 0, False
    for line in lines:
        line_units = units(line) + 1
        if used + line_units <= budget:
            kept.append(line)
            used += line_units
        else:
            omitted = True
    if omitted:
        kept.append(notice)
    return "\n".join(kept + tail)


def _alternative_group_summary(item: dict) -> str:
    options = " или ".join(str(skill) for skill in item.get("options", ()))
    confirmed = " / ".join(str(skill) for skill in item.get("confirmed_options", ()))
    resume = " / ".join(str(skill) for skill in item.get("resume_options", ()))
    facts = " / ".join(str(skill) for skill in item.get("candidate_fact_options", ()))
    status = item.get("status")
    if status == "confirmed":
        extras = " / ".join(str(skill) for skill in item.get("unconfirmed_resume_options", ()))
        suffix = f" В CV также есть неподтверждённое: {extras}. Проверь точность." if extras else ""
        return f"{options}: один и тот же вариант есть в CV и Candidate Facts ({confirmed}).{suffix}"
    if status == "resume_unconfirmed":
        suffix = f" Candidate Facts подтверждают: {facts}." if facts else " Candidate Facts не подтверждают варианты."
        return f"{options}: вариант в CV ({resume}), но совпадающего подтверждения нет.{suffix} Проверь точность."
    if status == "facts_not_in_resume":
        return f"{options}: Candidate Facts подтверждают {facts}, но этот вариант не найден в CV."
    return f"{options}: ни один вариант не найден в CV или Candidate Facts."


def render_applications(applications: list) -> str:
    status_labels = {
        "prepared": "черновик",
        "reviewed": "проверен",
        "submitted": "отправлен вручную",
        "interview": "интервью",
        "offer": "оффер",
        "rejected": "отказ",
        "withdrawn": "снят",
        "sent": "отправлен",
        "sending": "попытка начата — результат не подтверждён",
        "external": "внешняя форма — отправка не подтверждена",
        "unknown": "отправка не подтверждена",
    }
    lines = ["📂 <b>Отклики</b>", ""]
    if not applications:
        return "📂 <b>Откликов пока нет.</b> Подготовь пакет из вакансии через кнопку «Подготовить отклик»."
    for item in applications:
        created = getattr(item, "created_at", None)
        created_text = created.strftime("%Y-%m-%d") if created else "дата неизвестна"
        snippet = _clip(str(getattr(item, "message", "") or "").replace("\n", " "), 120)
        lines.append(
            f"<b>#{item.id}</b> · вакансия #{item.job_id} · "
            f"{html.escape(status_labels.get(item.status, item.status))} · {html.escape(created_text)}"
        )
        if item.resume_id:
            lines.append(f"Резюме ID {item.resume_id}")
        if snippet:
            lines.append(html.escape(snippet))
        lines.append("")
    lines.append("Статус: /application <id> reviewed|submitted|interview|offer|rejected|withdrawn · История: /application <id> history")
    return "\n".join(lines)


def render_application_history(events: list) -> str:
    labels = {
        "prepared": "черновик создан",
        "reviewed": "отмечен как проверенный",
        "submitted": "отмечен отправленным вручную",
        "interview": "отмечено интервью",
        "offer": "отмечен оффер",
        "rejected": "отмечен отказ",
        "withdrawn": "отмечен снятым",
        "sent": "отправлен",
        "sending": "HH-попытка зарезервирована; результат не подтверждён",
        "external": "переход на внешнюю форму, отправка не подтверждена",
        "unknown": "исход отправки неизвестен",
    }
    if not events:
        return "История статусов пуста."
    lines = ["🕓 <b>История статусов</b>", ""]
    for event in events:
        timestamp = getattr(event, "created_at", None)
        timestamp_text = timestamp.strftime("%Y-%m-%d %H:%M UTC") if timestamp else "время неизвестно"
        label = labels.get(event.status, event.status)
        lines.append(f"{html.escape(timestamp_text)} — {html.escape(label)}")
    return "\n".join(lines)


def render_application_export(application, events: list | None = None) -> str:
    created = getattr(application, "created_at", None)
    created_text = created.strftime("%Y-%m-%d %H:%M UTC") if created else "unknown"
    snapshot = getattr(application, "vacancy_snapshot", None) or {}
    lines = [
        f"Application package #{application.id}",
        (f"Saved vacancy: {snapshot.get('title') or 'not recorded'} — "
         f"{snapshot.get('company') or 'not recorded'}" if snapshot
         else "Vacancy metadata snapshot unavailable for this record."),
        f"Status: {application.status}",
        "Status is locally recorded and does not independently verify receipt by the employer or provider.",
        f"Prepared: {created_text}",
        f"Source: {application.source_id}",
        f"Saved posting source: {snapshot.get('source_id') or 'not recorded'}",
        f"Saved provider posting ID: {snapshot.get('source_job_id') or 'not recorded'}",
        f"Saved vacancy URL: {snapshot.get('source_url') or 'not recorded'}",
        f"Recorded external URL: {application.external_url or 'not recorded'}",
        f"Saved resume ID: {application.resume_id or 'not selected'}",
        f"External resume ID: {application.resume_external_id or 'not recorded'}",
        "",
        "=== Saved vacancy description (as stored) ===",
        snapshot.get("description") or "No vacancy description snapshot is available for this record.",
    ]
    saved_evidence = snapshot.get("relocation_evidence")
    if isinstance(saved_evidence, dict):
        lines.extend([
            "",
            "=== Saved source-scoped relocation evidence ===",
            json.dumps(saved_evidence, ensure_ascii=False, sort_keys=True, indent=2),
        ])
    else:
        lines.extend([
            "",
            "No source-scoped relocation evidence snapshot is available for this record; current source data was not backfilled.",
        ])
    lines.extend([
        "",
        "=== Saved resume text snapshot ===",
    ])
    if application.resume_snapshot:
        lines.append(application.resume_snapshot)
    elif application.resume_id:
        lines.append("No resume-content snapshot is available for this record.")
    else:
        lines.append("No resume was selected for this record.")
    lines.extend(["", "=== Saved cover-letter text ===", application.message or "No cover-letter text."])
    lines.extend(["", "=== Recorded status history ==="])
    if events is None:
        lines.append("Status history unavailable.")
    elif not events:
        lines.append("No status events recorded.")
    else:
        for event in events:
            timestamp = getattr(event, "created_at", None)
            timestamp_text = timestamp.strftime("%Y-%m-%d %H:%M UTC") if timestamp else "time unknown"
            lines.append(f"{timestamp_text} — {event.status}")
    return "\n".join(lines)


def render_interview_plan(job, plan: tuple[dict, ...]) -> str:
    title = _clip(repair_mojibake(str(job.title or "")), 120)
    lines = [
        "🎤 <b>Практика по вакансии</b>",
        f"#{job.id} · {html.escape(title)}",
        "",
    ]
    if not plan:
        lines.extend([
            "Для распознанных требований пока нет подготовленного сценария.",
            "Словарь упражнений покрывает выбранные DevOps/Infrastructure темы и будет расширяться.",
        ])
    else:
        importance_labels = {"required": "обязательно", "preferred": "желательно", "unknown": "важность неясна"}
        status_labels = {
            "commercial": "Candidate Fact: commercial",
            "lab": "Candidate Fact: lab",
            "learning": "Candidate Fact: learning",
            "unknown": "Candidate Fact: тип не указан",
            "missing": "Candidate Fact: отсутствует",
        }
        for index, item in enumerate(plan, 1):
            lines.extend([
                f"<b>{index}. {html.escape(item['skill'])}</b> · "
                f"{importance_labels.get(item['importance'], 'важность неясна')} · "
                f"{status_labels.get(item['candidate_status'], 'Candidate Fact: неизвестно')}",
            ])
            options = item.get("alternative_options")
            if options:
                labels = " или ".join(html.escape(_clip(str(option), 50)) for option in options)
                lines.append(f"Альтернатива: {labels}; достаточно одного варианта.")
            lines.extend([
                html.escape(_clip(item["scenario"], 300)),
                "Задание: " + html.escape(_clip(item["task"], 300)),
                "Ориентиры: " + "; ".join(html.escape(_clip(str(point), 100)) for point in item["criteria"]),
                "",
            ])
    lines.append(
        "Это тренировочные сценарии, не предсказание вопросов и не оценка собеседования. "
        "Candidate Fact показывает сохранённый тип опыта, а не результат тестирования."
    )
    return "\n".join(lines)
