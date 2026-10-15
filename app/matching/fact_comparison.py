from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from app.candidates.fact_types import normalize_experience_type
from app.database.models import CandidateFact


@dataclass(frozen=True, slots=True)
class SkillSpec:
    name: str
    aliases: tuple[str, ...]


# Deterministic DevOps / Infrastructure vocabulary.
#
# This is deliberately separate from SearchProfile.preferred_terms:
# search terms decide which vacancies are interesting, while this vocabulary
# describes technologies/signals that can be compared with Candidate Facts.
SKILLS: tuple[SkillSpec, ...] = (
    SkillSpec("Linux", ("linux", "debian", "ubuntu", "centos", "rhel")),
    SkillSpec("Windows", ("windows",)),
    SkillSpec("systemd", ("systemd",)),
    SkillSpec("Docker", ("docker",)),
    SkillSpec("Docker Compose", ("docker compose", "docker-compose")),
    SkillSpec("Kubernetes", ("kubernetes", "k8s")),
    SkillSpec("OpenShift", ("openshift", "red hat openshift")),
    SkillSpec("Databricks", ("databricks",)),
    SkillSpec("Nginx", ("nginx",)),
    SkillSpec("HAProxy", ("haproxy",)),
    SkillSpec("Git", ("git",)),
    SkillSpec(
        "GitLab CI",
        (
            "gitlab ci",
            "gitlab-ci",
            "gitlab ci/cd",
            "gitlab cicd",
            "gitlab",
        ),
    ),
    SkillSpec("CI/CD", ("ci/cd", "cicd", "continuous integration", "continuous delivery")),
    SkillSpec("Bash", ("bash", "shell scripting")),
    SkillSpec("Python", ("python",)),
    SkillSpec("Ansible", ("ansible",)),
    SkillSpec("Terraform", ("terraform",)),
    SkillSpec("Terragrunt", ("terragrunt",)),
    SkillSpec("Helm", ("helm", "helm chart", "helm charts", "helm-чарт", "helm-чарты")),
    SkillSpec("ArgoCD", ("argocd", "argo cd")),
    SkillSpec("GitOps", ("gitops", "git ops")),
    SkillSpec("Prometheus", ("prometheus",)),
    SkillSpec("Grafana", ("grafana",)),
    SkillSpec("Zabbix", ("zabbix",)),
    SkillSpec("ELK", ("elk", "elk stack", "elk-stack", "elasticsearch logstash kibana")),
    SkillSpec("Graylog", ("graylog",)),
    SkillSpec("MySQL", ("mysql",)),
    SkillSpec("PostgreSQL", ("postgresql", "postgres")),
    SkillSpec("MinIO", ("minio",)),
    SkillSpec("Yandex Cloud", ("yandex cloud", "яндекс облако", "яндекс.облако")),
    SkillSpec("AWS", ("aws", "amazon web services")),
    SkillSpec("Azure", ("azure", "microsoft azure")),
    SkillSpec("GCP", ("gcp", "google cloud", "google cloud platform")),
    SkillSpec("Active Directory", ("active directory", "active directory domain", "ad ds")),
    SkillSpec("VPN", ("vpn", "wireguard", "openvpn")),
    SkillSpec("DNS", ("dns", "domain name system", "domain name resolution")),
    SkillSpec("TLS", ("tls", "ssl", "tls ssl", "tls/ssl")),
    SkillSpec(
        "Security Operations",
        ("security operations", "cybersecurity", "information security", "информационная безопасность"),
    ),
    SkillSpec(
        "Networking",
        (
            "networking",
            "network",
            "networks",
            "сетей",
            "сети",
            "сетевые",
            "сетевых",
            "firewall",
            "nat",
        ),
    ),
    SkillSpec("Jitsi", ("jitsi",)),
    SkillSpec("WebRTC", ("webrtc", "web rtc")),
    SkillSpec("STUN/TURN", ("stun", "turn server", "turn servers", "stun/turn")),
)


