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
    r"\b(english|german|french|russian)\b|английск\w*|немецк\w*|французск\w*|русск\w*",
    re.I,
)
_LANGUAGE_REQUIRED = re.compile(r"\b(?:required|mandatory|must|essential)\b|\b(?:обязательно|требуется|необходимо)\b", re.I)
_LANGUAGE_PREFERRED = re.compile(r"\b(?:preferred|desirable|nice to have|advantageous)\b|\b(?:желательно|приветствуется|будет плюсом)\b", re.I)
_LANGUAGE_NEGATED = re.compile(r"\b(?:not required|not mandatory|not essential)\b|\b(?:не требуется|не обязательно|не необходимо)\b", re.I)


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
    fields["work_country"] = record(country or None, country or None, "source_structured" if country else "unknown")

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

    auth = existing_work_authorization_required(job.description or "")
    auth_excerpt = _excerpt(job.description or "", re.compile(
        r"[^.!?;\n]{0,100}(?:must (?:already )?(?:have the right to work|be authorized to work)|"
        r"(?:work permit|work authorization) (?:is )?required|должны? иметь право на работу)"
        r"[^.!?;\n]{0,100}", re.I
    )) if auth else None
    fields["existing_work_authorization_required"] = record(
        True if auth else None, auth_excerpt, "explicit_text" if auth else "unknown"
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
            language_match = _LANGUAGE_TERM.search(job.description or "")
            language = language_match.group(0) if language_match else None
            cefr = compare_english_level(job.description or "", None) if language and "english" in language.casefold() else None
            excerpt = (
                cefr.evidence if cefr
                else _excerpt(job.description or "", _RULES[field])
                or (language_match.group(0) if language_match else None)
            )
            requirement = cefr.requirement if cefr else "unspecified"
            if language and not cefr and excerpt:
                clause = next((part for part in re.split(r"[.!?;\n]+", job.description or "") if language.casefold() in part.casefold()), "")
                required = bool(_LANGUAGE_REQUIRED.search(clause)) and not bool(_LANGUAGE_NEGATED.search(clause))
                preferred = bool(_LANGUAGE_PREFERRED.search(clause))
                requirement = "required" if required != preferred and required else "preferred" if required != preferred and preferred else "unspecified"
            value = excerpt
            fields[field] = record(
                value, excerpt,
                "explicit_requirement" if requirement in {"required", "preferred"} else "observed_text" if excerpt else "unknown",
            )
            if excerpt:
                fields[field]["status"] = "confirmed" if requirement in {"required", "preferred"} else "observed"
                fields[field]["interpretation"] = {
                    "language": "English" if language and "english" in language.casefold() else language,
                    "requirement": requirement,
                    "cefr": cefr.required_level if cefr else None,
                }
            continue
        excerpt = _excerpt(job.description or "", _RULES[field])
        # A mention alone does not prove provision or a mandatory condition.
        fields[field] = record(
            excerpt, excerpt, "observed_text" if excerpt else "unknown"
        )
        if excerpt:
            fields[field]["status"] = "observed"
    return findings
