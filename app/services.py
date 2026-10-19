from __future__ import annotations

import asyncio
import html
import json
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from aiogram import Bot
import httpx

from app.agents.llm import make_cover_letter, recruiter_reply
from app.config import settings
from app.database import repository as repo
from app.database import notification_delivery as delivery_repo
from app.database.db import user_scan_lease
from app.domain.application_package import snapshot_vacancy
from app.domain.jobs import NormalizedJob
from app.domain.job_text import clean_html_text, format_salary
from app.domain.source_posting import posting_snapshot_digest, source_posting_view
from app.domain.vacancy_availability import publication_age_bucket
from app.geo.countries import normalize_country
from app.matching.engine import MATCH_ASSESSMENT_VERSION, score_job
from app.matching.fact_comparison import compare_facts
from app.matching.language_fit import compare_english_level
from app.matching.resume_diff import compare_resume_coverage
from app.providers.hh import HHClient, HHError
from app.sources.adapters.hh import HHSource
from app.sources.adapters.remoteok import RemoteOKSource
from app.sources.adapters.himalayas import HimalayasSource
from app.sources.adapters.remotive import RemotiveSource
from app.sources.adapters.arbeitnow import ArbeitnowSource
from app.sources.adapters.jobbank import JobBankSource
from app.sources.adapters.eures import EuresSource
from app.sources.adapters.greenhouse import GreenhouseSource
from app.sources.adapters.lever import LeverSource
from app.sources.adapters.smartrecruiters import SmartRecruitersSource
from app.sources.adapters.georgia import JobsGESource, HRGESource
from app.sources.adapters.employer_career_watch import EmployerCareerWatchSource
from app.sources.registry import build_source_plan, source_capabilities
from app.sources.base import SourceContext
from app.sources.network_errors import TRANSPORT_ERROR_TYPES, transport_failure_category
from app.search.source_summary import aggregate_source, normalize_attempt, scan_outcome
from app.sources.diagnostics import classify_source_error, diagnostic
from app.sources.notice_policy import (
    STATE_KEY as SOURCE_NOTICE_STATE_KEY,
    plan_source_notices,
    render_source_state_notice,
)
from app.search.preferences import discovery_queries, job_priority, source_enabled, source_priority, vacancy_allowed, vacancy_exclusion_reason
from app.telegram.ui import job_keyboard, recruiter_keyboard

log = logging.getLogger(__name__)


def _versioned_assessment(result) -> dict:
    scores = getattr(result, "recommendation_scores", {})
    versioned = dict(scores) if isinstance(scores, dict) else {}
    versioned["_meta"] = {"match_assessment_version": MATCH_ASSESSMENT_VERSION}
    return versioned
hh_client = HHClient()
_DISCOVERY_CACHE: dict[
    tuple[str, tuple[str, ...], str | None, tuple[str, ...]],
    tuple,
] = {}
CACHE_TTL_SECONDS = 600
GEORGIA_CACHE_TTL_SECONDS = 6 * 60 * 60
HIMALAYAS_CACHE_TTL_SECONDS = 24 * 60 * 60
REMOTIVE_CACHE_TTL_SECONDS = 24 * 60 * 60
LEVER_CACHE_TTL_SECONDS = 6 * 60 * 60
DISCOVERY_CONCURRENCY = 3
DISCOVERY_TIMEOUT_SECONDS = 180
HH_CONNECT_RECHECK_SECONDS = 15 * 60
_HH_CONNECT_RETRY_AFTER = 0.0
_HH_DISCOVERY_LOCK = asyncio.Lock()
# v3 forces one refresh after switching from the ignored API filter to RSS.
REMOTIVE_STATE_KEY = "source_cache.remotive.v3"
_REMOTIVE_PAYLOAD_CACHE: tuple[float, dict] | None = None
_REMOTIVE_PAYLOAD_LOCK = asyncio.Lock()
_SOURCE_REF_PREFERENCE = ("hh", "remoteok", "himalayas", "arbeitnow", "telegram", "jobs_ge", "hr_ge")


async def _discover_hh(adapter: HHSource, context: SourceContext) -> list[NormalizedJob] | None:
    """Serialize outage probes and discard stale HH results after connection failure."""
    global _HH_CONNECT_RETRY_AFTER
    async with _HH_DISCOVERY_LOCK:
        if time.monotonic() < _HH_CONNECT_RETRY_AFTER:
            return None
        try:
            jobs = await adapter.discover(context)
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            _HH_CONNECT_RETRY_AFTER = time.monotonic() + HH_CONNECT_RECHECK_SECONDS
            for key in list(_DISCOVERY_CACHE):
                if key[0] == "hh":
                    del _DISCOVERY_CACHE[key]
            log.warning("source hh connection failed (category=%s); skipping for %d seconds",
                        transport_failure_category(exc), HH_CONNECT_RECHECK_SECONDS)
            raise
        _HH_CONNECT_RETRY_AFTER = 0.0
        return jobs


def _aggregate_source(sources: dict, source_id: str, info: dict) -> None:
    aggregate_source(sources, source_id, info)


def _cache_ttl(source_id: str) -> int:
    if source_id == "himalayas":
        # The provider refreshes this API daily; repeated scans add no freshness.
        return HIMALAYAS_CACHE_TTL_SECONDS
    if source_id == "remotive":
        # Remotive recommends at most four requests per day; refresh once daily.
        return REMOTIVE_CACHE_TTL_SECONDS
    if source_id in {"lever", "smartrecruiters"}:
        # The curated employer board is refreshed periodically; avoid polling
        # it on every manual or scheduled scan.
        return LEVER_CACHE_TTL_SECONDS
    if source_id in {"jobs_ge", "hr_ge"}:
        # Public Georgia boards are refreshed less often by scheduled scans.
        # A user-triggered /scan still explicitly requests a fresh discovery.
        return GEORGIA_CACHE_TTL_SECONDS
    # Anonymous HH access is intentionally conservative: one lightweight search
    # can be cached for an hour, while other feeds remain fresher.
    if source_id == "hh" and not hh_client.private_api_available:
        return max(60, settings.hh_public_cache_minutes * 60)
    return CACHE_TTL_SECONDS


