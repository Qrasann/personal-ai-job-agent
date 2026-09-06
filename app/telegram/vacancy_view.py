from __future__ import annotations

import html
from datetime import datetime

from app.domain.job_text import clean_html_text, extract_experience, format_salary, repair_mojibake


def _clip(value: str, limit: int) -> str:
    text = value or ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _location(job, details: dict) -> str:
    return str(details.get("city") or job.city or job.country or "не указана")


def _experience(job, details: dict) -> str:
    direct = clean_html_text(str(details.get("experience") or ""))
    if direct:
        return direct
    return extract_experience(str(details.get("description") or job.description or "")) or "не указан"


def _work_mode(job, details: dict) -> str:
    return clean_html_text(str(details.get("work_mode") or job.work_mode or "")) or "не указан"


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
            str(job.description or ""),
        )
        if part
    )
    return format_salary(
        details.get("salary_from") if details.get("salary_from") is not None else job.salary_from,
        details.get("salary_to") if details.get("salary_to") is not None else job.salary_to,
        details.get("salary_currency") or job.salary_currency,
        fallback_text=salary_text,
    )


def _published(value: str) -> str:
    text = clean_html_text(value)
    if not text:
        return ""
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    return parsed.strftime("%d.%m.%Y %H:%M")


def render_queue_card(
    match,
    job,
    *,
    header: str,
    lane: str,
    position: int,
    total: int,
) -> str:
    title = _clip(repair_mojibake(str(getattr(job, "title", "") or "")), 120)
    company = _clip(repair_mojibake(str(getattr(job, "company", "") or "")), 100)
    description = str(getattr(job, "description", "") or "")
    salary = format_salary(
        getattr(job, "salary_from", None),
        getattr(job, "salary_to", None),
        getattr(job, "salary_currency", None),
        fallback_text=description,
    )

    location = repair_mojibake(
        str(getattr(job, "city", None) or getattr(job, "country", None) or "не указана")
    )
    work_mode = repair_mojibake(str(getattr(job, "work_mode", None) or "не указан"))

    lines = [
        f"<b>{html.escape(header)}</b>",
        f"<b>{html.escape(lane)}</b>",
        "",
        f"<b>{html.escape(title)}</b>",
        html.escape(company or "Компания не указана"),
        "",
        f"💰 {html.escape(salary)}",
        f"📍 {html.escape(location)}",
        f"🏠 {html.escape(work_mode)}",
        "",
        f"🎯 Match: <b>{getattr(match, 'total_score', 0)}/100</b>",
    ]

    components = []
    for label, attr in (
        ("Tech", "technical_score"),
        ("Geo", "geography_score"),
        ("Salary", "salary_score"),
        ("Reloc", "relocation_score"),
    ):
        value = getattr(match, attr, None)
        if value is not None:
            components.append(f"{label} {value}")
    if components:
        lines.append("📊 " + " · ".join(components))

    reason = _clip(repair_mojibake(str(getattr(match, "reason", "") or "")), 280)
    if reason:
        lines.append(f"💡 {html.escape(reason)}")

    lines.append(f"📌 {position} из {total}")
    return "\n".join(lines)

def render_jobs_list(rows: list[tuple[object, object]]) -> str:
    lines = ["🔥 <b>Последние совпадения</b>", ""]
    for match, job in rows:
        title = _clip(repair_mojibake(job.title or ""), 90)
        company = _clip(repair_mojibake(job.company or ""), 70)
        salary = format_salary(job.salary_from, job.salary_to, job.salary_currency, fallback_text=job.description)
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
        lines.append(html.escape(" · ".join(meta)))
        lines.append(f"Подробнее: /job {job.id}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_job_details(payload: dict) -> str:
    job = payload["job"]
    match = payload["match"]
    details = payload.get("details") or {}
    source = str(payload.get("source") or "unknown").upper()
    url = str(payload.get("url") or "")
    warning = str(payload.get("warning") or "")
    fallback_salary_text = str(payload.get("fallback_salary_text") or "")

    title = _clip(repair_mojibake(str(details.get("title") or job.title or "")), 140)
    company = _clip(repair_mojibake(str(details.get("company") or job.company or "")), 120)
    description = clean_html_text(str(details.get("description") or job.description or ""))
    description = _clip(description, 2250)
    salary = _salary(job, details, fallback_salary_text)
    experience = _experience(job, details)
    location = _clip(_location(job, details), 160)
    work_mode = _clip(_work_mode(job, details), 140)
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
    if applicant_location:
        lines.append(f"👥 Доступно для: {html.escape(applicant_location)}")
    if published_at:
        lines.append(f"📅 Опубликована: {html.escape(_clip(published_at, 80))}")

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
    if match.reason:
        lines.extend(["", f"💡 {html.escape(_clip(repair_mojibake(match.reason), 450))}"])
    if warning:
        lines.extend(["", f"⚠️ {html.escape(_clip(warning, 250))}"])
    if url:
        lines.extend(["", f'<a href="{html.escape(url, quote=True)}">🔗 Открыть оригинал вакансии</a>'])

    return "\n".join(lines)


def render_fact_comparison(payload: dict) -> str:
    job = payload["job"]
    comparison = payload["comparison"]

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

    if comparison.total == 0:
        lines.extend([
            "Технические требования из поддерживаемого словаря не найдены.",
            "",
            "Это не означает, что требований в вакансии нет — "
            "детерминированный анализатор пока не распознал их.",
        ])
        return "\n".join(lines)

    lines.append(
        f"📌 Найдено в Candidate Facts: "
        f"<b>{comparison.present}/{comparison.total}</b>"
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
            skills = [
                item.skill
                for item in items
                if item.status == status
            ]

            if not skills:
                continue

            lines.extend(["", status_heading])
            lines.extend(
                f"• {html.escape(skill)}"
                for skill in skills
            )

    lines.extend([
        "",
        "ℹ <i>Важность берётся из структуры вакансии. "
        "Тип опыта берётся только из Candidate Facts. "
        "Lab/learning не считаются коммерческим опытом.</i>",
    ])

    return "\n".join(lines)
