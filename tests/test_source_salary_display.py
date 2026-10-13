import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services
from app.database.models import Job, SearchProfile
from app.matching.engine import score_job
from app.sources.adapters.jobbank import JobBankSource
from app.telegram.vacancy_view import render_job_details


def job_and_match():
    job = Job(
        id=1, fingerprint="source-salary", title="Warehouse worker", company="Example",
        description="Warehouse duties", country="CA", work_mode="onsite",
    )
    match = SimpleNamespace(
        profile_id=2, search_profile_id=4, total_score=60, technical_score=70,
        geography_score=50, salary_score=58, relocation_score=42, reason="",
    )
    return job, match


def render(evidence, *, job=None):
    default_job, match = job_and_match()
    return render_job_details({
        "job": job or default_job, "match": match, "source": "jobbank",
        "details": {"source_salary_text": evidence},
    })


def test_jobbank_decimal_hourly_salary_survives_details_without_numeric_inference(monkeypatch):
    parsed = JobBankSource.parse_search('''
        <div id="results-list-content"><a class="resultJobItem" href="/jobsearch/jobpostingtfw/123">
        <span class="noctitle">warehouse worker</span><li class="salary">Salary $20.50 hourly</li>
        </a></div>''')[0]
    job, match = job_and_match()
    ref = SimpleNamespace(source_id="jobbank", url=parsed.url, raw=parsed.raw)
    monkeypatch.setattr(services.repo, "get_match_for_user_job", AsyncMock(return_value=match))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=job))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=ref))
    refresh = AsyncMock(return_value=match)
    monkeypatch.setattr(services, "refresh_match_score", refresh)
    monkeypatch.setattr(services.repo, "list_search_profiles", AsyncMock(return_value=[
        SimpleNamespace(id=4, name="Relocation-first"),
    ]))

    before = score_job(job, SearchProfile(settings={"minimum_salary": {"USD": 3000}}), [], [])
    payload = asyncio.run(services.get_vacancy_details(7, 1, search_profile_id=4))
    text = render_job_details(payload)
    after = score_job(job, SearchProfile(settings={"minimum_salary": {"USD": 3000}}), [], [])

    assert "💰 по источнику: Salary $20.50 hourly" in text
    assert "Источник: <b>JOBBANK</b>" in text
    assert "2 050" not in text and "USD" not in text and "в месяц" not in text
    assert payload["fallback_salary_text"] == ""
    assert (job.salary_from, job.salary_to, job.salary_currency, job.salary_period) == (None,) * 4
    assert before == after
    assert before.salary_score == 58
    refresh.assert_awaited_once_with(match, job, technical_text="Warehouse duties")


@pytest.mark.parametrize("evidence", [None, "", "  ", 2050, True, [], {"amount": 20.5}])
def test_invalid_salary_evidence_is_not_stringified(evidence):
    assert "💰 не указана" in render(evidence)
    assert "по источнику:" not in render(evidence)


def test_source_salary_html_is_cleaned_escaped_and_bounded():
    text = render("<b>CAD 20.50–25.75/hour &amp; bonus</b> " + "x" * 10000)
    line = next(line for line in text.splitlines() if line.startswith("💰"))
    assert "CAD 20.50–25.75/hour &amp; bonus" in line
    assert "<b>CAD" not in line
    assert len(line) < 270
    assert line.endswith("…")


def test_source_salary_text_does_not_override_structured_salary():
    job, _ = job_and_match()
    job.salary_from, job.salary_currency, job.salary_period = 3000, "USD", "monthly"
    text = render("Salary $20.50 hourly", job=job)
    assert "💰 от 3 000 $ в месяц" in text
    assert "по источнику:" not in text