def _fresh_remotive_payload(value: str, *, now: datetime) -> tuple[float, dict] | None:
    """Return the persisted response's age and payload without renewing its TTL."""
    try:
        cached = json.loads(value)
        fetched_at = datetime.fromisoformat(str(cached.get("fetched_at") or ""))
        payload = cached.get("payload")
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=UTC)
        age = (now - fetched_at.astimezone(UTC)).total_seconds()
        if age < 0 or age >= REMOTIVE_CACHE_TTL_SECONDS or not isinstance(payload, dict):
            return None
        return age, payload
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError):
        return None


async def _discover_remotive(
    adapter: RemotiveSource, context: SourceContext
) -> tuple[list[NormalizedJob], bool, float]:
    """Share and persist Remotive's daily response across profiles and restarts."""
    global _REMOTIVE_PAYLOAD_CACHE
    async with _REMOTIVE_PAYLOAD_LOCK:
        now_mono = time.monotonic()
        in_memory = _REMOTIVE_PAYLOAD_CACHE
        if in_memory and now_mono - in_memory[0] < REMOTIVE_CACHE_TTL_SECONDS:
            return adapter.parse_payload(in_memory[1], context), True, in_memory[0]

        cache_owner_id = context.user_id
        try:
            active_users = await repo.list_active_users()
            active_ids = [int(user.id) for user in active_users]
            if active_ids:
                cache_owner_id = min(active_ids)
        except Exception:
            log.warning("could not determine shared Remotive cache owner", exc_info=True)

        try:
            stored = await repo.get_state(cache_owner_id, REMOTIVE_STATE_KEY, "")
        except Exception:
            log.warning("could not read persisted Remotive cache", exc_info=True)
            stored = ""
        persisted = _fresh_remotive_payload(stored, now=datetime.now(UTC))
        if persisted is not None:
            age, payload = persisted
            # Reconstruct the original fetch time on the monotonic clock so
            # restarting near expiry does not grant another full day.
            fetched_mono = time.monotonic() - age
            _REMOTIVE_PAYLOAD_CACHE = (fetched_mono, payload)
            return adapter.parse_payload(payload, context), True, fetched_mono

        payload = await adapter.fetch_payload()
        fetched_at = datetime.now(UTC)
        fetched_mono = time.monotonic()
        _REMOTIVE_PAYLOAD_CACHE = (fetched_mono, payload)
        try:
            await repo.set_state(
                cache_owner_id,
                REMOTIVE_STATE_KEY,
                json.dumps({"fetched_at": fetched_at.isoformat(), "payload": payload}, separators=(",", ":")),
            )
        except Exception:
            # Keep the in-process throttle even if persistence is temporarily unavailable.
            log.warning("could not persist Remotive cache", exc_info=True)
        return adapter.parse_payload(payload, context), False, fetched_mono


async def notify_chat(bot: Bot, chat_id: str | int, text: str, **kwargs):
    return await bot.send_message(int(chat_id), text[:4096], **kwargs)


async def _send_claimed_job_alert(bot: Bot, claim: dict) -> bool:
    """Retry the frozen message even when its original source no longer responds."""
    payload = claim["payload"]
    delivered = False
    try:
        response = await notify_chat(
            bot, claim["chat_id"], payload["text"], parse_mode="HTML",
            reply_markup=job_keyboard(
                claim["match_id"], payload.get("url") or "",
                can_apply=bool(payload.get("can_apply")),
                job_id=payload.get("job_id"),
            ),
        )
        delivered = True
        message_id = getattr(response, "message_id", None)
        ok = await delivery_repo.settle_job_notification(
            user_id=claim["user_id"], match_id=claim["match_id"],
            token=claim["token"], delivered=True,
            message_id=message_id if isinstance(message_id, int) else None,
        )
        if not ok:
            log.warning("job notification claim was superseded before finalization")
        return bool(ok)
    except Exception as exc:
        # If DB confirmation fails *after* Telegram succeeds, preserve the
        # in-flight lease. Its expiry allows an at-least-once retry.
        if not delivered:
            try:
                await delivery_repo.settle_job_notification(
                    user_id=claim["user_id"], match_id=claim["match_id"],
                    token=claim["token"], delivered=False,
                )
            except Exception:
                log.warning("cannot persist failed job notification; lease will expire")
        log.warning("job notification delivery incomplete (%s)", type(exc).__name__)
        return False


async def retry_job_notifications(bot: Bot) -> None:
    """Retry due journal entries independently of source discovery and scans."""
    try:
        due = await delivery_repo.due_job_notifications(limit=100)
    except Exception as exc:
        log.warning("job notification retry scan failed (%s)", type(exc).__name__)
        return
    for user_id, match_id in due:
        try:
            if await repo.get_state(user_id, "paused", "false") == "true":
                continue
            claim = await delivery_repo.claim_job_notification(
                user_id=user_id, match_id=match_id,
            )
            if claim:
                await _send_claimed_job_alert(bot, claim)
        except Exception as exc:
            # A broken individual notification must not starve other jobs.
            log.warning("individual job notification retry failed (%s)", type(exc).__name__)


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


def _can_reach_threshold_with_technical(result, threshold: int) -> bool:
    possible_gain = ((100 - result.technical_score) * 48 + 99) // 100
    return result.total_score + possible_gain >= threshold


def _match_lane(result, threshold: int) -> str:
    fit = getattr(result, "fit", "good")
    if fit == "skip" or result.total_score < threshold:
        return "filtered"
    if fit == "stretch":
        return "stretch"
    return "qualified"


