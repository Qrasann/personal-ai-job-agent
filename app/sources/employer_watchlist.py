from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
import re
from urllib.parse import urlparse

import yaml


WATCHLIST_PATH = Path("data/employer_watchlist.yaml")
_ATS_KINDS = {"custom", "greenhouse", "lever", "smartrecruiters"}
_PRIORITIES = {"P0", "P1", "P2"}
_SUITABILITY = {"high", "medium", "low"}
_EVIDENCE = {"unknown", "confirmed", "refused", "conflicting"}
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


@dataclass(frozen=True)
class WatchedOpening:
    provider_id: str
    title: str
    location: str
    url: str
    suitability: str
    work_authorization: str
    visa_sponsorship: str
    relocation: str


@dataclass(frozen=True)
class WatchedEmployer:
    id: str
    name: str
    enabled: bool
    priority: str
    ats: str
    identifier: str
    careers_url: str
    api_url: str | None
    allowed_hosts: frozenset[str]
    markets: tuple[str, ...]
    tracks: tuple[str, ...]
    industry_tags: tuple[str, ...]
    openings: tuple[WatchedOpening, ...]


@dataclass(frozen=True)
class EmployerWatchlist:
    schema_version: int
    verified_at: date
    evidence_policy: str
    employers: tuple[WatchedEmployer, ...]


def _https_url(value: object, *, hosts: set[str] | frozenset[str] | None = None) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        raise ValueError("watchlist URL must be a bounded non-empty string")
    value = value.strip()
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("watchlist URL is malformed") from exc
    host = (parsed.hostname or "").casefold()
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.fragment
        or (hosts is not None and host not in hosts)
    ):
        raise ValueError("watchlist URL is outside its HTTPS host contract")
    return value


def _api_url(kind: str, identifier: str, value: object) -> str | None:
    if kind == "custom":
        if value not in {None, ""}:
            raise ValueError("custom career pages cannot declare an unreviewed API endpoint")
        return None
    expected = {
        "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{identifier}/jobs",
        "lever": f"https://api.lever.co/v0/postings/{identifier}",
        "smartrecruiters": f"https://api.smartrecruiters.com/v1/companies/{identifier}/postings",
    }[kind]
    if value != expected:
        raise ValueError(f"{kind} API endpoint does not match the reviewed identifier")
    return expected


def _strings(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    result = tuple(str(item).strip() for item in value)
    if any(not item or len(item) > 96 for item in result) or len(set(result)) != len(result):
        raise ValueError(f"{field} contains invalid or duplicate values")
    return result


def _opening(row: object, hosts: frozenset[str]) -> WatchedOpening:
    if not isinstance(row, dict):
        raise ValueError("opening must be a mapping")
    provider_id = str(row.get("provider_id") or "").strip()
    title = str(row.get("title") or "").strip()
    location = str(row.get("location") or "").strip()
    suitability = str(row.get("suitability") or "")
    if not _ID_RE.fullmatch(provider_id):
        raise ValueError("opening provider_id is invalid")
    if not title or len(title) > 256 or not location or len(location) > 256:
        raise ValueError("opening title/location is invalid")
    if suitability not in _SUITABILITY:
        raise ValueError("opening suitability is invalid")
    evidence = {
        key: str(row.get(key) or "")
        for key in ("work_authorization", "visa_sponsorship", "relocation")
    }
    if any(value not in _EVIDENCE for value in evidence.values()):
        raise ValueError("opening eligibility evidence is invalid")
    return WatchedOpening(
        provider_id=provider_id,
        title=title,
        location=location,
        url=_https_url(row.get("url"), hosts=hosts),
        suitability=suitability,
        **evidence,
    )


def _employer(row: object) -> WatchedEmployer:
    if not isinstance(row, dict):
        raise ValueError("employer must be a mapping")
    employer_id = str(row.get("id") or "").strip()
    identifier = str(row.get("identifier") or "").strip()
    name = str(row.get("name") or "").strip()
    kind = str(row.get("ats") or "")
    priority = str(row.get("priority") or "")
    if not _ID_RE.fullmatch(employer_id) or not _ID_RE.fullmatch(identifier):
        raise ValueError("employer id/identifier is invalid")
    if not name or len(name) > 128 or kind not in _ATS_KINDS or priority not in _PRIORITIES:
        raise ValueError("employer metadata is invalid")
    if not isinstance(row.get("enabled"), bool):
        raise ValueError("employer enabled must be boolean")
    hosts = frozenset(host.casefold() for host in _strings(row.get("allowed_hosts"), "allowed_hosts"))
    if any(urlparse(f"https://{host}").hostname != host for host in hosts):
        raise ValueError("allowed_hosts contains an invalid hostname")
    openings_raw = row.get("openings")
    if not isinstance(openings_raw, list) or not openings_raw:
        raise ValueError("each employer needs at least one verified opening")
    openings = tuple(_opening(item, hosts) for item in openings_raw)
    industry_tags_raw = row.get("industry_tags", [])
    if not isinstance(industry_tags_raw, list):
        raise ValueError("industry_tags must be a list")
    industry_tags = tuple(str(value).strip().casefold() for value in industry_tags_raw)
    if (
        any(not value or len(value) > 64 for value in industry_tags)
        or len(set(industry_tags)) != len(industry_tags)
    ):
        raise ValueError("industry_tags contains invalid or duplicate values")
    provider_ids = [item.provider_id for item in openings]
    if len(provider_ids) != len(set(provider_ids)):
        raise ValueError("opening provider IDs must be unique per employer")
    return WatchedEmployer(
        id=employer_id,
        name=name,
        enabled=row["enabled"],
        priority=priority,
        ats=kind,
        identifier=identifier,
        careers_url=_https_url(row.get("careers_url")),
        api_url=_api_url(kind, identifier, row.get("api_url")),
        allowed_hosts=hosts,
        markets=_strings(row.get("markets"), "markets"),
        tracks=_strings(row.get("tracks"), "tracks"),
        industry_tags=industry_tags,
        openings=openings,
    )


@lru_cache(maxsize=1)
def load_employer_watchlist(path: Path | None = None) -> EmployerWatchlist:
    source = path or WATCHLIST_PATH
    with source.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("unsupported employer watchlist schema")
    try:
        verified_at = date.fromisoformat(str(payload.get("verified_at") or ""))
    except ValueError as exc:
        raise ValueError("watchlist verified_at must be an ISO date") from exc
    policy = str(payload.get("evidence_policy") or "").strip()
    rows = payload.get("employers")
    if not policy or not isinstance(rows, list) or not 10 <= len(rows) <= 20:
        raise ValueError("watchlist needs policy and 10-20 reviewed employers")
    employers = tuple(_employer(row) for row in rows)
    employer_ids = [item.id for item in employers]
    if len(employer_ids) != len(set(employer_ids)):
        raise ValueError("employer IDs must be unique")
    return EmployerWatchlist(1, verified_at, policy, employers)


def enabled_employers(path: Path | None = None) -> tuple[WatchedEmployer, ...]:
    return tuple(item for item in load_employer_watchlist(path).employers if item.enabled)
