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