def _scoring_exclusion_reason(result, threshold: int) -> str | None:
    """Explain a filtered result from structured scores without parsing prose."""
    if getattr(result, "fit", "good") == "skip":
        return "fit_skip"
    if result.total_score >= threshold:
        return None
    weights = {
        "technical_gap": (100 - result.technical_score) * 48,
        "geography_gap": (100 - result.geography_score) * 27,
        "salary_gap": (100 - result.salary_score) * 12,
        "relocation_gap": (100 - result.relocation_score) * 13,
    }
    weighted_total = round(
        result.technical_score * 0.48
        + result.geography_score * 0.27
        + result.salary_score * 0.12
        + result.relocation_score * 0.13
    )
    if weighted_total >= threshold:
        return "score_cap_or_risk"
    return max(weights, key=weights.get)

async def ingest_and_match(
    bot: Bot,
    normalized: NormalizedJob,
    *,
    only_user_id: int | None = None,
    only_search_profile_id: int | None = None,
) -> dict:
    counters = {"processed": 0, "qualified": 0, "stretch": 0, "notified": 0, "filtered": 0, "duplicate": 0,
                "scoring_exclusion_reasons": {}}
    job, _ = await repo.upsert_job(normalized)
    src = await repo.source_ref(
        job.id, normalized.source, source_job_id=normalized.source_job_id
    )
    job = source_posting_view(job, src)
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
        if only_search_profile_id is not None:
            searches = [item for item in searches if item.id == only_search_profile_id]
        for search in searches:
            counters["processed"] += 1
            result = score_job(job, search, facts, resumes)
            threshold = int((search.settings or {}).get("notify_min_score", 60))

            if normalized.source == "hh":
                if _can_reach_threshold_with_technical(result, threshold):
                    try:
                        details = await get_cached_hh_details(
                            job.id, source_job_id=normalized.source_job_id
                        )
                    except HHError:
                        details = {}
                    technical_text = str(details.get("description") or "")
                    if technical_text:
                        result = score_job(
                            job,
                            search,
                            facts,
                            resumes,
                            technical_text=technical_text,
                        )

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
                recommendation_scores=_versioned_assessment(result),
                total_score=result.total_score,
                reason=result.reason,
            )
            lane = _match_lane(result, threshold)
            if lane == "filtered":
                counters["filtered"] += 1
                reason = _scoring_exclusion_reason(result, threshold) or "score_cap_or_risk"
                reasons = counters["scoring_exclusion_reasons"]
                reasons[reason] = reasons.get(reason, 0) + 1
                if match.status not in {"applied", "prepared", "skipped", "saved"}:
                    await repo.set_match_status(match.id, "filtered")
                continue

            if lane == "stretch":
                counters["stretch"] += 1
                if match.status not in {"applied", "prepared", "skipped", "saved", "stretch"}:
                    await repo.set_match_status(match.id, "stretch")
                continue

            counters["qualified"] += 1
            # A previously filtered vacancy can become eligible after the
            # profile/scoring rules change. Re-open it for notification.
            if match.status in {"filtered", "stretch"}:
                await repo.set_match_status(match.id, "new")
                match.status = "new"
            if match.status != "new":
                continue

            if await repo.has_notified_equivalent(
                user.id, job.id, job.title, job.company, match_id=match.id,
            ):
                counters["duplicate"] += 1
                await repo.set_match_status(match.id, "duplicate")
                continue

            salary = format_salary(
                job.salary_from,
                job.salary_to,
                job.salary_currency,
                period=job.salary_period,
                fallback_text=str(
                    (normalized.raw or {}).get("salary_text")
                    or (normalized.raw or {}).get("card_text")
                    or ""
                ),
            )
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
            # Persist original observed content before network delivery.
            # A concurrent scan and scheduled retry cannot claim the same
            # vacancy while the lease is active.
            claim = await delivery_repo.claim_job_notification(
                user_id=user.id, match_id=match.id,
                payload={
                    "match_id": match.id, "job_id": job.id, "text": text,
                    "url": src.url if src else "",
                    "can_apply": source_capabilities(normalized.source).apply,
                },
            )
            if claim and await _send_claimed_job_alert(bot, claim):
                counters["notified"] += 1
    return counters


def _error_text(exc: Exception) -> str:
    """Compatibility helper: controlled diagnostic code, never exception text."""
    return classify_source_error(exc)["code"]


class ScanAlreadyRunning(RuntimeError):
    """A scan for this user holds the shared PostgreSQL lease."""


async def coordinated_scan_for_user(
    bot: Bot, user_id: int, progress_callback=None, *, force_refresh: bool = False,
    on_start: Callable[[], Awaitable[None]] | None = None,
) -> dict:
    async with user_scan_lease(user_id) as acquired:
        if not acquired:
            raise ScanAlreadyRunning("A scan is already running for this user")
        if on_start:
            await on_start()
        return await scan_for_user(bot, user_id, progress_callback, force_refresh=force_refresh)


