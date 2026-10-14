from __future__ import annotations

import html
from datetime import datetime
from urllib.parse import urlsplit

from app.domain.job_text import clean_html_text, extract_experience, format_salary, repair_mojibake
from app.domain.remote_evidence import remote_residence_requirement, restricted_remote_scope
from app.domain.support_evidence import existing_work_authorization_required, support_evidence
from app.domain.vacancy_availability import vacancy_availability_lines


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
    return parsed.strftime("%d.%m.%Y %H:%M")


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
                f'<a href="{html.escape(url, quote=True)}">{html.escape(name)}</a>'
                for url, name in source_items
                if url and name
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
    url = str(payload.get("url") or "")
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
    if source == "HIMALAYAS" or "availability" in details:
        lines.extend(html.escape(line) for line in vacancy_availability_lines(details))

    lines.extend(_mobility_evidence_lines(job, description_full))

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

    return "\n".join(lines)


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
    has_detected_requirements = any(diff.get(key) for key, _ in headings)
    if not has_detected_requirements:
        lines.append("Поддерживаемый словарь не распознал в вакансии технические требования.")
    else:
        for key, heading in headings:
            skills = diff.get(key) or ()
            if skills:
                lines.extend([heading, "• " + ", ".join(html.escape(skill) for skill in skills), ""])
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
        f"{html.escape(title)}" + (f" — {html.escape(company)}" if company else ""),
        f"Резюме: <b>{html.escape(_clip(str(resume.name or ''), 100))}</b> (ID {resume.id})"
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
    if not any(diff.get(key) for key in (
        "supported_missing_from_resume", "resume_only_unconfirmed", "missing_from_both",
    )):
        lines.append("• По распознанным навыкам дополнительных расхождений нет.")
    source_url = str(payload.get("url") or "").strip()
    parsed_url = urlsplit(source_url)
    if (
        parsed_url.scheme.casefold() in {"http", "https"}
        and parsed_url.hostname
        and not parsed_url.username
        and not parsed_url.password
    ):
        url = html.escape(_clip(source_url, 600), quote=True)
        lines.append(f'<a href="{url}">Открыть вакансию для ручной отправки</a>')
    else:
        lines.append("• Прямая ссылка на источник не сохранена; найди вакансию вручную перед откликом.")
    lines.extend([
        "",
        "<b>Черновик сопроводительного</b>",
        html.escape(_clip(str(payload.get("cover_letter") or ""), 1600)) or "Черновик отсутствует.",
        "",
        "Черновик не отправлен. Проверь факты, язык и содержание и отправь сам.",
    ])
    return "\n".join(lines)


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


def render_application_export(application, job, events: list | None = None) -> str:
    created = getattr(application, "created_at", None)
    created_text = created.strftime("%Y-%m-%d %H:%M UTC") if created else "unknown"
    lines = [
        f"Application package #{application.id}",
        f"Vacancy: {job.title} — {job.company}",
        f"Status: {application.status}",
        f"Prepared: {created_text}",
        f"Source: {application.source_id}",
        f"Vacancy URL: {application.external_url or 'not recorded'}",
        f"Saved resume ID: {application.resume_id or 'not selected'}",
        f"External resume ID: {application.resume_external_id or 'not recorded'}",
        "",
        "=== Saved resume text snapshot ===",
    ]
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