_EXPERIENCE_PRIORITY: dict[str, int] = {
    "commercial": 4,
    "lab": 3,
    "learning": 2,
    "unknown": 1,
}


@dataclass(frozen=True, slots=True)
class RequirementMatch:
    skill: str
    status: str
    importance: str = "unknown"
    fact_ids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class FactComparison:
    requirements: tuple[RequirementMatch, ...]
    alternative_groups: tuple[tuple[str, ...], ...] = ()
    preferred_alternative_groups: tuple[tuple[str, ...], ...] = ()

    @property
    def total(self) -> int:
        return len(self.requirements)

    @property
    def present(self) -> int:
        return sum(1 for item in self.requirements if item.status != "missing")

    def skills_for(self, status: str) -> list[str]:
        return [
            item.skill
            for item in self.requirements
            if item.status == status
        ]

    def items_for_importance(self, importance: str) -> list[RequirementMatch]:
        return [
            item
            for item in self.requirements
            if item.importance == importance
        ]

    def total_for_importance(self, importance: str) -> int:
        return len(self.items_for_importance(importance))

    def present_for_importance(self, importance: str) -> int:
        return sum(
            1
            for item in self.items_for_importance(importance)
            if item.status != "missing"
        )


def _normalize_text(value: str) -> str:
    text = (value or "").casefold()

    # Normalize common separators so aliases such as GitLab-CI and CI/CD
    # can be matched without broad substring searches.
    text = re.sub(r"[/_–—-]+", " ", text)
    text = re.sub(r"[^\w+#]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _contains_alias(text: str, alias: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_alias = _normalize_text(alias)

    if not normalized_alias:
        return False

    # Padding gives us token/phrase boundaries and prevents e.g. "git"
    # from matching arbitrary longer words.
    return f" {normalized_alias} " in f" {normalized_text} "


def _matches_skill(text: str, spec: SkillSpec) -> bool:
    return any(_contains_alias(text, alias) for alias in spec.aliases)


def _explicitly_not_required(text: str, spec: SkillSpec) -> bool:
    """Recognize narrow, direct negations of a skill requirement."""
    normalized = _normalize_text(text)
    for alias in spec.aliases:
        target = re.escape(_normalize_text(alias)).replace(r"\ ", r"\s+")
        patterns = (
            rf"\bno (?:prior |previous )?(?:experience|knowledge|proficiency) (?:with |in |of )?{target}\b",
            rf"\bno {target} (?:experience|knowledge|proficiency)\b",
            rf"\b{target}(?: (?:experience|knowledge|proficiency))? (?:is )?(?:not required|not mandatory|not necessary|not needed|optional)\b",
            rf"\b(?:not required|not mandatory|not necessary|not needed) (?:for )?(?:experience|knowledge|proficiency)(?: (?:with|in|of))? {target}\b",
            rf"\bno experience (?:with|in|of) {target} required\b",
        )
        if any(re.search(pattern, normalized) for pattern in patterns):
            return True
    return False


def _explicitly_preferred(text: str, spec: SkillSpec) -> bool:
    """Recognize a narrow skill-local optional/preferred phrase."""
    normalized = _normalize_text(text)
    for alias in spec.aliases:
        target = re.escape(_normalize_text(alias)).replace(r"\ ", r"\s+")
        patterns = (
            rf"\b{target}(?: (?:experience|knowledge))? (?:is )?(?:a )?(?:plus|bonus|preferred|desirable|optional|nice to have)\b",
            rf"\b{target}(?: (?:experience|knowledge))? (?:would be )?(?:a )?plus\b",
            rf"\b{target} (?:будет плюсом|приветствуется|желательно|является преимуществом)\b",
            rf"\b(?:preferred|desirable|optional|nice to have|bonus|будет плюсом|желательно|приветствуется) (?:experience|knowledge)? (?:with |in )?{target}\b",
        )
        if any(re.search(pattern, normalized) for pattern in patterns):
            return True
    return False


def _required_skill_in_section(text: str, spec: SkillSpec) -> bool:
    # Clause boundaries prevent a negated skill from masking another explicit
    # requirement elsewhere in the same heading.
    for clause in re.split(r"[\n.!?;]+", text or ""):
        if (
            _matches_skill(clause, spec)
            and not _explicitly_not_required(clause, spec)
            and not _explicitly_preferred(clause, spec)
        ):
            return True
    return False


def _preferred_skill_in_section(text: str, spec: SkillSpec) -> bool:
    return any(
        _matches_skill(clause, spec) and _explicitly_preferred(clause, spec)
        for clause in re.split(r"[\n.!?;]+", text or "")
    )


_REQUIRED_HEADINGS = (
    "требования к кандидатам",
    "обязательные требования",
    "necessary qualification",
    "necessary qualifications",
    "required qualification",
    "required qualifications",
    "minimum qualification",
    "minimum qualifications",
    "essential qualification",
    "essential qualifications",
    "требования",
    "что мы ожидаем",
    "мы ожидаем",
    "необходимо",
    "requirements",
    "what we are looking for",
    "what we are looking for in you",
    "what you'll bring",
    "what you bring",
    "must have",
    "must-have",
    "required",
    "what we expect",
    "what we expect from candidates",
)

_PREFERRED_HEADINGS = (
    "приветствуется",
    "будет плюсом",
    "плюсом будет",
    "будет преимуществом",
    "что будет вашим преимуществом",
    "желательно",
    "желательные требования",
    "nice to have",
    "nice-to-have",
    "nice to have skills",
    "nice-to-have skills",
    "preferred",
    "preferred qualifications",
    "bonus",
    "would be a plus",
    "as a plus",
)

_NEUTRAL_HEADINGS = (
    "обязанности",
    "чем вам предстоит заниматься",
    "чем предстоит заниматься",
    "в процессе работы необходимо",
    "задачи",
    "что предстоит делать",
    "responsibilities",
    "duties",
    "what you will do",
    "what you'll do",
    "о компании",
    "about us",
    "about company",
    "что мы предлагаем",
    "мы предлагаем",
    "для вас мы предлагаем",
    "условия",
    "what we offer",
    "benefits",
)

_INLINE_HEADING_BREAK = re.compile(
    r"(?<=[.;])\s+(?=(?:"
    + "|".join(
        re.escape(heading)
        for heading in sorted(
            set(_REQUIRED_HEADINGS + _PREFERRED_HEADINGS + _NEUTRAL_HEADINGS),
            key=len,
            reverse=True,
        )
    )
    + r")\s*:)",
    flags=re.IGNORECASE,
)

# An example of a language choice is not an individual must-have. Keep the
# mention in the vacancy text (and thus in unknown evidence), but exclude the
# explicitly qualified clause from the required bucket. This intentionally
# handles only the unambiguous wording observed in an employer posting.
_LANGUAGE_ALTERNATIVE_EXAMPLE = re.compile(
    r"\bwith\s+[^.\n:]{1,80}?\s+among\s+(?:the\s+)?language\s+alternatives?\b",
    flags=re.IGNORECASE,
)


def _match_section_heading(
    line: str,
    headings: tuple[str, ...],
) -> tuple[bool, str]:
    # Preserve common typographic apostrophes used by job boards while
    # matching against the canonical ASCII heading variants.
    line = line.replace("’", "'").replace("‘", "'")
    for heading in headings:
        match = re.match(
            rf"^\s*{re.escape(heading)}\s*(?:[:.\-–—]\s*(.*))?\s*$",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            return True, (match.group(1) or "").strip()

    return False, ""


def _split_requirement_sections(text: str) -> dict[str, str]:
    buckets: dict[str, list[str]] = {
        "required": [],
        "preferred": [],
        "unknown": [],
    }

    current = "unknown"

    # Some feeds flatten adjacent labelled sections into one sentence. Split
    # only at an explicit punctuated heading so a preferred skill does not
    # inherit the previous required section.
    for raw_line in _INLINE_HEADING_BREAK.sub("\n", text or "").splitlines():
        line = raw_line.strip()

        if not line:
            continue

        matched, remainder = _match_section_heading(
            line,
            _REQUIRED_HEADINGS,
        )
        if matched:
            current = "required"
            if remainder:
                buckets[current].append(remainder)
            continue

        matched, remainder = _match_section_heading(
            line,
            _PREFERRED_HEADINGS,
        )
        if matched:
            current = "preferred"
            if remainder:
                buckets[current].append(remainder)
            continue

        matched, remainder = _match_section_heading(
            line,
            _NEUTRAL_HEADINGS,
        )
        if matched:
            current = "unknown"
            if remainder:
                buckets[current].append(remainder)
            continue

        buckets[current].append(line)

    return {
        key: "\n".join(lines)
        for key, lines in buckets.items()
    }


def extract_requirement_importance(text: str) -> dict[str, str]:
    """Classify explicit technology mentions by vacancy section.

    Priority:
        required > preferred > unknown
    """
    sections = _split_requirement_sections(text)
    required_text = _LANGUAGE_ALTERNATIVE_EXAMPLE.sub("", sections["required"])
    result: dict[str, str] = {}

    for spec in SKILLS:
        if _required_skill_in_section(required_text, spec):
            result[spec.name] = "required"
        elif _preferred_skill_in_section(required_text, spec) or _matches_skill(sections["preferred"], spec):
            result[spec.name] = "preferred"
        elif _matches_skill(text, spec):
            result[spec.name] = "unknown"

    return result


def extract_skill_alternatives(
    text: str, importance: str,
) -> tuple[tuple[str, ...], ...]:
    """Find isolated, explicit skill choices in a labelled section.

    A choice may wrap around an explicit ``or``/``или`` line break. A clause
    may contain two or more options, each separated by an explicit connector.
    A clause with additional skills or a repeated skill remains ungrouped.
    """
    if importance not in {"required", "preferred"}:
        return ()
    raw_lines = _split_requirement_sections(text)[importance].splitlines()
    merged_lines: list[str] = []
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            continue
        begins_connector = re.match(r"^(?:or|или)\b", line, flags=re.IGNORECASE)
        previous_ends_connector = bool(
            merged_lines
            and re.search(r"\b(?:or|или)$", merged_lines[-1], flags=re.IGNORECASE)
        )
        if merged_lines and (begins_connector or previous_ends_connector):
            merged_lines[-1] += " " + line
        else:
            merged_lines.append(line)
    section_lines = [
        clause.strip()
        for line in merged_lines
        for clause in re.split(r"(?<=[.;])\s+", line)
        if clause.strip()
    ]
    mentions = [
        tuple(spec.name for spec in SKILLS if _matches_skill(line, spec))
        for line in section_lines
    ]
    counts = {
        skill: sum(skill in line_skills for line_skills in mentions)
        for line_skills in mentions
        for skill in line_skills
    }
    groups: list[tuple[str, ...]] = []
    skill_specs = {spec.name: spec for spec in SKILLS}

    def explicit_options(expression: str, candidates: tuple[str, ...]) -> tuple[str, ...]:
        normalized = re.sub(r",\s*(?=(?:or|или)\b)", " ", expression, flags=re.IGNORECASE)
        if not re.search(r"\b(?:or|или)\b", normalized, flags=re.IGNORECASE):
            return ()
        options = [option.strip() for option in re.split(r"\b(?:or|или)\b|,\s*", normalized, flags=re.IGNORECASE)]
        if any(re.match(r"^(?:and|и)\b", option, flags=re.IGNORECASE) for option in options):
            return ()
        if len(options) != len(candidates):
            return ()
        option_skills = [
            [skill for skill in candidates if _matches_skill(option, skill_specs[skill])]
            for option in options
        ]
        return tuple(option[0] for option in option_skills) if all(len(option) == 1 for option in option_skills) else ()

    for line, line_skills in zip(section_lines, mentions):
        if len(line_skills) < 2 or any(counts[skill] != 1 for skill in line_skills):
            continue
        # Only word connectors count. A slash also occurs inside names such
        # as CI/CD and can mean a combined skill rather than a choice.
        whole_line_group = explicit_options(line, line_skills)
        if whole_line_group:
            groups.append(whole_line_group)
            # A pure OR chain already includes every option, even when some
            # are parenthesized. Adding inner groups would count them twice.
            continue
        # Parentheses let an explicit choice coexist with a separate skill in
        # the same clause. Keep the outer expression intact so a nested flat
        # OR chain is recognized as one choice instead of only its inner tail.
        parenthesized: list[tuple[int, int]] = []
        depth = 0
        start = -1
        for index, character in enumerate(line):
            if character == "(":
                if depth == 0:
                    start = index
                depth += 1
            elif character == ")" and depth:
                depth -= 1
                if depth == 0:
                    parenthesized.append((start, index))
        for start, end in parenthesized:
            expression = line[start + 1:end]
            candidates = tuple(
                skill for skill in line_skills
                if _matches_skill(expression, skill_specs[skill])
            )
            outside = line[:start] + line[end + 1:]
            repeated_outside = any(_matches_skill(outside, skill_specs[skill]) for skill in candidates)
            if len(candidates) >= 2 and not repeated_outside and all(counts[skill] == 1 for skill in candidates):
                parenthesized_group = explicit_options(expression, candidates)
                if parenthesized_group:
                    groups.append(parenthesized_group)
    return tuple(dict.fromkeys(groups))


def extract_technical_requirements(text: str) -> list[str]:
    """Return canonical technical skills explicitly mentioned by a vacancy.

    This is intentionally deterministic. It does not infer technologies that
    are not present in the vacancy text.
    """
    return [
        spec.name
        for spec in SKILLS
        if _matches_skill(text, spec)
    ]


def compare_facts(
    vacancy_text: str,
    facts: Iterable[CandidateFact],
) -> FactComparison:
    """Compare vacancy technology mentions with truth-only Candidate Facts.

    A skill receives the strongest *explicitly stored* experience type among
    matching active facts:

        commercial > lab > learning > unknown

    Missing means no active Candidate Fact mentions that skill at all.
    No type is upgraded or inferred from wording.
    """
    importance_by_skill = extract_requirement_importance(vacancy_text)

    active_facts = [
        fact
        for fact in facts
        if fact.active is not False
        and fact.deleted_at is None
    ]

    requirements: list[RequirementMatch] = []

    for spec in SKILLS:
        if spec.name not in importance_by_skill:
            continue

        importance = importance_by_skill[spec.name]

        matched_facts = [
            fact
            for fact in active_facts
            if _matches_skill(str(fact.value or ""), spec)
        ]

        if not matched_facts:
            requirements.append(
                RequirementMatch(
                    skill=spec.name,
                    status="missing",
                    importance=importance,
                )
            )
            continue

        typed: list[tuple[int, str, int]] = []

        for fact in matched_facts:
            experience_type = (
                normalize_experience_type(
                    str(fact.experience_type or "")
                )
                or "unknown"
            )
            typed.append(
                (
                    _EXPERIENCE_PRIORITY[experience_type],
                    experience_type,
                    int(fact.id or 0),
                )
            )

        typed.sort(reverse=True)
        best_priority = typed[0][0]
        best_type = typed[0][1]

        fact_ids = tuple(
            sorted(
                fact_id
                for priority, _, fact_id in typed
                if priority == best_priority and fact_id
            )
        )

        requirements.append(
            RequirementMatch(
                skill=spec.name,
                status=best_type,
                importance=importance,
                fact_ids=fact_ids,
            )
        )

    def valid_groups(importance: str) -> tuple[tuple[str, ...], ...]:
        return tuple(
            group
            for group in extract_skill_alternatives(vacancy_text, importance)
            if all(importance_by_skill.get(skill) == importance for skill in group)
        )

    return FactComparison(
        tuple(requirements),
        valid_groups("required"),
        valid_groups("preferred"),
    )
