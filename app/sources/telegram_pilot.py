"""Offline analysis of an owner-approved bounded Telegram channel sample."""
from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import score_job
from app.sources.adapters.telegram_ingest import parse_telegram_job
from app.sources.telegram_post import explicit_non_vacancy


APPROVED_CHANNELS = {
    -1001134745498: "devops_jobs_feed",
    -1002619852984: "itjobsgeorgia",
    -1001475742662: "vgrecruitingit",
}
MAX_SAMPLE_POSTS = 150
MAX_SAMPLE_BYTES = 16 * 1024 * 1024


def load_private_sample(path: Path) -> list[dict]:
    """Load only a private, regular pilot file containing approved channels."""
    info = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ValueError("pilot sample must be a regular file")
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("pilot sample must be owned by the current user with mode 0600")
    if info.st_size > MAX_SAMPLE_BYTES:
        raise ValueError("pilot sample is too large")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != 1:
        raise ValueError("unsupported pilot sample schema")
    posts = payload.get("posts")
    if not isinstance(posts, list) or len(posts) > MAX_SAMPLE_POSTS:
        raise ValueError("pilot sample has an invalid post count")
    checked = []
    for row in posts:
        if not isinstance(row, dict):
            raise ValueError("pilot sample contains an invalid post")
        chat_id = row.get("channel_id")
        username = str(row.get("username") or "").lstrip("@").casefold()
        message_id = row.get("message_id")
        text = row.get("text")
        published = row.get("published_at")
        if (
            chat_id not in APPROVED_CHANNELS
            or username != APPROVED_CHANNELS[chat_id]
            or not isinstance(message_id, int) or isinstance(message_id, bool) or message_id <= 0
            or not isinstance(text, str) or not text.strip() or len(text) > 100_000
            or not isinstance(published, str)
        ):
            raise ValueError("pilot sample post is outside the approved contract")
        try:
            date = datetime.fromisoformat(published)
        except ValueError as exc:
            raise ValueError("pilot sample publication date is invalid") from exc
        if date.tzinfo is None:
            raise ValueError("pilot sample publication date needs a timezone")
        checked.append(row)
    return checked


def _profile(profile_path: Path) -> tuple[list[CandidateFact], tuple[SearchProfile, SearchProfile]]:
    payload = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    candidate = payload.get("candidate") or {}
    geography = payload.get("geography") or {}
    source = dict(payload.get("search") or {})
    facts = [
        CandidateFact(profile_id=1, value=str(value), category="experience", active=True)
        for value in candidate.get("facts") or []
        if str(value).strip()
    ]
    minimum = source.pop("minimum_salary_net_rub", 0)
    common = {
        **source,
        "target_countries": geography.get("target_countries") or [],
        "remote_worldwide": geography.get("remote_worldwide", True),
        "remote_regions": geography.get("remote_regions") or [],
        "relocation_enabled": geography.get("relocation_enabled", True),
        "relocation_countries": geography.get("relocation_countries") or [],
        "minimum_salary": {"RUB": minimum},
        "modes": source.get("modes") or {
            "local_ru": True, "remote_international": True, "relocation": True,
        },
    }
    career = SearchProfile(id=1, profile_id=1, name="Career-first", kind="employment", settings={
        **common, "search_strategy": "career_first",
    })
    relocation = SearchProfile(id=2, profile_id=1, name="Relocation-first", kind="employment", settings={
        **common,
        "queries": source.get("relocation_queries") or source.get("queries") or [],
        "search_strategy": "relocation_first",
    })
    return facts, (career, relocation)


def _job(normalized) -> Job:
    return Job(
        fingerprint=normalized.canonical_fingerprint(), title=normalized.title,
        company=normalized.company, description=normalized.description,
        country=normalized.country, city=normalized.city, work_mode=normalized.work_mode,
        remote_scope=normalized.remote_scope, relocation=normalized.relocation,
        visa_sponsorship=normalized.visa_sponsorship,
        salary_from=normalized.salary_from, salary_to=normalized.salary_to,
        salary_currency=normalized.salary_currency, salary_period=normalized.salary_period,
        published_at=normalized.published_at,
    )


def analyze_sample(posts: list[dict], profile_path: Path) -> dict:
    facts, searches = _profile(profile_path)
    channels: dict[str, Counter] = {name: Counter() for name in APPROVED_CHANNELS.values()}
    fingerprints: Counter[str] = Counter()
    rows = []
    for post in posts:
        channel = APPROVED_CHANNELS[post["channel_id"]]
        counts = channels[channel]
        counts["posts"] += 1
        if explicit_non_vacancy(post["text"]):
            counts["non_vacancy"] += 1
            continue
        counts["vacancy_candidates"] += 1
        identity = f'channel:{post["channel_id"]}:{post["message_id"]}'
        normalized = parse_telegram_job(post["text"], source_ref=identity, source_url=post.get("url") or "")
        normalized.published_at = post["published_at"]
        fingerprint = normalized.canonical_fingerprint()
        fingerprints[fingerprint] += 1
        scored = []
        for search in searches:
            result = score_job(_job(normalized), search, facts, [])
            threshold = int(search.settings.get("notify_min_score", 60))
            lane = "filtered" if result.fit == "skip" or result.total_score < threshold else result.fit
            lane = "good" if lane == "good" else lane
            scored.append({"profile": search.name, "lane": lane, "score": result.total_score,
                           "reason": result.reason})
        rank = {"good": 2, "stretch": 1, "filtered": 0}
        best = max(scored, key=lambda item: (rank[item["lane"]], item["score"]))
        counts[best["lane"]] += 1
        rows.append({
            "channel": channel, "message_id": post["message_id"], "url": post.get("url"),
            "title": normalized.title, "company": normalized.company,
            "country": normalized.country, "city": normalized.city,
            "canonical_fingerprint": fingerprint, "best": best, "profiles": scored,
        })
    duplicate_posts = sum(amount - 1 for amount in fingerprints.values() if amount > 1)
    totals = sum(channels.values(), Counter())
    totals["unique_vacancies"] = len(fingerprints)
    totals["duplicates"] = duplicate_posts
    return {
        "profile_basis": str(profile_path),
        "channels": {name: dict(counts) for name, counts in channels.items()},
        "totals": dict(totals),
        "vacancies": rows,
    }