async def scan_for_user(bot: Bot, user_id: int, progress_callback=None, *, force_refresh: bool = False) -> dict:
    summary = {"sources": {}, "searches": {}, "processed": 0, "qualified": 0, "stretch": 0, "notified": 0, "filtered": 0, "duplicate": 0}
    async def emit_progress(text: str) -> None:
        if not progress_callback:
            return
        try:
            await progress_callback(text)
        except Exception as exc:
            log.warning("scan progress update failed (%s)", type(exc).__name__)

    ctx = await _user_context(user_id)
    if not ctx:
        return summary
    user, profile, searches = ctx
    if await repo.get_state(user.id, "paused", "false") == "true":
        return summary
    for search in searches:
        settings_map = search.settings or {}
        queries = discovery_queries(settings_map, profile.target_role)
        targets = [normalize_country(str(x)) for x in (settings_map.get("target_countries") or [])]
        targets = [x for x in targets if x]
        plan = build_source_plan(user.current_country, targets, include_international=True)
        source_ids = {
            x.source_id for x in plan
            if x.implemented and getattr(x, "available", True) and source_enabled(settings_map, x.source_id)
        }
        modes = settings_map.get("modes") or {"local_ru": True, "remote_international": True, "relocation": True}
        if not modes.get("local_ru", True):
            source_ids.discard("hh")
        if not modes.get("remote_international", True):
            source_ids.discard("remoteok")
            source_ids.discard("himalayas")
            source_ids.discard("remotive")
        if not modes.get("relocation", True):
            source_ids.discard("jobbank")
            source_ids.discard("eures")
        context = SourceContext(user_id=user.id, current_country=user.current_country,
                                target_countries=targets, queries=queries, force_refresh=force_refresh)
        search_summary = {"name": search.name, "sources": {}, "discovered": 0,
                          "preference_filtered": 0, "processed": 0, "qualified": 0,
                          "stretch": 0, "notified": 0, "filtered": 0, "duplicate": 0,
                          "preference_exclusion_reasons": {}, "scoring_exclusion_reasons": {}}
        summary["searches"][str(search.id)] = search_summary

        adapters = []
        if "hh" in source_ids:
            adapters.append(HHSource(hh_client))
        if "remoteok" in source_ids:
            adapters.append(RemoteOKSource())
        if "himalayas" in source_ids:
            adapters.append(HimalayasSource())
        if "remotive" in source_ids:
            adapters.append(RemotiveSource())
        if "arbeitnow" in source_ids:
            adapters.append(ArbeitnowSource())
        if "jobbank" in source_ids:
            adapters.append(JobBankSource())
        if "eures" in source_ids:
            adapters.append(EuresSource())
        if "greenhouse" in source_ids:
            adapters.append(GreenhouseSource())
        if "lever" in source_ids:
            adapters.append(LeverSource())
        if "smartrecruiters" in source_ids:
            adapters.append(SmartRecruitersSource())
        if "jobs_ge" in source_ids:
            adapters.append(JobsGESource())
        if "hr_ge" in source_ids:
            adapters.append(HRGESource())
        if "employer_career_watch" in source_ids:
            adapters.append(EmployerCareerWatchSource())
        adapters.sort(key=lambda item: source_priority(settings_map, item.source_id), reverse=True)

        semaphore = asyncio.Semaphore(DISCOVERY_CONCURRENCY)

        async def discover(adapter):
            if adapter.source_id == "hh" and time.monotonic() < _HH_CONNECT_RETRY_AFTER:
                return adapter, [], False, None, 0, True
            cache_key = (
                adapter.source_id,
                tuple(sorted(str(x).casefold() for x in queries)),
                normalize_country(str(context.current_country or "")),
                tuple(sorted(
                    country
                    for value in (context.target_countries or [])
                    if (country := normalize_country(str(value or "")))
                )),
            )
            cached = _DISCOVERY_CACHE.get(cache_key)
            cache_hit = bool(
                cached
                and time.monotonic() - cached[0] < _cache_ttl(adapter.source_id)
                and (not force_refresh or adapter.source_id in {"himalayas", "remotive"})
            )
            if cache_hit:
                adapter.discovery_observation = cached[3] if len(cached) > 3 else str(cached[0])
                adapter.discovery_diagnostics = cached[4] if len(cached) > 4 else []
                adapter.partial_failures = cached[2] if len(cached) > 2 else 0
                if adapter.source_id == "eures":
                    adapter.partial_failures = cached[2] if len(cached) > 2 else 0
                    adapter.partial_failure_observation = cached[3] if len(cached) > 3 else str(cached[0])
                return adapter, cached[1], True, None, 0, False
            started = time.monotonic()
            observation_id = str(time.monotonic_ns())
            adapter.discovery_observation = observation_id
            if adapter.source_id == "eures":
                adapter.partial_failure_observation = observation_id
            try:
                async with semaphore:
                    if adapter.source_id == "remotive":
                        jobs, source_cache_hit, fetched_mono = await asyncio.wait_for(
                            _discover_remotive(adapter, context), timeout=DISCOVERY_TIMEOUT_SECONDS
                        )
                    elif adapter.source_id == "hh":
                        jobs = await asyncio.wait_for(_discover_hh(adapter, context), timeout=DISCOVERY_TIMEOUT_SECONDS)
                        if jobs is None:
                            return adapter, [], False, None, int((time.monotonic() - started) * 1000), True
                        source_cache_hit = False
                        fetched_mono = time.monotonic()
                    else:
                        jobs = await asyncio.wait_for(adapter.discover(context), timeout=DISCOVERY_TIMEOUT_SECONDS)
                        source_cache_hit = False
                        fetched_mono = time.monotonic()
                # A context-specific projection must expire with its provider
                # response, including when that response came from disk.
                partial_failures = int(getattr(adapter, "partial_failures", 0) or 0)
                _DISCOVERY_CACHE[cache_key] = (fetched_mono, jobs, partial_failures, observation_id, list(getattr(adapter, "discovery_diagnostics", [])))
                return adapter, jobs, source_cache_hit, None, int((time.monotonic() - started) * 1000), False
            except Exception as exc:
                return adapter, [], False, exc, int((time.monotonic() - started) * 1000), False

        for adapter in adapters:
            await emit_progress(f"⏳ {search.name} · {adapter.name}: подготовка поиска…")

        discovered = await asyncio.gather(*(discover(adapter) for adapter in adapters))
        for adapter, jobs, cache_hit, discovery_error, duration_ms, skipped in discovered:
            attempt_observation = str(time.monotonic_ns())
            observation = getattr(adapter, "discovery_observation", None) or attempt_observation
            info = {"name": adapter.name, "profile_id": search.id, "profile_name": search.name,
                    "found": 0, "duration_ms": duration_ms, "cache": cache_hit,
                    "retry": 0 if cache_hit else int(getattr(adapter, "retry_count", 0)),
                    "fallback": 0 if cache_hit else int(getattr(adapter, "fallback_count", 0)),
                    "diagnostics": []}
            partial_failures = int(getattr(adapter, "partial_failures", 0) or 0)
            if partial_failures:
                info.update(partial_failures=partial_failures, partial_failure_observations={observation: partial_failures})
            def add_error(item):
                for previous in info["diagnostics"]:
                    if all(previous.get(key) == item.get(key) for key in ("code", "stage", "action", "operation")):
                        previous["count"] += item.get("count", 1)
                        return
                info["diagnostics"].append({**item, "profiles": [search.name], "observation_id": attempt_observation if item["stage"] in {"processing", "summary"} else observation})

            silent_hh = adapter.source_id == "hh" and isinstance(discovery_error, httpx.ConnectError)
            if skipped or silent_hh:
                info["status"] = "failed" if silent_hh else "skipped"
                for prior in getattr(adapter, "discovery_diagnostics", []):
                    add_error(prior)
                item = (classify_source_error(discovery_error, action="cooldown") if discovery_error
                        else diagnostic("SOURCE_CONNECTION_COOLDOWN", action="cooldown"))
                add_error(item)
                if discovery_error:
                    info["failure_category"] = transport_failure_category(discovery_error)
            elif discovery_error:
                info["status"] = "failed"
                for item in getattr(adapter, "discovery_diagnostics", []):
                    add_error(item)
                fatal = classify_source_error(discovery_error)
                if not any(item["code"] == fatal["code"] and item["stage"] == fatal["stage"] and item["action"] != "fallback" for item in info["diagnostics"]):
                    add_error(fatal)
                log.error("source %s failed for search %s (%s; category=%s)",
                          adapter.source_id, search.id, type(discovery_error).__name__, transport_failure_category(discovery_error))
            else:
                info["status"] = "success"
                partial_failures = int(getattr(adapter, "partial_failures", 0) or 0)
                if partial_failures:
                    info.update(status="partial", partial_failures=partial_failures,
                                partial_failure_observations={observation: partial_failures})
                for item in getattr(adapter, "discovery_diagnostics", []):
                    add_error(item)
                if partial_failures and not info["diagnostics"]:
                    add_error(diagnostic("SOURCE_PARTIAL_RESULTS", action="continue_partial", count=partial_failures))
                # Isolate malformed jobs before scoring; valid jobs from the same
                # response must still be processed and retained.
                info["discovered"] = len(jobs)
                info["preference_filtered"] = 0
                info["preference_exclusion_reasons"] = {}
                eligible = []
                processing_errors = 0
                for job in jobs:
                    try:
                        if vacancy_allowed(job, settings_map, current_country=user.current_country):
                            eligible.append((job_priority(job, settings_map, current_country=user.current_country), job))
                        else:
                            info["preference_filtered"] += 1
                            reason = vacancy_exclusion_reason(
                                job, settings_map, current_country=user.current_country,
                            ) or "other_settings"
                            reasons = info["preference_exclusion_reasons"]
                            reasons[reason] = reasons.get(reason, 0) + 1
                    except Exception as exc:
                        processing_errors += 1
                        add_error(classify_source_error(exc, stage="processing", action="continue_partial"))
                eligible.sort(key=lambda pair: pair[0], reverse=True)
                jobs = [job for _, job in eligible]
                info["found"] = len(jobs)
                info["publication_date_provided"] = sum(
                    bool(str(getattr(job, "published_at", "") or "").strip()) for job in jobs
                )
                info["publication_date_missing"] = len(jobs) - info["publication_date_provided"]
                age_buckets = {
                    "fresh_7d": "publication_age_0_7d",
                    "age_8_30d": "publication_age_8_30d",
                    "older_30d": "publication_age_over_30d",
                    "unknown": "publication_age_unknown",
                }
                freshness_now = datetime.now(UTC)
                for job in jobs:
                    bucket = publication_age_bucket(
                        getattr(job, "published_at", None), now=freshness_now,
                    )
                    key = age_buckets[bucket]
                    info[key] = info.get(key, 0) + 1
                cache_label = " (кэш)" if cache_hit else ""
                await emit_progress(f"⏳ {search.name} · {adapter.name}: найдено {len(jobs)}{cache_label} · {duration_ms / 1000:.1f} с")
                for index, job in enumerate(jobs, start=1):
                    try:
                        counters = await ingest_and_match(bot, job, only_user_id=user.id, only_search_profile_id=search.id)
                    except Exception as exc:
                        processing_errors += 1
                        add_error(classify_source_error(exc, stage="processing", action="continue_partial"))
                        log.error("source %s vacancy processing failed for search %s (%s)", adapter.source_id, search.id, type(exc).__name__)
                        continue
                    for key in ("processed", "qualified", "stretch", "notified", "filtered", "duplicate"):
                        value = counters.get(key, 0)
                        summary[key] += value
                        search_summary[key] += value
                        info[key] = info.get(key, 0) + value
                    for reason, count in counters.get("scoring_exclusion_reasons", {}).items():
                        scoring_reasons = info.setdefault("scoring_exclusion_reasons", {})
                        scoring_reasons[reason] = scoring_reasons.get(reason, 0) + int(count)
                    if index % 5 == 0 or index == len(jobs):
                        await emit_progress(f"⏳ {search.name} · {adapter.name}: найдено {len(jobs)}{cache_label} · анализ {index}/{len(jobs)}")
                if processing_errors:
                    info.update(status="partial", processing_errors=processing_errors)
            info = normalize_attempt(info)
            search_summary["discovered"] += info.get("discovered", 0)
            search_summary["preference_filtered"] += info.get("preference_filtered", 0)
            for key in ("preference_exclusion_reasons", "scoring_exclusion_reasons"):
                totals = search_summary[key]
                for reason, count in info.get(key, {}).items():
                    totals[reason] = totals.get(reason, 0) + int(count)
            search_summary["sources"][adapter.source_id] = info
            # Summary errors belong to application telemetry, not the provider.
            try:
                _aggregate_source(summary["sources"], adapter.source_id, info)
            except Exception as exc:
                info["diagnostics"].append({**classify_source_error(exc, stage="summary"), "profiles": [search.name], "observation_id": attempt_observation})
                if info["status"] == "success":
                    info["status"] = "partial"
                rebuilt = {}
                for entry in summary["searches"].values():
                    if adapter.source_id in entry["sources"]:
                        aggregate_source(rebuilt, adapter.source_id, entry["sources"][adapter.source_id])
                summary["sources"][adapter.source_id] = rebuilt[adapter.source_id]
                log.error("source summary reconstruction for %s (%s)", adapter.source_id, type(exc).__name__)
    # Persist the technical state before Telegram I/O. Detailed per-attempt
    # diagnostics remain in the scan dashboard; chat receives only transitions
    # and bounded repeat summaries, never one message per profile/attempt.
    try:
        previous_notice_state = await repo.get_state(user.id, SOURCE_NOTICE_STATE_KEY, "")
        source_notices, next_notice_state = plan_source_notices(
            summary["sources"], previous_notice_state,
        )
        await repo.set_state(user.id, SOURCE_NOTICE_STATE_KEY, next_notice_state)
    except Exception as exc:
        source_notices = []
        log.error("source notification state persistence failed (%s)", type(exc).__name__)
    for event in source_notices:
        info = summary["sources"].get(event["source_id"], {})
        try:
            await notify_chat(
                bot,
                user.telegram_chat_id,
                render_source_state_notice(event, info),
                parse_mode=None,
            )
        except Exception as exc:
            log.error("source diagnostic notification failed (%s)", type(exc).__name__)
    return summary


