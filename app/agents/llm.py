from __future__ import annotations

import json
from openai import OpenAI

from app.config import settings
from app.database.models import CandidateFact, Job, ResumeProfile


def _client() -> OpenAI | None:
    return OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def _facts_payload(facts: list[CandidateFact]) -> list[dict]:
    return [
        {
            "category": f.category,
            "key": f.key,
            "value": f.value,
            "commercial": f.commercial,
            "evidence": f.evidence,
        }
        for f in facts if f.active
    ]


def fallback_cover_letter(job: Job, facts: list[CandidateFact]) -> str:
    known = " ".join(f.value for f in facts[:4])
    return (
        f"Здравствуйте! Заинтересовала вакансия «{job.title}». "
        f"Мой опыт и практические навыки релевантны части требований: {known[:650]}. "
        "Буду рад обсудить задачи команды и рассказать подробнее о своём опыте."
    )[:1800]


def make_cover_letter(job: Job, facts: list[CandidateFact], resume: ResumeProfile | None = None) -> str:
    client = _client()
    if not client:
        return fallback_cover_letter(job, facts)
    prompt = f"""
Напиши короткое сопроводительное письмо на IT-вакансию.

SOURCE OF TRUTH — только эти факты кандидата:
{json.dumps(_facts_payload(facts), ensure_ascii=False)}

Выбранное резюме: {resume.name if resume else 'не выбрано'} / {resume.role if resume else ''}

Вакансия:
Название: {job.title}
Компания: {job.company}
Описание: {job.description[:12000]}

Правила:
- Никогда не придумывай работодателей, годы опыта, production/commercial опыт, сертификаты или навыки.
- commercial=false нельзя превращать в коммерческий опыт.
- 3–5 предложений, без лести и канцелярита.
- Верни только текст письма.
"""
    response = client.responses.create(model=settings.openai_model, input=prompt)
    return response.output_text.strip()[:8000]


def recruiter_reply(question: str, facts: list[CandidateFact], context: str = "") -> tuple[str, float, bool, str]:
    lowered = question.casefold()
    sensitive_markers = [
        "паспорт", "document", "bank", "банков", "инн", "снилс", "salary", "зарплат", "оклад",
        "interview", "интервью", "созвон", "meeting", "дата выхода", "start date", "offer", "оффер",
        "relocation", "релокац", "when can", "когда сможете",
    ]
    sensitive = any(x in lowered for x in sensitive_markers)
    client = _client()
    if not client:
        return "", 0.0, True, "LLM не настроен: нужен ручной ответ"
    prompt = f"""
Ты отвечаешь рекрутеру от имени кандидата.

FACTS:
{json.dumps(_facts_payload(facts), ensure_ascii=False)}

CONTEXT:
{context[:4000]}

QUESTION:
{question}

Правила:
- Используй только FACTS.
- Никогда не придумывай опыт, доступность календаря, зарплату, документы или согласие на переезд.
- commercial=false не называй коммерческим опытом.
- Если вопрос требует решения человека, requires_human=true.
- Ответ 1–4 предложения.
- Верни строго JSON: {{"reply":"...","confidence":0.0,"requires_human":true,"reason":"..."}}
"""
    response = client.responses.create(model=settings.openai_model, input=prompt)
    raw = response.output_text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        data = json.loads(raw)
        return (
            str(data.get("reply", "")).strip(),
            float(data.get("confidence", 0)),
            bool(data.get("requires_human")) or sensitive,
            str(data.get("reason", "")),
        )
    except Exception:
        return raw[:3000], 0.4, True, "Неструктурированный ответ LLM"
