import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

import app.sources.adapters.jobbank as jobbank_module
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
SEARCH_TWO_JOBS = '''<div id="results-list-content">
<a class="resultJobItem" href="/jobsearch/jobpostingtfw/123"><span class="noctitle">warehouse worker</span></a>
<a class="resultJobItem" href="/jobsearch/jobpostingtfw/456"><span class="noctitle">network technician</span></a>
</div>'''


def detail(text, eligibility=""):
    return f'<div class="job-posting-details-body"><p>{text}</p><div class="job-posting-detail-apply">{eligibility}</div></div>'


def job():
    return JobBankSource.parse_search(SEARCH)[0]


@pytest.fixture(autouse=True)
def reset_jobbank_request_clock(monkeypatch):
    monkeypatch.setattr(jobbank_module, "_LAST_REQUEST_STARTED", None)


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
    assert sleep.await_count == 2
    assert all(call.args[0] == pytest.approx(5, abs=0.01) for call in sleep.await_args_list)
    assert calls[0][1]["params"]["fglo"] == "1"


def test_fetch_retries_transport_failure_once_and_keeps_request_delay(monkeypatch):
    class Client:
        calls = 0

        async def get(self, url, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise httpx.ConnectTimeout("temporary connect timeout")
            return httpx.Response(200, text="ok", request=httpx.Request("GET", url))

    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)

    client = Client()
    assert asyncio.run(JobBankSource()._fetch(client, "https://example.test/job")) == "ok"
    assert client.calls == 2
    sleep.assert_awaited_once()
    assert sleep.await_args.args[0] == pytest.approx(5, abs=0.01)


def test_fetch_does_not_retry_http_status_errors(monkeypatch):
    class Client:
        calls = 0

        async def get(self, url, **kwargs):
            self.calls += 1
            return httpx.Response(503, request=httpx.Request("GET", url))

    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)
    client = Client()

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(JobBankSource()._fetch(client, "https://example.test/job"))
    assert client.calls == 1
    sleep.assert_not_awaited()


def test_fetch_stops_after_one_failed_transport_retry(monkeypatch):
    class Client:
        calls = 0

        async def get(self, url, **kwargs):
            self.calls += 1
            raise httpx.ReadTimeout("temporary read timeout")

    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)
    client = Client()

    with pytest.raises(httpx.ReadTimeout):
        asyncio.run(JobBankSource()._fetch(client, "https://example.test/job"))
    assert client.calls == 2
    sleep.assert_awaited_once()
    assert sleep.await_args.args[0] == pytest.approx(5, abs=0.01)


def test_discovery_preserves_verified_jobs_when_one_detail_times_out(monkeypatch):
    calls = []

    async def get(client, url, **kwargs):
        calls.append(url)
        if url.endswith("/jobsearch/jobsearch"):
            text = SEARCH_TWO_JOBS
        elif url.endswith("/123"):
            raise httpx.ReadTimeout("temporary detail timeout")
        else:
            text = detail("Network support duties")
        return httpx.Response(200, text=text, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)

    jobs = asyncio.run(JobBankSource().discover(SourceContext(1, queries=["warehouse worker"])))

    assert [item.source_job_id for item in jobs] == ["456"]
    assert calls.count("https://www.jobbank.gc.ca/jobsearch/jobpostingtfw/123") == 2
    assert sleep.await_count == 3
    assert all(call.args[0] == pytest.approx(5, abs=0.01) for call in sleep.await_args_list)


def test_discovery_reports_detail_failure_when_no_detail_was_verified(monkeypatch):
    calls = []

    async def get(client, url, **kwargs):
        calls.append(url)
        if url.endswith("/jobsearch/jobsearch"):
            return httpx.Response(200, text=SEARCH_TWO_JOBS, request=httpx.Request("GET", url))
        raise httpx.ConnectTimeout("temporary connection timeout")

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    sleep = AsyncMock()
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", sleep)

    with pytest.raises(httpx.ConnectTimeout):
        asyncio.run(JobBankSource().discover(SourceContext(1, queries=["warehouse worker"])))

    assert len(calls) == 5  # one search plus two attempts for each detail
    assert sleep.await_count == 4


@pytest.mark.parametrize(
    ("request_duration", "expected_gap", "expected_wait"),
    [(2, 5, 3), (6, 6, 0)],
)
def test_fetch_enforces_start_interval_without_idle_wait(monkeypatch, request_duration, expected_gap, expected_wait):
    now = [0.0]
    starts = []
    waits = []

    async def sleep(delay):
        waits.append(delay)
        now[0] += delay

    class Client:
        async def get(self, url, **kwargs):
            starts.append(now[0])
            now[0] += request_duration
            return httpx.Response(200, text="ok", request=httpx.Request("GET", url))

    monkeypatch.setattr(jobbank_module, "_monotonic", lambda: now[0])
    monkeypatch.setattr(jobbank_module.asyncio, "sleep", sleep)
    client = Client()
    source = JobBankSource()

    async def fetch_twice():
        await source._fetch(client, "https://example.test/first")
        await source._fetch(client, "https://example.test/second")

    asyncio.run(fetch_twice())

    assert starts == pytest.approx([0, expected_gap])
    if expected_wait:
        assert waits == pytest.approx([expected_wait])
    else:
        assert waits == []


def test_concurrent_fetches_remain_serialized(monkeypatch):
    async def no_wait(delay):
        return None

    monkeypatch.setattr(jobbank_module, "_wait_for_request_slot", no_wait)
    client_started = asyncio.Event()
    release_first = asyncio.Event()

    class Client:
        calls = 0
        active = 0
        max_active = 0

        async def get(self, url, **kwargs):
            self.calls += 1
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            if self.calls == 1:
                client_started.set()
                await release_first.wait()
            self.active -= 1
            return httpx.Response(200, text="ok", request=httpx.Request("GET", url))

    async def run():
        client = Client()
        source = JobBankSource()
        first = asyncio.create_task(source._fetch(client, "https://example.test/first"))
        await client_started.wait()
        second = asyncio.create_task(source._fetch(client, "https://example.test/second"))
        await asyncio.sleep(0)
        assert client.calls == 1
        release_first.set()
        await asyncio.gather(first, second)
        assert client.max_active == 1

    asyncio.run(run())


def test_discovery_continues_after_a_query_transport_failure(monkeypatch):
    calls_by_query = {}

    async def get(client, url, **kwargs):
        if url.endswith("/jobsearch/jobsearch"):
            query = kwargs["params"]["searchstring"]
            calls_by_query[query] = calls_by_query.get(query, 0) + 1
            if query == "first" and calls_by_query[query] <= 2:
                raise httpx.ConnectTimeout("temporary connection timeout")
            text = "<div id=\"results-list-content\"></div>" if query == "first" else SEARCH
        else:
            text = detail("Network support duties")
        return httpx.Response(200, text=text, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr("app.sources.adapters.jobbank.asyncio.sleep", AsyncMock())

    jobs = asyncio.run(JobBankSource().discover(SourceContext(1, queries=["first", "second"])))

    assert [item.source_job_id for item in jobs] == ["123"]
    assert calls_by_query == {"first": 2, "second": 1}
