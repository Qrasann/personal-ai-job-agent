from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import score_job
from app.matching.technical_score import score_technical_v2


def _fact(skill: str, experience_type: str, *, fact_id: int = 1, active: bool = True, deleted=False):
    fact = CandidateFact(
        id=fact_id,
        profile_id=1,
        value=skill,
        experience_type=experience_type,
        active=active,
    )
    if deleted:
        from app.database.time_utils import utcnow_naive
        fact.deleted_at = utcnow_naive()
    return fact


def _search():
    return SearchProfile(
        id=1,
        profile_id=1,
        settings={
            "queries": ["DevOps Engineer"],
            "preferred_terms": ["linux", "docker", "nginx"],
            "strong_terms": ["linux", "docker"],
            "exclude_terms": ["gambling"],
            "modes": {
                "local_ru": True,
                "remote_international": True,
                "relocation": True,
            },
            "minimum_salary": {"RUR": 100000},
        },
    )


def test_required_commercial_is_full_technical_match():
    text = "Требования:\nLinux"
    assert score_technical_v2(text, [_fact("Linux", "commercial")]) == 100


def test_required_experience_levels_have_strict_order():
    text = "Требования\nLinux"

    commercial = score_technical_v2(text, [_fact("Linux", "commercial")])
    lab = score_technical_v2(text, [_fact("Linux", "lab")])
    unknown = score_technical_v2(text, [_fact("Linux", "unknown")])
    learning = score_technical_v2(text, [_fact("Linux", "learning")])
    missing = score_technical_v2(text, [])

    assert (commercial, lab, unknown, learning, missing) == (100, 75, 60, 40, 0)


def test_required_partial_coverage_is_proportional():
    text = """Требования:
Linux
Docker
Kubernetes
Nginx
"""
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]
    assert score_technical_v2(text, facts) == 54


def test_preferred_requirements_cannot_compensate_for_missing_required():
    text = """Требования:
Linux
Приветствуется:
Docker
"""
    facts = [_fact("Docker", "commercial")]
    assert score_technical_v2(text, facts) == 15


def test_missing_preferred_requirement_only_reduces_small_bonus_lane():
    text = """Требования:
Linux
Приветствуется:
Docker
"""
    facts = [_fact("Linux", "commercial")]
    assert score_technical_v2(text, facts) == 85


def test_unknown_responsibility_signals_do_not_change_structured_score():
    text = """Обязанности:
Docker
Требования:
Linux
"""
    without_docker = [_fact("Linux", "commercial")]
    with_docker = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "commercial", fact_id=2),
    ]

    assert score_technical_v2(text, without_docker) == 100
    assert score_technical_v2(text, with_docker) == 100


def test_no_required_section_requests_legacy_fallback():
    assert score_technical_v2(
        "Linux Docker Nginx",
        [_fact("Linux Docker Nginx", "commercial")],
    ) is None

    assert score_technical_v2(
        "Приветствуется:\nDocker",
        [_fact("Docker", "commercial")],
    ) is None


def test_inactive_and_deleted_facts_are_not_counted():
    text = "Требования:\nLinux"
    facts = [
        _fact("Linux", "commercial", fact_id=1, active=False),
        _fact("Linux", "commercial", fact_id=2, deleted=True),
    ]
    assert score_technical_v2(text, facts) == 0


def test_skill_present_in_required_and_preferred_is_counted_as_required_only():
    text = """Требования:
Linux
Приветствуется:
Linux
Docker
"""
    facts = [_fact("Linux", "commercial")]
    # Linux is required (priority required > preferred), Docker is preferred and missing.
    assert score_technical_v2(text, facts) == 85


def test_score_job_uses_v2_for_structured_requirements():
    job = Job(
        fingerprint="structured-v2",
        title="DevOps Engineer",
        company="ACME",
        description="""Требования:
Linux
Docker
Приветствуется:
Kubernetes
""",
        country="RU",
        salary_to=150000,
        salary_currency="RUR",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]

    result = score_job(job, _search(), facts, [])

    assert result.technical_score == 80
    assert result.geography_score == 95
    assert result.salary_score == 100
    assert result.relocation_score == 50


def test_score_job_keeps_legacy_technical_fallback_for_unstructured_jobs():
    job = Job(
        fingerprint="legacy-fallback",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "commercial", fact_id=2),
    ]

    result = score_job(job, _search(), facts, [])

    assert result.technical_score == 86


def test_score_job_can_use_full_details_for_technical_only():
    job = Job(
        fingerprint="full-details-override",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker DevOps Engineer",
        country="RU",
        salary_to=150000,
        salary_currency="RUR",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]
    full_text = """Требования:
Linux
Docker
Приветствуется:
Kubernetes
"""

    result = score_job(
        job,
        _search(),
        facts,
        [],
        technical_text=full_text,
    )

    assert result.technical_score == 80
    assert result.geography_score == 95
    assert result.salary_score == 100
    assert result.relocation_score == 50


def test_structured_required_and_preferred_can_score_exactly_zero():
    text = "Требования:\nLinux\nПриветствуется:\nDocker\n"
    assert score_technical_v2(text, []) == 0

def test_score_job_classifies_good_stretch_and_skip():
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
    ]
    good = Job(fingerprint="fit-good", title="DevOps Engineer", company="ACME", description="Опыт 1–3 года. Linux Docker", country="RU")
    stretch = Job(fingerprint="fit-stretch", title="DevOps Engineer", company="ACME", description="Опыт 3–6 лет. Linux Docker", country="RU")
    senior = Job(fingerprint="fit-senior", title="Senior DevOps Engineer", company="ACME", description="Linux Docker", country="RU")
    high_exp = Job(fingerprint="fit-5plus", title="DevOps Engineer", company="ACME", description="Опыт от 5 лет. Linux Docker", country="RU")

    assert score_job(good, _search(), facts, []).fit == "good"
    assert score_job(stretch, _search(), facts, []).fit == "stretch"
    assert score_job(senior, _search(), facts, []).fit == "skip"
    assert score_job(high_exp, _search(), facts, []).fit == "skip"
