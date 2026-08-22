from __future__ import annotations

import asyncio
import html
import logging
import time

from aiogram import Bot

from app.agents.llm import make_cover_letter, recruiter_reply
from app.config import settings
from app.database import repository as repo
from app.domain.jobs import NormalizedJob
from app.geo.countries import normalize_country
from app.matching.engine import score_job
from app.providers.hh import HHClient
from app.sources.adapters.hh import HHSource
from app.sources.adapters.remoteok import RemoteOKSource
from app.sources.adapters.georgia import JobsGESource, HRGESource
from app.sources.registry import build_source_plan, source_capabilities
from app.sources.base import SourceContext
from app.telegram.ui import job_keyboard, recruiter_keyboard

log = logging.getLogger(__name__)
hh_client = HHClient()
_DISCOVERY_CACHE: dict[tuple[str, tuple[str, ...]], tuple[float, list[NormalizedJob]]] = {}
CACHE_TTL_SECONDS = 600


def _cache_ttl(source_id: str) -> int:
    # Anonymous HH access is intentionally conservative: one lightweight search
    # can be cached for an hour, while other feeds remain fresher.
    if source_id == "hh" and not hh_client.private_api_available:
        return max(60, settings.hh_public_cache_minutes * 60)
    return CACHE_TTL_SECONDS


async def notify_chat(bot: Bot, chat_id: str | int, text: str, **kwargs) -> None:
    await bot.send_message(int(chat_id), text[:4096], **kwargs)


async def _user_context(user_id: int):
    user = next((u for u in await repo.list_active_users() if u.id == user_id), None)
    if not user:
        return None
    profile = await repo.active_profile(user.id)
    if not profile:
        return None
    searches = await repo.list_search_profiles(profile.id)
    if not searches:
        return None
    return user, profile, searches


async def ingest_and_match(bot: Bot, normalized: NormalizedJob, *, only_user_id: int | None = None) -> dict:
    counters = {"processed": 0, "qualified": 0, "notified": 0, "filtered": 0, "duplicate": 0}
    job, _ = await repo.upsert_job(normalized)
    src = await repo.source_ref(job.id, normalized.source)
    users = await repo.list_active_users()
    if only_user_id is not None:
        users = [u for u in users if u.id == only_user_id]

    for user in users:
        if await repo.get_state(user.id, "paused", "false") == "true":
            continue
        profile = await repo.active_profile(user.id)
        if not profile:
            continue
        facts = await repo.list_facts(profile.id)
        resumes = await repo.list_resumes(profile.id)
        searches = await repo.list_search_profiles(profile.id)
        for search in searches:
            counters["processed"] += 1
            result = score_job(job, search, facts, resumes)
            match = await repo.save_match(
                job_id=job.id,
                user_id=user.id,
                profile_id=profile.id,
                search_profile_id=search.id,
                resume_id=result.resume_id,
                technical_score=result.technical_score,
                geography_score=result.geography_score,
                salary_score=result.salary_score,
                relocation_score=result.relocation_score,
                total_score=result.total_score,
                reason=result.reason,
            )
            threshold = int((search.settings or {}).get("notify_min_score", 60))
            if result.total_score < threshold:
                counters["filtered"] += 1
                if match.status not in {"applied", "prepared", "skipped"}:
                    await repo.set_match_status(match.id, "filtered")
                continue

            counters["qualified"] += 1
            # A previously filtered vacancy can become eligible after the
            # profile/scoring rules change. Re-open it for notification.
            if match.status == "filtered":
                await repo.set_match_status(match.id, "new")
                match.status = "new"
            if match.status != "new":
                continue

            if await repo.has_notified_equivalent(user.id, job.id, job.title, job.company):
                counters["duplicate"] += 1
                await repo.set_match_status(match.id, "duplicate")
                continue

            salary = "не указана"
            if job.salary_from or job.salary_to:
                salary = f"{job.salary_from or '—'}–{job.salary_to or '—'} {job.salary_currency or ''}"
            text = (
                f"🔥 <b>{html.escape(job.title)}</b>\n"
                f"{html.escape(job.company)}\n\n"
                f"Источник: <b>{html.escape(normalized.source)}</b>\n"
                f"🌍 {html.escape(job.country or job.city or 'география не указана')}\n"
                f"💰 {html.escape(str(salary))}\n"
                f"🎯 Match: <b>{result.total_score}/100</b>\n"
                f"🧭 Режим: <b>{html.escape(result.track)}</b>\n\n"
                f"{html.escape(result.reason)}"
            )
            await notify_chat(
                bot,
                user.telegram_chat_id,
                text,
                parse_mode="HTML",
                reply_markup=job_keyboard(match.id, src.url if src else "", can_apply=source_capabilities(normalized.source).apply),
            )
            await repo.set_match_status(match.id, "notified")
            counters["notified"] += 1
    return counters


