from types import SimpleNamespace

import pytest

from app.database.models import Job, SearchProfile
from app.domain.jobs import NormalizedJob
from app.domain.source_posting import snapshot_source_posting, source_posting_view
from app.matching.engine import MATCH_ASSESSMENT_VERSION, score_job
from app.services import _match_lane


@pytest.mark.parametrize("excluded_term", ["betting", "gambling"])
def test_employer_watch_industry_tag_excludes_betsson_before_review_or_notification(excluded_term):
    normalized = NormalizedJob(
        source="employer_career_watch",
        source_job_id="betsson-group:8200701",
        title="Platform Core DevOps Engineer - Infra",
        company="Betsson Group",
        description="Kubernetes, Kafka and infrastructure as code",
        country="MT",
        raw={"industry_tags": ["betting", "gambling"]},
    )
    source_ref = SimpleNamespace(raw={
        **normalized.raw,
        "normalized_posting_v1": snapshot_source_posting(normalized),
    })
    job = source_posting_view(Job(
        fingerprint=normalized.canonical_fingerprint(),
        title=normalized.title,
        company=normalized.company,
        description=normalized.description,
        country=normalized.country,
    ), source_ref)
    search = SearchProfile(id=1, profile_id=1, settings={
        "queries": ["DevOps Engineer"],
        "exclude_terms": [excluded_term],
        "modes": {"local_ru": True, "remote_international": True, "relocation": True},
    })

    result = score_job(job, search, [], [])

    assert MATCH_ASSESSMENT_VERSION == 2
    assert result.total_score == 0
    assert result.fit == "skip"
    assert "Исключено по фильтру" in result.reason
    assert _match_lane(result, 60) == "filtered"
