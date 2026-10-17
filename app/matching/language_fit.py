from __future__ import annotations

import re
from dataclasses import dataclass


_CEFR_ORDER = {
    "A1": 10,
    "A1+": 11,
    "A2": 20,
    "A2+": 21,
    "B1": 30,
    "B1+": 31,
    "B2": 40,
    "B2+": 41,
    "C1": 50,
    "C1+": 51,
    "C2": 60,
}

_ENGLISH_RE = re.compile(
    r"\b(?:english(?:\s+language)?|английск(?:ий|ого|ому|им|ом|ая|ую|ое|ие)(?:\s+язык\w*)?)\b",
    flags=re.IGNORECASE,
)
_LEVEL_RE = re.compile(
    r"\b(?P<level>[ABC][12])\s*(?P<plus>\+)?(?!\w)",
    flags=re.IGNORECASE,
)
_PREFERRED_RE = re.compile(
    r"\b(?:preferred|desirable|nice\s+to\s+have|advantageous)\b|"
    r"\b(?:желательно|приветствуется|будет\s+плюсом|преимуществом)\b",
    flags=re.IGNORECASE,
)
_REQUIRED_RE = re.compile(
    r"\b(?:required|must|mandatory|essential|minimum)\b|"
    r"\b(?:обязательно|требуется|необходимо|не\s+ниже)\b",
    flags=re.IGNORECASE,
)
_NEGATED_REQUIRED_RE = re.compile(
    r"\b(?:not\s+(?:required|mandatory)|not\s+essential)\b|"
    r"\b(?:не\s+(?:требуется|обязательно|необходимо))\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class LanguageFit:
    required_level: str
    candidate_level: str | None
    status: str
    evidence: str
    requirement: str


def normalize_cefr(value: str | None) -> str | None:
    normalized = re.sub(r"\s+", "", str(value or "")).upper()
    return normalized if normalized in _CEFR_ORDER else None


def extract_english_level(text: str) -> tuple[str, str] | None:
    """Return one explicit CEFR English level and its bounded source phrase.

    Ambiguous clauses containing different CEFR levels stay unknown. General
    wording such as "fluent English" is deliberately not converted to CEFR.
    """
    observations: list[tuple[str, str]] = []
    for clause in re.split(r"[.\n;]+", text or ""):
        english = _ENGLISH_RE.search(clause)
        if english is None:
            continue
        for match in _LEVEL_RE.finditer(clause):
            distance = max(
                english.start() - match.end(),
                match.start() - english.end(),
                0,
            )
            if distance > 45:
                continue
            level = normalize_cefr(match.group("level") + (match.group("plus") or ""))
            if level:
                start = min(english.start(), match.start())
                end = max(english.end(), match.end())
                observations.append((level, " ".join(clause[start:end].split())))

    levels = {level for level, _ in observations}
    if len(levels) != 1:
        return None
    level = levels.pop()
    evidence = min(
        (evidence for observed, evidence in observations if observed == level),
        key=len,
    )
    return level, evidence


def compare_english_level(text: str, candidate_level: str | None) -> LanguageFit | None:
    extracted = extract_english_level(text)
    if extracted is None:
        return None
    required_level, evidence = extracted
    requirement = "unspecified"
    clause_matches = [
        clause
        for clause in re.split(r"[.\n;]+", text or "")
        if evidence.casefold() in clause.casefold()
    ]
    markers = {
        "preferred": any(_PREFERRED_RE.search(clause) for clause in clause_matches),
        "required": any(
            _REQUIRED_RE.search(clause) and not _NEGATED_REQUIRED_RE.search(clause)
            for clause in clause_matches
        ),
    }
    if markers["preferred"] != markers["required"]:
        requirement = "preferred" if markers["preferred"] else "required"
    normalized_candidate = normalize_cefr(candidate_level)
    if normalized_candidate is None:
        status = "unknown"
    elif _CEFR_ORDER[normalized_candidate] >= _CEFR_ORDER[required_level]:
        status = "meets"
    else:
        status = "below"
    return LanguageFit(
        required_level=required_level,
        candidate_level=normalized_candidate,
        status=status,
        evidence=evidence,
        requirement=requirement,
    )
