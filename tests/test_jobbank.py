import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from app.sources.adapters.jobbank import JobBankSource
from app.sources.base import SourceContext
from app.search.preferences import _signals
from app.geo.countries import normalize_country
from app.sources.registry import build_source_plan, source_capabilities


SEARCH = '''<div id="results-list-content"><a class="resultJobItem"
href="/jobsearch/jobpostingtfw/123;jsessionid=private?source=searchresults">
<span class="noctitle">warehouse worker</span><li class="business">Example</li>
<li class="location">Location Toronto (ON)</li><li class="salary">Salary $20.50 hourly</li>
<span class="jobLMIAflag">LMIA requested</span></a></div>'''


def detail(text, eligibility=""):
    return f'<div class="job-posting-details-body"><p>{text}</p><div class="job-posting-detail-apply">{eligibility}</div></div>'


def job():
    return JobBankSource.parse_search(SEARCH)[0]


def test_search_strips_session_and_preserves_explicit_salary():
    item = job()
    assert item.url == "https://www.jobbank.gc.ca/jobsearch/jobpostingtfw/123"
    assert item.source_job_id == "123"
    assert item.country == "CA"
    assert item.city == "Toronto (ON)"
    assert item.raw["source_salary_text"] == "Salary $20.50 hourly"
    assert "salary_text" not in item.raw
    assert item.salary_from is None


def test_lmia_request_is_not_sponsorship_or_work_permit_support():
    item = JobBankSource.enrich(job(), detail("LMIA requested. Employer applied to hire a temporary foreign worker."))
    assert item.visa_sponsorship is None
    assert item.raw["international_candidates"] is None
    assert not any(_signals(item).values())


def test_explicit_eligibility_restriction_overrides_lmia_and_support():
    item = JobBankSource.enrich(job(), detail("We offer visa sponsorship.", "Do not apply if you are not authorized to work in Canada"))
    assert item.raw["international_candidates"] is False
    assert item.visa_sponsorship is False
    assert not any(_signals(item).values())


def test_international_eligibility_does_not_imply_sponsorship():
    item = JobBankSource.enrich(job(), detail("LMIA requested.", "Other candidates, with or without a valid Canadian work permit."))
    assert item.raw["international_candidates"] is True
    assert item.visa_sponsorship is None
    assert not any(_signals(item).values())


def test_explicit_support_keeps_evidence_and_url():
    item = JobBankSource.enrich(job(), detail("We provide visa sponsorship. We offer relocation assistance."))
    assert item.visa_sponsorship is True
    assert item.relocation is True
    assert item.raw["support_evidence"]["visa_sponsorship"] == "We provide visa sponsorship"
    assert item.raw["evidence_url"] == item.url
    assert _signals(item)["visa_sponsorship"] is True


def test_negated_or_incidental_support_does_not_count():
    item = JobBankSource.enrich(job(), detail("No visa sponsorship. You must obtain a work permit. Relocation support is not available."))
    assert item.visa_sponsorship is False
    assert item.relocation is False
    assert not any(_signals(item).values())


def test_explicit_refusal_overrides_support_offer():
    item = JobBankSource.enrich(job(), detail("We offer visa sponsorship guidance. Visa sponsorship is not available."))
    assert item.visa_sponsorship is False
    assert not any(_signals(item).values())


def test_sponsorship_guidance_is_not_an_offer():
    item = JobBankSource.enrich(job(), detail("We offer visa sponsorship guidance. We provide relocation support information."))
    assert item.visa_sponsorship is None
    assert item.relocation is None


@pytest.mark.parametrize("parser", [JobBankSource.parse_search, lambda html: JobBankSource.enrich(job(), html)])
def test_service_error_is_not_empty_success(parser):
    with pytest.raises(ValueError, match="contract unavailable"):
        parser("<html>Service unavailable</html>")


def test_country_and_source_registration():
    assert normalize_country("Канада") == "CA"
    plans = build_source_plan("RU", ["CA"])
    assert next(p for p in plans if p.source_id == "jobbank").implemented
    assert not source_capabilities("jobbank").apply


def test_discovery_dedupes_queries_and_excludes_restricted_candidates(monkeypatch):
    calls = []
    async def get(client, url, **kwargs):
        calls.append((url, kwargs))
        text = SEARCH if url.endswith("jobsearch") else detail("LMIA requested", "Do not apply if you are not authorized to work in Canada")
        return httpx.Response(200, text=text, request=httpx.Request("GET", url))
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)
    assert asyncio.run(JobBankSource().discover(SourceContext(1, queries=["warehouse", "worker"]))) == []
    assert len(calls) == 3
    assert sleep.await_count == 3
    assert all(call.args == (5,) for call in sleep.await_args_list)
    assert calls[0][1]["params"]["fglo"] == "1"
