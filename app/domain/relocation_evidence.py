"""Conservative, source-scoped evidence extracted from vacancy text.

This is descriptive evidence only. It does not determine legal eligibility.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.domain.jobs import NormalizedJob
from app.domain.support_evidence import existing_work_authorization_required, support_evidence
from app.matching.language_fit import compare_english_level

EVIDENCE_FIELDS = (
    "work_country",
    "citizenship_or_residence_restriction",
    "existing_work_authorization_required",
    "visa_sponsorship",
    "relocation_assistance",
    "housing_provided",
    "language_requirement",
    "start_timing",
)

_RULES: dict[str, re.Pattern[str]] = {
    "citizenship_or_residence_restriction": re.compile(
        r"[^.!?;\n]{0,100}(?:citizens|citizenship|nationals only|residents only|"
        r"must be located in|only candidates (?:currently )?(?:living|residing|located) in|"
        r"candidates must (?:currently )?(?:live|reside|be located) in|applicants must be based in|"
        r"(?:граждан|резидент)\w* только|только для граждан|проживать в)"
        r"[^.!?;\n]{0,100}", re.I
    ),
    "language_requirement": re.compile(
        r"[^.!?;\n]{0,80}(?:(?:fluent|native|professional|business|basic|intermediate|"
        r"advanced) (?:level of )?(?:english|german|french|russian|language)|"
        r"(?:english|german|french|russian) (?:language )?(?:is )?(?:required|mandatory|must|preferred|desirable|not required)|"
        r"(?:английск|немецк|французск|русск)\w* язык\w*[^.!?;\n]{0,50})"
        r"[^.!?;\n]{0,80}", re.I
    ),
    "start_timing": re.compile(
        r"[^.!?;\n]{0,80}(?:start (?:date|immediately|as soon as possible)|"
        r"available to start|starting date|commencement date|notice period|"
        r"начать работу|дата выхода|срок выхода)[^.!?;\n]{0,80}", re.I
    ),
}

_HOUSING_TERM = r"(?:accommodation|housing|lodging|apartment|место проживания|жиль[её])"
_HOUSING_YES = re.compile(
    rf"(?:{_HOUSING_TERM})[^.!?;\n]{{0,45}}(?:is )?(?:provided|included|offered|available|предоставляется|включено)|"
    rf"(?:provide|offer|include|предоставляем|предлагаем)[^.!?;\n]{{0,35}}(?:{_HOUSING_TERM})",
    re.I,
)
_HOUSING_NO = re.compile(
    rf"(?:{_HOUSING_TERM})[^.!?;\n]{{0,35}}(?:is )?(?:not provided|not included|not offered|unavailable)|"
    rf"no (?:provided )?(?:{_HOUSING_TERM})[^.!?;\n]{{0,35}}(?:provided|included|offered)",
    re.I,
)
_LANGUAGE_TERM = re.compile(
    r"\b(english|german|french|russian|spanish|dutch|italian|polish|portuguese|arabic)\b|"
    r"английск\w*|немецк\w*|французск\w*|русск\w*",
    re.I,
)
_LANGUAGE_REQUIRED = re.compile(r"\b(?:required|mandatory|must|essential)\b|\b(?:обязательно|требуется|необходимо)\b", re.I)
_LANGUAGE_PREFERRED = re.compile(r"\b(?:preferred|desirable|nice to have|advantageous)\b|\b(?:желательно|приветствуется|будет плюсом)\b", re.I)
_LANGUAGE_NEGATED = re.compile(r"\b(?:not required|not mandatory|not essential)\b|\b(?:не требуется|не обязательно|не необходимо)\b", re.I)
_START_IMMEDIATE = re.compile(r"\b(?:immediately|as soon as possible|right away)\b|\b(?:немедленно|как можно скорее)\b", re.I)
_START_RELATIVE = re.compile(r"\b(?:within|in)\s+\d+\s+(?:business )?(?:days?|weeks?|months?)\b|\bчерез\s+\d+\s+(?:дн\w*|недел\w*|месяц\w*)", re.I)
_START_NEGOTIABLE = re.compile(r"\b(?:negotiable|by agreement|to be agreed)\b|\b(?:по договоренности|обсуждается)\b", re.I)
_START_NOTICE = re.compile(r"\bnotice period\b|\bсрок уведомления\b", re.I)
_START_DATE = re.compile(r"\b(?:start(?:ing)? date|commencement date)\s*[:\-]?\s*\S+|\bдата выхода\s*[:\-]?\s*\S+", re.I)
_AUTH_NOT_REQUIRED = re.compile(
    r"\b(?:no|not required|not necessary|not needed|unnecessary) "
    r"(?:(?:existing|valid|eu|european union) )?(?:right to work|work permit|work authorization)"
    r"(?: (?:is )?(?:required|necessary|needed))?\b|"
    r"\b(?:right to work|work permit|work authorization) (?:is )?(?:not required|not necessary|not needed)\b|"
    r"\b(?:разрешение на работу|право на работу) не (?:требуется|нужно|обязательно)\b",
    re.I,
)
_AUTH_REQUIREMENT_TEXT = re.compile(
    r"[^.!?;\n]{0,100}(?:must (?:already )?(?:have (?:the )?right to work|be authorized to work)|"
    r"(?:work permit|work authorization) (?:is )?required|должны? иметь право на работу)"
    r"[^.!?;\n]{0,100}", re.I,
)


def _excerpt(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text)
    return " ".join(match.group(0).split())[:240] if match else None


def build_relocation_evidence(
    job: NormalizedJob,
    *,
    captured_at: datetime | None = None,
) -> dict[str, Any]:
    """Build an auditable evidence snapshot from one source posting.

    Unknown is explicit and carries no invented excerpt. Structured source
    country is labelled as a source-reported field, not a legal work-location
    or candidate-eligibility conclusion.
    """
    captured_at = captured_at or datetime.now(timezone.utc)
    if captured_at.tzinfo is None:
        captured_at = captured_at.replace(tzinfo=timezone.utc)
    captured = captured_at.astimezone(timezone.utc).isoformat()
    text = "\n".join(part for part in (job.title, job.description) if part)
    support = support_evidence(text)
    support_patterns = {
        "visa_sponsorship": re.compile(r"[^.!?;\n]{0,100}(?:visa sponsor(?:ship)?|sponsor.{0,20}visa|визов\w* поддерж\w*)[^.!?;\n]{0,100}", re.I),
        "relocation_assistance": re.compile(r"[^.!?;\n]{0,100}(?:relocation|переезд\w*|релокац\w*)[^.!?;\n]{0,100}", re.I),
    }

    def record(value: Any, excerpt: str | None, confidence: str) -> dict[str, Any]:
        return {
            "status": "unknown" if value is None else "confirmed",
            "value": value,
            "source_id": str(job.source)[:64],
            "source_url": str(job.url or "")[:1000],
            "excerpt": excerpt,
            "captured_at": captured,
            "confidence": confidence,
        }

    country = str(job.country or "").strip()
    findings: dict[str, Any] = {
        "schema": "relocation_evidence_v1",
        "captured_at": captured,
        "fields": {},
    }
    fields = findings["fields"]
    location_excerpt = None
    for raw_key in ("source_location", "source_country"):
        raw_value = (job.raw or {}).get(raw_key)
        if isinstance(raw_value, str) and raw_value.strip():
            location_excerpt = " ".join(raw_value.split())[:240]
            break
    fields["work_country"] = record(
        country or None,
        location_excerpt or country or None,
        "source_structured" if country else "unknown",
    )

    restriction = _excerpt(job.description or "", _RULES["citizenship_or_residence_restriction"])
    restriction_field = record(
        restriction, restriction, "explicit_text" if restriction else "unknown"
    )
    if restriction:
        normalized_restriction = restriction.casefold()
        citizenship = bool(re.search(r"citizens|citizenship|nationals|граждан", normalized_restriction))
        residence = bool(re.search(
            r"residents|located|living|residing|live|reside|based in|проживать|резидент",
            normalized_restriction,
        ))
        restriction_field["interpretation"] = {
            "scope": "citizenship_and_residence" if citizenship and residence else
                     "citizenship" if citizenship else
                     "residence" if residence else "unspecified",
        }
    fields["citizenship_or_residence_restriction"] = restriction_field

    auth_text = job.description or ""
    auth = existing_work_authorization_required(auth_text)
    not_required = _AUTH_NOT_REQUIRED.search(auth_text)
    auth_positive_excerpt = _excerpt(auth_text, _AUTH_REQUIREMENT_TEXT) if auth else None
    auth_negative_excerpt = " ".join(not_required.group(0).split())[:240] if not_required else None
    if auth and not_required:
        auth_value = None
        auth_excerpt = " | ".join(filter(None, (auth_positive_excerpt, auth_negative_excerpt)))[:480]
        auth_confidence = "conflicting_text"
    elif auth:
        auth_value, auth_excerpt, auth_confidence = True, auth_positive_excerpt, "explicit_text"
    elif not_required:
        auth_value, auth_excerpt, auth_confidence = False, auth_negative_excerpt, "explicit_text"
    else:
        auth_value, auth_excerpt, auth_confidence = None, None, "unknown"
    fields["existing_work_authorization_required"] = record(
        auth_value, auth_excerpt, auth_confidence
    )

    for field, key in (("visa_sponsorship", "visa_sponsorship"), ("relocation_assistance", "relocation")):
        value = support[key]
        excerpt = _excerpt(text, support_patterns[field]) if value is not None else None
        fields[field] = record(value, excerpt, "explicit_text" if value is not None and excerpt else "unknown")
        if value is not None and not excerpt:
            fields[field] = record(None, None, "unknown")

    for field in ("housing_provided", "language_requirement", "start_timing"):
        if field == "housing_provided":
            description = job.description or ""
            no = _HOUSING_NO.search(description)
            yes = _HOUSING_YES.search(description)
            found = no or yes
            excerpt = " ".join(found.group(0).split())[:240] if found else None
            value = False if no else True if yes else None
            fields[field] = record(
                value, excerpt, "explicit_text" if value is not None else "unknown"
            )
            continue
        if field == "language_requirement":
            observations: list[dict[str, Any]] = []
            for clause in re.split(r"[.!?;\n]+", job.description or ""):
                for language_match in _LANGUAGE_TERM.finditer(clause):
                    language_text = language_match.group(0)
                    language = language_match.group(1)
                    if not language:
                        language = next((name for prefix, name in (
                            ("английск", "English"), ("немецк", "German"),
                            ("французск", "French"), ("русск", "Russian"),
                        ) if language_text.casefold().startswith(prefix)), language_text)
                    canonical = language.title() if language else "Unknown"
                    cefr = compare_english_level(clause, None) if canonical == "English" else None
                    required = bool(_LANGUAGE_REQUIRED.search(clause)) and not bool(_LANGUAGE_NEGATED.search(clause))
                    preferred = bool(_LANGUAGE_PREFERRED.search(clause))
                    if cefr and cefr.requirement in {"required", "preferred"}:
                        requirement = cefr.requirement
                    elif required != preferred and required:
                        requirement = "required"
                    elif required != preferred and preferred:
                        requirement = "preferred"
                    else:
                        requirement = "unspecified"
                    excerpt = (cefr.evidence if cefr else None) or " ".join(clause.split())[:240]
                    observations.append({
                        "language": canonical,
                        "requirement": requirement,
                        "cefr": cefr.required_level if cefr else None,
                        "excerpt": excerpt,
                    })
            grouped: dict[str, list[dict[str, Any]]] = {}
            for item in observations:
                grouped.setdefault(item["language"], []).append(item)
            normalized_observations = []
            for language, items in grouped.items():
                explicit = {item["requirement"] for item in items if item["requirement"] in {"required", "preferred"}}
                if len(explicit) > 1:
                    normalized_observations.append({
                        "language": language, "requirement": "conflicting", "cefr": None,
                        "excerpt": " | ".join(item["excerpt"] for item in items)[:480],
                    })
                else:
                    normalized_observations.extend(items)
            excerpt = " | ".join(item["excerpt"] for item in normalized_observations)[:480] or None
            explicit_requirement = any(
                item["requirement"] in {"required", "preferred"}
                for item in normalized_observations
            )
            fields[field] = record(
                excerpt, excerpt,
                "explicit_requirement" if explicit_requirement else "observed_text" if excerpt else "unknown",
            )
            if excerpt:
                fields[field]["status"] = "confirmed" if explicit_requirement else "observed"
                fields[field]["interpretation"] = {
                    "requirements": normalized_observations,
                }
            continue
        excerpt = _excerpt(job.description or "", _RULES[field])
        # A mention alone does not prove provision or a mandatory condition.
        fields[field] = record(
            excerpt, excerpt, "observed_text" if excerpt else "unknown"
        )
        if excerpt:
            fields[field]["status"] = "observed"
            if field == "start_timing":
                if _START_IMMEDIATE.search(excerpt):
                    kind = "immediate"
                elif _START_RELATIVE.search(excerpt):
                    kind = "relative_window"
                elif _START_NEGOTIABLE.search(excerpt):
                    kind = "negotiable"
                elif _START_NOTICE.search(excerpt):
                    kind = "notice_period"
                elif _START_DATE.search(excerpt):
                    kind = "stated_date"
                else:
                    kind = "observed_text"
                fields[field]["interpretation"] = {"kind": kind}
    return findings
