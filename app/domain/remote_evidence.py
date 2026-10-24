from __future__ import annotations

import re

from app.domain.job_text import clean_html_text
from app.geo.countries import normalize_country


_UNKNOWN_SCOPES = frozenset({"", "unknown", "unspecified", "none", "n/a", "remote"})
_GLOBAL_SCOPES = frozenset({
    "worldwide", "global", "anywhere", "remote worldwide", "worldwide remote",
    "globally remote", "global remote", "work from anywhere", "anywhere in the world",
})
_OTHER_LOCATION_LABELS = frozenset({
    "us", "usa", "u.s.", "united states", "united states of america",
    "uk", "united kingdom", "eu", "european union", "europe", "emea",
})
_RESIDENCE = re.compile(
    r"(?:^|[.!?;]\s+|\n)\s*(?:[-*•]\s*)?"
    r"(?P<requirement>(?:(?:all\s+)?(?:candidates?|applicants?)\s+|you\s+)?"
    r"(?:must|need to|needs to|are required to|is required to)\s+"
    r"(?:(?:currently|already)\s+)?"
    r"(?:live|reside|be (?:based|located))\s+in\s+"
    r"(?P<location>[^\n;!?]+))",
    re.I,
)
_WITHDRAWN_REQUIREMENT = re.compile(
    r"\b(?:not (?:required|mandatory|necessary)|no (?:such )?requirement|"
    r"only (?:preferred|a preference)|(?:is|are) optional)\b", re.I,
)
_NON_REMOTE_WORK = re.compile(
    r"\b(?:there is )?no (?:option|opportunity) to work remotely\b|"
    r"\bno remote (?:work|working)\b|"
    r"\bremote(?:ly)? (?:work|working) (?:is )?not "
    r"(?:available|offered|permitted|possible)\b|"
    r"\bremote location\b|"
    r"\b(?:не )?удал[её]нн\w* работ\w* не (?:предусмотрен\w*|доступн\w*|возможн\w*)\b|"
    r"\bне удал[её]нн\w* работ\w*\b",
    re.I,
)
_REMOTE_WORK = re.compile(r"\bremote(?:ly)?\b|\bудал[её]н\w*\b", re.I)


def has_remote_work_evidence(*values: str | None) -> bool:
    """Recognize remote work without treating explicit onsite text as remote.

    Job boards commonly include either “no option to work remotely” or
    “remote location” in otherwise onsite postings. Those phrases describe a
    refusal or physical remoteness, not a remote-work arrangement.
    """
    text = " ".join(clean_html_text(value or "") for value in values)
    return bool(_REMOTE_WORK.search(_NON_REMOTE_WORK.sub(" ", text)))


def restricted_remote_scope(scope: str | None) -> bool:
    """A supplied non-global scope is a limit, not proof of applicant eligibility."""
    normalized = " ".join(clean_html_text(scope or "").casefold().split())
    return normalized not in _UNKNOWN_SCOPES | _GLOBAL_SCOPES


def remote_location_restriction(value: object) -> str | None:
    """Preserve an explicit '<known geography> only' label, without legal inference.

    A bare country/city could be an office label. Unknown wording, worldwide
    labels and qualifications stay unknown; do not promote them to a work country
    or a residence/citizenship requirement.
    """
    if not isinstance(value, str) or len(value) > 512:
        return None
    label = " ".join(clean_html_text(value).split())
    if len(label) > 128:
        return None
    match = re.fullmatch(r"(?P<location>.+?)(?:\s+|[-–])only\.?", label, re.I)
    if not match:
        return None
    location = match.group("location").strip()
    if normalize_country(location) or location.casefold() in _OTHER_LOCATION_LABELS:
        return label
    return None


def remote_residence_requirement(description: str | None) -> str | None:
    """Extract a narrow, positive applicant-residence clause as source evidence.

    Deliberately does not map regions to countries or claim work authorization.
    Sentence/list anchoring avoids extracting company-office descriptions,
    quotations within narrative, or negated requirements as applicant facts.
    Unrecognized phrasing stays unknown; this is not a general language parser.
    """
    text = clean_html_text(description or "")
    for match in _RESIDENCE.finditer(text):
        requirement = match.group("requirement").strip()
        # Stop at a following sentence. A dotted abbreviation such as U.S.
        # remains intact when it is the end of the candidate-location clause.
        requirement = re.split(r"(?<!\b[A-Z])\.\s+", requirement, maxsplit=1)[0]
        requirement = requirement.rstrip(". ")
        location = requirement[match.start("location") - match.start("requirement"):].strip()
        if not location or _WITHDRAWN_REQUIREMENT.search(requirement):
            continue
        if location.casefold() in {"any country", "any location", "anywhere", "the world"}:
            continue
        # A question about a requirement is not an affirmative requirement.
        if match.end() < len(text) and text[match.end()] == "?":
            continue
        return " ".join(requirement.split())[:240]
    return None