async def scan_for_user(bot: Bot, user_id: int) -> dict:
    summary = {"sources": {}, "processed": 0, "qualified": 0, "notified": 0, "filtered": 0, "duplicate": 0}
    ctx = await _user_context(user_id)
    if not ctx:
        return summary
    user, profile, searches = ctx
    if await repo.get_state(user.id, "paused", "false") == "true":
        return summary
    search = searches[0]
    settings_map = search.settings or {}
    queries = settings_map.get("queries") or [profile.target_role]
    targets = [normalize_country(str(x)) for x in (settings_map.get("target_countries") or [])]
    targets = [x for x in targets if x]
    plan = build_source_plan(user.current_country, targets, include_international=True)
    source_ids = {x.source_id for x in plan if x.implemented}
    modes = settings_map.get("modes") or {"local_ru": True, "remote_international": True, "relocation": True}
    if not modes.get("local_ru", True):
        source_ids.discard("hh")
    if not modes.get("remote_international", True):
        source_ids.discard("remoteok")
    context = SourceContext(user_id=user.id, current_country=user.current_country, target_countries=targets, queries=queries)

    adapters = []
    if "hh" in source_ids:
        adapters.append(HHSource(hh_client))
    if "remoteok" in source_ids:
        adapters.append(RemoteOKSource())
    if "jobs_ge" in source_ids:
        adapters.append(JobsGESource())
    if "hr_ge" in source_ids:
        adapters.append(HRGESource())

    for adapter in adapters:
        try:
            cache_key = (adapter.source_id, tuple(sorted(str(x).casefold() for x in queries)))
            cached = _DISCOVERY_CACHE.get(cache_key)
            cache_hit = bool(cached and time.monotonic() - cached[0] < _cache_ttl(adapter.source_id))
            if cache_hit:
                jobs = cached[1]
            else:
                jobs = await adapter.discover(context)
                _DISCOVERY_CACHE[cache_key] = (time.monotonic(), jobs)
            summary["sources"][adapter.source_id] = {"found": len(jobs), "cache": cache_hit}
            for job in jobs:
                counters = await ingest_and_match(bot, job, only_user_id=user.id)
                for key in ("processed", "qualified", "notified", "filtered", "duplicate"):
                    summary[key] += counters.get(key, 0)
        except Exception as exc:
            log.exception("source %s failed", adapter.source_id)
            summary["sources"][adapter.source_id] = {"error": str(exc)}
            await notify_chat(bot, user.telegram_chat_id, f"⚠️ Источник {adapter.name}: {html.escape(str(exc))}")
    return summary


async def scan_all(bot: Bot) -> None:
    for user in await repo.list_active_users():
        await scan_for_user(bot, user.id)


async def prepare_match(match_id: int, user_id: int) -> dict:
    match = await repo.get_match(match_id)
    if not match or match.user_id != user_id:
        raise RuntimeError("Match не найден")
    job = await repo.get_job(match.job_id)
    if not job:
        raise RuntimeError("Вакансия не найдена")
    facts = await repo.list_facts(match.profile_id)
    resumes = await repo.list_resumes(match.profile_id)
    chosen = next((r for r in resumes if r.id == match.resume_id), None)
    cover = await asyncio.to_thread(make_cover_letter, job, facts, chosen)
    refs = []
    for source_id in ("hh", "remoteok", "telegram"):
        ref = await repo.source_ref(job.id, source_id)
        if ref:
            refs.append(ref)
    source_ref = refs[0] if refs else await repo.source_ref(job.id)
    return {
        "job": job,
        "resume": chosen,
        "cover_letter": cover,
        "url": source_ref.url if source_ref else "",
        "source": source_ref.source_id if source_ref else "",
    }


