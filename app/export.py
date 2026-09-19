from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.database.models import Job, JobMatch
from app.domain.job_text import format_salary


def prepare_export_data(
    rows: list[tuple[JobMatch, Job]],
    urls: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    urls = urls or {}
    items: list[dict[str, Any]] = []
    for match, job in rows:
        salary_text = format_salary(job.salary_from, job.salary_to, job.salary_currency)
        items.append({
            "match_id": match.id,
            "job_id": job.id,
            "title": job.title,
            "company": job.company or "Не указана",
            "url": urls.get(job.id, ""),
            "total_score": match.total_score,
            "scores": {
                "technical": match.technical_score,
                "geography": match.geography_score,
                "salary": match.salary_score,
                "relocation": match.relocation_score,
            },
            "location": {
                "city": job.city or "",
                "country": job.country or "",
                "work_mode": job.work_mode or "",
                "remote_scope": job.remote_scope or "",
                "relocation": job.relocation,
                "visa_sponsorship": job.visa_sponsorship,
            },
            "salary": {
                "from": job.salary_from,
                "to": job.salary_to,
                "currency": job.salary_currency or "",
                "text": salary_text,
            },
            "reason": match.reason or "",
            "status": match.status,
            "description": job.description or "",
            "published_at": job.published_at or "",
            "created_at": match.created_at.isoformat() if getattr(match, "created_at", None) else "",
        })
    return items


def export_to_markdown(data: list[dict[str, Any]]) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# ⭐ Сохранённые вакансии",
        "",
        f"- **Дата выгрузки:** {now_str}",
        f"- **Всего вакансий:** {len(data)}",
        "",
        "---",
        "",
    ]

    for idx, item in enumerate(data, start=1):
        lines.append(f"## {idx}. {item['title']} — {item['company']}")
        lines.append(
            f"- **Оценка:** {item['total_score']}/100 "
            f"(Tech: {item['scores']['technical']} | "
            f"Geo: {item['scores']['geography']} | "
            f"Salary: {item['scores']['salary']} | "
            f"Relo: {item['scores']['relocation']})"
        )
        loc_parts = [p for p in [item['location']['city'], item['location']['country']] if p]
        loc_str = ", ".join(loc_parts) if loc_parts else "не указана"
        lines.append(f"- **Локация:** {loc_str}")
        if item["location"]["work_mode"]:
            lines.append(f"- **Формат работы:** {item['location']['work_mode']}")
        lines.append(f"- **Зарплата:** {item['salary']['text']}")
        if item["url"]:
            lines.append(f"- **Ссылка:** {item['url']}")
        if item["reason"]:
            lines.append(f"- **Причина скоринга:** {item['reason']}")
        lines.append("")
        if item["description"]:
            lines.append("### Описание")
            lines.append(item["description"].strip())
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def export_to_json(data: list[dict[str, Any]]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