async def scan_all(bot: Bot) -> None:
    for user in await repo.list_active_users():
        started = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        state = {"kind": "scheduled", "started_at": started}
        try:
            try:
                summary = await coordinated_scan_for_user(bot, user.id)
            except ScanAlreadyRunning:
                state.update(status="skipped", stage="Другой поиск уже выполняется")
            else:
                outcome = scan_outcome(summary)
                state.update(status=outcome, stage="Готово" if outcome == "completed" else "Завершено с неполными результатами", summary=summary)
        except Exception as exc:
            issue = classify_source_error(exc, stage="scan")
            state.update(status="failed", stage=issue["code"], diagnostic=issue)
            log.error("scheduled scan failed for user %s (%s); continuing", user.id, type(exc).__name__)
        state["finished_at"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        try:
            # A separate state key cannot replace an active manual dashboard.
            await repo.set_state(user.id, "scheduled_scan_dashboard", json.dumps(state, ensure_ascii=False))
        except Exception as exc:
            log.error("scheduled diagnostic persistence failed for user %s (%s); continuing", user.id, type(exc).__name__)


async def refresh_match_score(match, job, *, technical_text: str = ""):
    facts = await repo.list_facts(match.profile_id)
    resumes = await repo.list_resumes(match.profile_id)
    searches = await repo.list_search_profiles(match.profile_id)

    search = next(
        (item for item in searches if item.id == match.search_profile_id),
        None,
    )
    if not search:
        return match

    result = score_job(
        job,
        search,
        facts,
        resumes,
        technical_text=technical_text or None,
    )

    return await repo.save_match(
        job_id=job.id,
        user_id=match.user_id,
        profile_id=match.profile_id,
        search_profile_id=match.search_profile_id,
        resume_id=result.resume_id,
        technical_score=result.technical_score,
        geography_score=result.geography_score,
        salary_score=result.salary_score,
        relocation_score=result.relocation_score,
        recommendation_scores=_versioned_assessment(result),
        total_score=result.total_score,
        reason=result.reason,
    )


async def get_cached_hh_details(job_id: int, *, source_job_id: str | None = None) -> dict:
    ref = await repo.source_ref(
        job_id, "hh", **({"source_job_id": source_job_id} if source_job_id is not None else {})
    )
    if not ref:
        return {}

    raw = dict(ref.raw or {})
    cached = raw.get("details_cache_v1")
    posting_digest = posting_snapshot_digest(raw.get("normalized_posting_v1"))
    cache_digest = raw.get("details_cache_posting_digest_v1")
    # A versioned posting must never reuse unversioned (legacy) details.
    # For legacy refs without a posting snapshot, continue supporting legacy cache.
    if isinstance(cached, dict) and cache_digest == posting_digest:
        return dict(cached)

    vacancy_html = await hh_client.vacancy_web(ref.source_job_id)
    details = HHSource.parse_vacancy_web_html(vacancy_html)
    if not isinstance(details, dict):
        details = {}

    saved = await repo.save_source_ref_detail_cache(
        ref.id, details, expected_posting_digest=posting_digest
    )
    if saved is False:
        # A newer observation replaced this source posting mid-fetch. Never
        # score or show its stale network response as current verified detail.
        return {}
    return dict(details)


async def get_vacancy_details(
    user_id: int, job_id: int, *, search_profile_id: int | None = None
) -> dict:
    match = await repo.get_match_for_user_job(
        user_id, job_id, **({"search_profile_id": search_profile_id} if search_profile_id is not None else {})
    )
    if not match:
        raise RuntimeError("Вакансия не найдена среди твоих совпадений")
    job = await repo.get_job(job_id)
    if not job:
        raise RuntimeError("Вакансия не найдена")

    ref = None
    for source_id in _SOURCE_REF_PREFERENCE:
        ref = await repo.source_ref(job.id, source_id)
        if ref:
            break
    if not ref:
        ref = await repo.source_ref(job.id)
    job = source_posting_view(job, ref)

    details: dict = {}
    warning = ""
    if ref and ref.source_id == "hh":
        try:
            details = await get_cached_hh_details(job.id)
        except HHError as exc:
            warning = str(exc)

    if not details.get("description"):
        details["description"] = clean_html_text(job.description)

    technical_text = clean_html_text(
        str(details.get("description") or job.description or "")
    )
    match = await refresh_match_score(
        match,
        job,
        technical_text=technical_text,
    )

    raw = (ref.raw or {}) if ref else {}
    relocation_evidence = raw.get("relocation_evidence_v1")
    source_salary_text = raw.get("source_salary_text")
    if isinstance(source_salary_text, str) and source_salary_text.strip():
        # Display-only source evidence: never send decimal/hourly or ambiguous
        # amounts through the legacy HH numeric salary fallback.
        details["source_salary_text"] = source_salary_text[:2000]
    if isinstance(raw.get("availability"), dict):
        details["availability"] = dict(raw["availability"])
    applicant_count = raw.get("applicant_count_v1")
    if isinstance(applicant_count, dict):
        value = applicant_count.get("value")
        kind = applicant_count.get("kind")
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0 and kind == "applications":
            details["applicant_count"] = value
            details["applicant_count_source"] = str(
                applicant_count.get("source_url") or applicant_count.get("source_id") or (ref.source_id if ref else "")
            )[:600]
            details["applicant_count_observed_at"] = str(applicant_count.get("observed_at") or "")[:40]
    if ref and ref.source_id == "himalayas":
        timezone_restrictions = raw.get("timezone_restrictions")
        if isinstance(timezone_restrictions, list):
            known_timezones = [
                value.strip()
                for value in timezone_restrictions
                if isinstance(value, str) and value.strip()
            ]
            if known_timezones:
                details["timezone_restrictions"] = known_timezones
    fallback_salary_text = str(raw.get("salary_text") or raw.get("card_text") or "")
    searches = await repo.list_search_profiles(match.profile_id)
    search = next((item for item in searches if item.id == match.search_profile_id), None)
    source_first_seen = getattr(ref, "first_seen_at", None) if ref else None
    if isinstance(source_first_seen, datetime):
        # Database timestamps use naive UTC for compatibility with the current
        # schema; expose an explicit offset so Telegram never labels local time
        # or confuses first discovery with the latest evidence refresh.
        if source_first_seen.tzinfo is None:
            source_first_seen = source_first_seen.replace(tzinfo=UTC)

    return {
        "job": job,
        "match": match,
        "source": ref.source_id if ref else "",
        "source_job_id": getattr(ref, "source_job_id", "") if ref else "",
        "source_observed_at": source_first_seen.isoformat() if source_first_seen else "",
        "url": ref.url if ref else "",
        "details": details,
        "fallback_salary_text": fallback_salary_text,
        "relocation_evidence": relocation_evidence if isinstance(relocation_evidence, dict) else {},
        "warning": warning,
        "search_profile_name": search.name if search else "",
    }


async def get_vacancy_comparison(
    user_id: int, job_id: int, *, search_profile_id: int | None = None
) -> dict:
    payload = await get_vacancy_details(
        user_id, job_id, **({"search_profile_id": search_profile_id} if search_profile_id is not None else {})
    )

    match = payload["match"]
    job = payload["job"]
    details = payload.get("details") or {}

    facts = await repo.list_facts(match.profile_id)

    vacancy_text = clean_html_text(
        str(details.get("description") or job.description or "")
    )

    comparison = compare_facts(vacancy_text, facts)
    profile = await repo.get_profile(match.profile_id)
    language_fit = compare_english_level(
        vacancy_text,
        profile.english_level if profile else None,
    )

    return {
        **payload,
        "comparison": comparison,
        "language_fit": language_fit,
        "facts": facts,
    }


async def get_resume_diff(
    user_id: int,
    job_id: int,
    *,
    resume_id: int | None = None,
    search_profile_id: int | None = None,
) -> dict:
    payload = await get_vacancy_comparison(
        user_id,
        job_id,
        **({"search_profile_id": search_profile_id} if search_profile_id is not None else {}),
    )
    match = payload["match"]
    resumes = await repo.list_resumes(match.profile_id)
    available = [
        resume for resume in resumes
        if resume.active is not False and getattr(resume, "deleted_at", None) is None
    ]
    selected_id = resume_id if resume_id is not None else match.resume_id
    chosen = next((resume for resume in available if resume.id == selected_id), None)
    if chosen is None:
        raise RuntimeError("Не найдено выбранное резюме этого профиля; укажи ID из /resumes")
    return {
        **payload,
        "resume": chosen,
        "resume_diff": compare_resume_coverage(payload["comparison"], chosen.content),
    }


async def prepare_match(match_id: int, user_id: int) -> dict:
    match = await repo.get_match(match_id)
    if not match or match.user_id != user_id:
        raise RuntimeError("Match не найден")
    job = await repo.get_job(match.job_id)
    if not job:
        raise RuntimeError("Вакансия не найдена")
    source_ref = None
    for source_id in _SOURCE_REF_PREFERENCE:
        source_ref = await repo.source_ref(job.id, source_id)
        if source_ref:
            break
    if not source_ref:
        source_ref = await repo.source_ref(job.id)
    job = source_posting_view(job, source_ref)
    facts = await repo.list_facts(match.profile_id)
    resumes = await repo.list_resumes(match.profile_id)
    chosen = next((r for r in resumes if r.id == match.resume_id), None)
    cover = await asyncio.to_thread(make_cover_letter, job, facts, chosen)
    comparison = compare_facts(job.description or "", facts)
    resume_diff = compare_resume_coverage(
        comparison,
        chosen.content if chosen else "",
    )
    return {
        "job": job,
        "resume": chosen,
        "cover_letter": cover,
        "resume_diff": resume_diff,
        "url": source_ref.url if source_ref else "",
        "source": source_ref.source_id if source_ref else "",
        "source_job_id": getattr(source_ref, "source_job_id", "") if source_ref else "",
        "relocation_evidence": (
            (source_ref.raw or {}).get("relocation_evidence_v1", {})
            if source_ref else {}
        ),
    }


async def apply_match(bot: Bot, match_id: int, user_id: int) -> dict:
    match = await repo.get_match(match_id)
    if not match or match.user_id != user_id:
        raise RuntimeError("Match не найден")
    # The applicant token is a single global owner credential, not per-user
    # OAuth. Never let another registered user submit through that identity.
    owner_chat = settings.telegram_admin_chat_id.strip()
    owner = await repo.get_user_by_chat(owner_chat) if owner_chat else None
    if not owner or owner.id != user_id:
        raise RuntimeError("HH private applicant API доступен только owner-профилю")
    job = await repo.get_job(match.job_id)
    if not job:
        raise RuntimeError("Вакансия не найдена")
    ref = await repo.source_ref(job.id, "hh")
    if not ref:
        raise RuntimeError("Для этой вакансии нет HH-источника с поддержкой автоотклика")
    if not hh_client.private_api_available:
        raise RuntimeError("HH private applicant API отключён; используй «Подготовить отклик» и открой вакансию на HH.")

    job = source_posting_view(job, ref)

    facts = await repo.list_facts(match.profile_id)
    resumes = await repo.list_resumes(match.profile_id)
    chosen = next((r for r in resumes if r.id == match.resume_id), None)
    hh_resume_id = (chosen.external_id if chosen and chosen.source == "hh" else None) or settings.hh_resume_id
    if not hh_resume_id:
        raise RuntimeError("Для выбранного профиля нет HH resume ID")
    cover = await asyncio.to_thread(make_cover_letter, job, facts, chosen)
    # Persist an attempt before calling HH. A crash/timeout must not make a
    # second button press look like a brand-new, safe submission.
    attempt = await repo.reserve_hh_application(
        user_id=user_id,
        job_id=job.id,
        source_job_id=ref.source_job_id,
        resume_id=match.resume_id,
        resume_snapshot=chosen.content if chosen else "",
        resume_external_id=hh_resume_id,
        vacancy_snapshot=snapshot_vacancy(
            job,
            source_id="hh",
            source_job_id=ref.source_job_id,
            source_url=ref.url,
            relocation_evidence=(getattr(ref, "raw", None) or {}).get("relocation_evidence_v1"),
        ),
        message=cover,
    )
    try:
        result = await hh_client.apply(ref.source_job_id, hh_resume_id, cover)
    except Exception:
        # HH may have accepted the request even if the client timed out.
        # If the DB is also down, the original "sending" claim still blocks retry.
        try:
            await repo.finish_hh_application(
                user_id=user_id, application_id=attempt.id, match_id=match.id,
                status="unknown",
            )
        except Exception:
            log.warning("Could not finalize ambiguous HH submission (database error)")
        raise RuntimeError(
            f"HH не подтвердил результат попытки #{attempt.id}. "
            "Проверь /applications и кабинет HH перед любым повтором."
        ) from None

    outcome = result.get("status") if isinstance(result, dict) else "unknown"
    try:
        await repo.finish_hh_application(
            user_id=user_id, application_id=attempt.id, match_id=match.id,
            status=outcome,
            source_application_id=result.get("negotiation_id") if isinstance(result, dict) else None,
            external_url=result.get("external_url") if isinstance(result, dict) else None,
        )
    except Exception:
        # The provider may have accepted the request. Fail closed: reservation
        # remains and an owner must reconcile the status before trying again.
        log.warning("Could not persist HH result after external call")
        raise RuntimeError(
            f"Статус HH попытки #{attempt.id} не удалось сохранить. "
            "Проверь /applications и кабинет HH; повторная отправка небезопасна."
        ) from None
    return {**result, "application_id": attempt.id} if isinstance(result, dict) else {
        "status": "unknown", "application_id": attempt.id,
    }


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
        log.warning("HH chats failed (%s)", type(exc).__name__)
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
            try:
                draft, confidence, human, reason = await asyncio.to_thread(
                    recruiter_reply,
                    text,
                    facts,
                    (payload.get("display") or {}).get("title", ""),
                )
            except Exception as exc:
                log.warning("HH reply draft failed (%s)", type(exc).__name__)
                draft, confidence, human = "", 0.0, True
                reason = "Черновик не создан; ответь вручную в HH."
            await repo.set_state(owner.id, f"draft:{chat_id}:{msg_id}", draft)
            if settings.auto_reply and draft and confidence >= settings.auto_reply_min_confidence and not human:
                try:
                    await hh_client.send_chat_message(chat_id, draft)
                    continue
                except Exception as exc:
                    log.warning("HH auto reply failed (%s)", type(exc).__name__)
                    reason = "Автоответ не отправлен; проверь чат и ответь вручную."
            shown = draft or "Нужен ручной ответ"
            await notify_chat(
                bot,
                owner.telegram_chat_id,
                f"💬 <b>HH сообщение</b>\n\n{html.escape(text)}\n\n<b>Черновик:</b>\n{html.escape(shown)}\n\nConfidence: {confidence:.0%}\n{html.escape(reason)}",
                parse_mode="HTML",
                reply_markup=recruiter_keyboard(chat_id, msg_id),
            )