async def apply_match(bot: Bot, match_id: int, user_id: int) -> dict:
    match = await repo.get_match(match_id)
    if not match or match.user_id != user_id:
        raise RuntimeError("Match не найден")
    job = await repo.get_job(match.job_id)
    if not job:
        raise RuntimeError("Вакансия не найдена")
    ref = await repo.source_ref(job.id, "hh")
    if not ref:
        raise RuntimeError("Для этой вакансии нет HH-источника с поддержкой автоотклика")
    if not hh_client.private_api_available:
        raise RuntimeError("HH private applicant API отключён; используй «Подготовить отклик» и открой вакансию на HH.")

    facts = await repo.list_facts(match.profile_id)
    resumes = await repo.list_resumes(match.profile_id)
    chosen = next((r for r in resumes if r.id == match.resume_id), None)
    hh_resume_id = (chosen.external_id if chosen and chosen.source == "hh" else None) or settings.hh_resume_id
    if not hh_resume_id:
        raise RuntimeError("Для выбранного профиля нет HH resume ID")
    cover = await asyncio.to_thread(make_cover_letter, job, facts, chosen)
    result = await hh_client.apply(ref.source_job_id, hh_resume_id, cover)
    await repo.save_application(
        user_id=user_id,
        job_id=job.id,
        source_id="hh",
        source_application_id=result.get("negotiation_id"),
        external_url=result.get("external_url"),
        resume_id=match.resume_id,
        message=cover,
        status=result.get("status", "sent"),
    )
    await repo.set_match_status(match.id, "applied")
    return result


async def scan_hh_chats(bot: Bot) -> None:
    # Current v3 MVP uses the owner's HH OAuth token. Per-user OAuth is represented
    # by SourceAccount and is the next connector layer; we never store raw tokens in Candidate Facts.
    if not hh_client.private_api_available:
        return
    owner_chat = settings.telegram_admin_chat_id.strip()
    if not owner_chat:
        return
    owner = await repo.get_user_by_chat(owner_chat)
    if not owner or await repo.get_state(owner.id, "paused", "false") == "true":
        return
    profile = await repo.active_profile(owner.id)
    if not profile:
        return
    facts = await repo.list_facts(profile.id)
    try:
        chats = await hh_client.chats(per_page=50)
    except Exception as exc:
        log.warning("HH chats failed: %s", exc)
        return
    for chat in chats.get("items", []):
        if int(chat.get("unread_message_count") or 0) <= 0:
            continue
        chat_id = str(chat.get("id", ""))
        payload = await hh_client.chat_messages(chat_id)
        for msg in sorted(payload.get("messages", []), key=lambda x: x.get("creation_time", "")):
            msg_id = str(msg.get("id", ""))
            sender = msg.get("sender_display_info") or {}
            if not msg_id or sender.get("is_current_participant") is True:
                continue
            if await repo.message_seen(owner.id, msg_id, "hh_chat"):
                continue
            text = ((msg.get("payload") or {}).get("text") or "").strip()
            await repo.mark_message_seen(owner.id, msg_id, chat_id, text or "[non-text]", "hh_chat")
            if not text:
                await notify_chat(bot, owner.telegram_chat_id, "⚠️ В HH пришло интерактивное/нетекстовое сообщение. Проверь чат вручную.")
                continue
            draft, confidence, human, reason = await asyncio.to_thread(recruiter_reply, text, facts, (payload.get("display") or {}).get("title", ""))
            await repo.set_state(owner.id, f"draft:{chat_id}:{msg_id}", draft)
            if settings.auto_reply and draft and confidence >= settings.auto_reply_min_confidence and not human:
                await hh_client.send_chat_message(chat_id, draft)
                continue
            shown = draft or "Нужен ручной ответ"
            await notify_chat(
                bot,
                owner.telegram_chat_id,
                f"💬 <b>HH сообщение</b>\n\n{html.escape(text)}\n\n<b>Черновик:</b>\n{html.escape(shown)}\n\nConfidence: {confidence:.0%}\n{html.escape(reason)}",
                parse_mode="HTML",
                reply_markup=recruiter_keyboard(chat_id, msg_id),
            )
