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
    SkillSpec("systemd", ("systemd",)),
    SkillSpec("Docker", ("docker",)),
    SkillSpec("Docker Compose", ("docker compose", "docker-compose")),
    SkillSpec("Kubernetes", ("kubernetes", "k8s")),
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


_REQUIRED_HEADINGS = (
    "требования к кандидатам",
    "обязательные требования",
    "требования",
    "что мы ожидаем",
    "мы ожидаем",
    "необходимо",
    "requirements",
    "must have",
    "must-have",
    "required",
    "what we expect",
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
    "preferred",
    "preferred qualifications",
    "bonus",
    "would be a plus",
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


def _match_section_heading(
    line: str,
    headings: tuple[str, ...],
) -> tuple[bool, str]:
    for heading in sorted(headings, key=len, reverse=True):
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

    for raw_line in (text or "").splitlines():
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
    result: dict[str, str] = {}

    for spec in SKILLS:
        if _matches_skill(sections["required"], spec):
            result[spec.name] = "required"
        elif _matches_skill(sections["preferred"], spec):
            result[spec.name] = "preferred"
        elif _matches_skill(text, spec):
            result[spec.name] = "unknown"

    return result


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
        if getattr(fact, "active", True) is not False
        and getattr(fact, "deleted_at", None) is None
    ]

    requirements: list[RequirementMatch] = []

    for spec in SKILLS:
        if spec.name not in importance_by_skill:
            continue

        importance = importance_by_skill[spec.name]

        matched_facts = [
            fact
            for fact in active_facts
            if _matches_skill(str(getattr(fact, "value", "") or ""), spec)
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
                    str(getattr(fact, "experience_type", "") or "")
                )
                or "unknown"
            )
            typed.append(
                (
                    _EXPERIENCE_PRIORITY[experience_type],
                    experience_type,
                    int(getattr(fact, "id", 0) or 0),
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

    return FactComparison(tuple(requirements))
