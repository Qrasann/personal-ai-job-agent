from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import _candidate_commercial_years, _required_experience_years, score_job


def _search():
    return SearchProfile(
        id=1,
        profile_id=1,
        settings={
            "queries": ["DevOps Engineer"],
            "preferred_terms": ["linux", "docker"],
            "strong_terms": ["linux", "docker"],
            "modes": {
                "local_ru": True,
                "remote_international": False,
                "relocation": False,
            },
        },
    )


def test_learning_years_do_not_count_as_commercial_experience():
    facts = [
        CandidateFact(
            profile_id=1,
            value="More than five years of Linux learning",
            experience_type="learning",
        )
    ]
    assert _candidate_commercial_years(facts) is None

def test_candidate_experience_explains_three_year_stretch():
    facts = [
        CandidateFact(
            profile_id=1,
            value="More than two years of system administration experience with Windows and Linux.",
            experience_type="commercial",
        )
    ]
    job = Job(
        fingerprint="experience-stretch",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker. Требуется опыт от 3 лет.",
        country="RU",
    )

    result = score_job(job, _search(), facts, [])

    assert result.fit == "stretch"
    assert "commercial 2+" in result.reason
    assert "требуется 3+" in result.reason

def test_required_experience_uses_strictest_explicit_requirement():
    job = Job(
        fingerprint="experience-multiple",
        title="DevOps Engineer",
        company="ACME",
        description="Опыт Linux от 1 года. Для позиции требуется опыт от 3 лет.",
        country="RU",
    )

    assert _required_experience_years(job) == 3

def test_minimum_experience_wording_extracts_years_from_qualification_sections():
    job = Job(
        fingerprint="experience-minimum-qualifications",
        title="Infrastructure Engineer",
        company="ACME",
        description=(
            "Necessary Qualifications:\n"
            "Minimum 3 years of hands-on Linux system administration experience.\n"
            "Minimum 2 years of hands-on AWS production experience."
        ),
        country="GE",
    )

    assert _required_experience_years(job) == 3
    result = score_job(
        job,
        _search(),
        [
            CandidateFact(
                profile_id=1,
                value="2 years of Linux system administration",
                experience_type="commercial",
            )
        ],
        [],
    )
    assert result.fit == "stretch"
    assert "требуется 3+" in result.reason


def test_preferred_experience_band_does_not_raise_required_fit_threshold():
    job = Job(
        fingerprint="experience-preferred-band",
        title="DevOps Engineer",
        company="ACME",
        description="Minimum 3 years of production experience required. 5 years of experience preferred.",
        country="DE",
    )

    assert _required_experience_years(job) == 3
    result = score_job(
        job,
        _search(),
        [CandidateFact(
            profile_id=1,
            value="2 years of commercial DevOps experience",
            experience_type="commercial",
        )],
        [],
    )
    assert result.fit == "stretch"
    assert "требуется 3+" in result.reason


def test_preferred_only_experience_band_is_not_a_required_minimum():
    job = Job(
        fingerprint="experience-preferred-only",
        title="DevOps Engineer",
        company="ACME",
        description="5 years of experience preferred.",
        country="DE",
    )

    assert _required_experience_years(job) is None


def test_preferred_five_plus_years_does_not_trigger_high_experience_skip():
    job = Job(
        fingerprint="experience-preferred-five-plus",
        title="DevOps Engineer",
        company="ACME",
        description="Minimum 3 years of experience required. 5+ years of experience preferred.",
        country="RU",
    )
    facts = [CandidateFact(
        profile_id=1,
        value="2 years of commercial DevOps experience",
        experience_type="commercial",
    )]

    result = score_job(job, _search(), facts, [])

    assert _required_experience_years(job) == 3
    assert result.fit == "stretch"
    assert "высокого опыта" not in result.reason


def test_preferred_only_five_plus_years_keeps_good_fit():
    job = Job(
        fingerprint="experience-only-preferred-five-plus",
        title="DevOps Engineer",
        company="ACME",
        description="5+ years of experience preferred.",
        country="RU",
    )

    assert _required_experience_years(job) is None
    assert score_job(job, _search(), [], []).fit == "good"


def test_more_than_five_years_required_keeps_high_experience_restriction():
    job = Job(
        fingerprint="experience-more-than-five",
        title="DevOps Engineer",
        company="ACME",
        description="More than 5 years of experience required.",
        country="RU",
    )

    assert _required_experience_years(job) == 5
    result = score_job(job, _search(), [], [])
    assert result.fit == "skip"
    assert "высокого опыта" in result.reason
