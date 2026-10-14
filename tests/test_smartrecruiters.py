import asyncio

import httpx
import pytest

from app.matching.fact_comparison import extract_requirement_importance
from app.sources.adapters.smartrecruiters import SmartRecruitersSource
from app.sources.base import SourceContext


def posting(posting_id="744000138376969", title="Application Support Engineer (Support Level 1)", **overrides):
    row = {
        "id": posting_id,
        "name": title,
        "location": {"country": "ge", "city": "Tbilisi", "remote": False, "hybrid": True},
        "postingUrl": f"https://jobs.smartrecruiters.com/Devexperts/{posting_id}-application-support-engineer",
        "releasedDate": "2026-07-17T16:36:52.830Z",
        "active": True,
        "visibility": "PUBLIC",
        "language": {"code": "en", "label": "English"},
        "jobAd": {"sections": {
            "companyDescription": {"title": "Company Description", "text": "<p>Market data technology.</p>"},
            "jobDescription": {"title": "Job Description", "text": "<p>Support international clients.</p>"},
            "qualifications": {"title": "Qualifications", "text": "<p>Required Qualifications</p><ul><li>Linux and Python basics.</li></ul>"},
            "additionalInformation": {
                "title": "Additional Information",
                "text": "<p>Possibility of hybrid/remote work mode in Georgia.</p><p>Georgian language courses for foreign employees.</p>",
            },
        }},
    }
    row.update(overrides)
    return row


def context(queries=None, targets=None):
    return SourceContext(user_id=1, current_country="RU", target_countries=targets or ["GE", "AM"], queries=queries or ["customer support"])


def response(url, payload, status=200):
    return httpx.Response(status, json=payload, request=httpx.Request("GET", url))


def test_smartrecruiters_preserves_country_hybrid_publication_and_unknown_hiring_support():
    job = SmartRecruitersSource.parse_payload({"content": [posting()]}, context())[0]

    assert job.source == "smartrecruiters"
    assert job.source_job_id == "Devexperts:744000138376969"
    assert job.company == "Devexperts"
    assert job.country == "GE"
    assert job.city == "Tbilisi"
    assert job.work_mode == "hybrid"
    assert job.remote_scope is None
    assert job.published_at == "2026-07-17T16:36:52.830000+00:00"
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert job.salary_from is None
    assert job.salary_to is None
    assert job.salary_currency is None
    assert "<p>" not in job.description
    assert job.raw["source_url"] == job.url
    assert job.raw["source_active"] is True
    assert job.raw["source_visibility"] == "PUBLIC"
    assert "availability" not in job.raw
    assert extract_requirement_importance(job.description)["Linux"] == "required"


def test_smartrecruiters_does_not_broaden_role_preferences_or_other_country_data():
    rows = [
        posting(),
        posting("2", title="Office Assistant"),
        posting("3", location={"country": "AM", "city": "Yerevan", "remote": True}),
        posting("4", location={"country": "US", "city": "Tbilisi", "remote": True}),
        posting("5", active=False),
        posting("6", visibility="INTERNAL"),
        posting("7", location={"city": "Tbilisi"}),
        posting(),
    ]
    assert len(SmartRecruitersSource.parse_payload({"content": rows}, context())) == 1
    assert SmartRecruitersSource.parse_payload({"content": rows}, context(["DevOps Engineer", "Linux Administrator"])) == []
    assert SmartRecruitersSource.parse_payload({"content": rows}, context(targets=["AM"])) == []


@pytest.mark.parametrize("location, expected, scope", [
    ({"country": "GE", "remote": True, "hybrid": False}, "remote", "Georgia"),
    ({"country": "GE", "remote": False, "hybrid": False}, "onsite", None),
    ({"country": "GE", "remote": True, "hybrid": True}, "hybrid", None),
    ({"country": "GE"}, None, None),
    ({"country": "GE", "remote": "false", "hybrid": "true"}, None, None),
])
def test_smartrecruiters_uses_explicit_structured_work_mode_without_prose_inference(location, expected, scope):
    job = SmartRecruitersSource.parse_payload({"content": [posting(location=location)]}, context())[0]
    assert job.work_mode == expected
    assert job.remote_scope == scope


def test_smartrecruiters_support_refusals_outrank_offers_and_prerequisites_stay_unknown():
    offered = posting("1")
    offered["jobAd"]["sections"]["additionalInformation"]["text"] = "We offer visa sponsorship and relocation assistance."
    refused = posting("2")
    refused["jobAd"]["sections"]["additionalInformation"]["text"] = "We offer visa sponsorship and relocation assistance. No visa sponsorship. We do not provide relocation assistance."
    unknown = posting("3")
    unknown["jobAd"]["sections"]["additionalInformation"]["text"] = "Candidates must already have the right to work. Visa sponsorship guidance is available. Relocation may be needed."
    jobs = SmartRecruitersSource.parse_payload({"content": [offered, refused, unknown]}, context())
    assert (jobs[0].visa_sponsorship, jobs[0].relocation) == (True, True)
    assert (jobs[1].visa_sponsorship, jobs[1].relocation) == (False, False)
    assert (jobs[2].visa_sponsorship, jobs[2].relocation) == (None, None)


@pytest.mark.parametrize("url", [
    "https://example.com/Devexperts/744000138376969",
    "http://jobs.smartrecruiters.com/Devexperts/744000138376969",
    "https://jobs.smartrecruiters.com/OtherCompany/744000138376969",
    "https://jobs.smartrecruiters.com/Devexperts/123456789",
    "https://user:password@jobs.smartrecruiters.com/Devexperts/744000138376969",
    "https://jobs.smartrecruiters.com:8080/Devexperts/744000138376969",
    "https://[invalid/Devexperts/744000138376969",
])
def test_smartrecruiters_rejects_untrusted_or_mismatched_posting_links(url):
    assert SmartRecruitersSource.parse_payload({"content": [posting(postingUrl=url)]}, context()) == []


@pytest.mark.parametrize("date", [None, True, "yesterday", "2026-07-17T16:36:52"])
def test_smartrecruiters_does_not_guess_a_publication_date(date):
    job = SmartRecruitersSource.parse_payload({"content": [posting(releasedDate=date)]}, context())[0]
    assert job.published_at is None


def test_smartrecruiters_unknown_active_status_is_not_a_refusal_or_positive_claim():
    row = posting()
    row.pop("active")
    job = SmartRecruitersSource.parse_payload({"content": [row]}, context())[0]
    assert job.raw["source_active"] is None


def test_smartrecruiters_discovery_uses_bounded_public_country_list_and_owned_detail_urls(monkeypatch):
    calls = []
    summaries = [posting(str(index)) for index in range(20)]
    summaries.append(posting("999", title="Unrelated product analyst"))
    summaries[0]["ref"] = "https://127.0.0.1/private"

    async def get(self, url, **kwargs):
        calls.append((url, kwargs))
        if url == SmartRecruitersSource.endpoint:
            return response(url, {"totalFound": 2000, "content": summaries})
        return response(url, posting(url.rsplit("/", 1)[-1]))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(SmartRecruitersSource().discover(context()))
    assert len(jobs) == SmartRecruitersSource.max_details
    assert len(calls) == 1 + SmartRecruitersSource.max_details
    assert calls[0][1]["params"] == {"country": "ge", "destination": "PUBLIC", "offset": 0, "limit": 100}
    assert all(url.startswith(SmartRecruitersSource.endpoint) for url, _ in calls)
    assert not SmartRecruitersSource.capabilities.apply
    assert not SmartRecruitersSource.capabilities.messages


def test_smartrecruiters_does_not_request_an_unselected_country(monkeypatch):
    async def get(*args, **kwargs):
        raise AssertionError("an AM-only profile must not request the Georgian employer feed")

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    assert asyncio.run(SmartRecruitersSource().discover(context(targets=["AM"]))) == []


def test_smartrecruiters_transport_retry_is_bounded_and_recovers(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise httpx.ConnectError("temporary connection failure", request=httpx.Request("GET", url))
        return response(url, {"content": []})

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    assert asyncio.run(SmartRecruitersSource().discover(context())) == []
    assert calls == [SmartRecruitersSource.endpoint] * 2


@pytest.mark.parametrize("status", [403, 429])
def test_smartrecruiters_http_failures_are_not_retried(monkeypatch, status):
    calls = []

    async def get(self, url, **kwargs):
        calls.append(url)
        return response(url, {}, status)

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(SmartRecruitersSource().discover(context()))
    assert len(calls) == 1


def test_smartrecruiters_partial_detail_failure_preserves_other_successes(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append(url)
        if url == SmartRecruitersSource.endpoint:
            return response(url, {"content": [posting("1"), posting("2"), posting("3")]})
        if url.endswith("/1"):
            raise httpx.ReadTimeout("detail unavailable", request=httpx.Request("GET", url))
        if url.endswith("/2"):
            return response(url, posting("2", active=False))
        return response(url, posting("3"))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    source = SmartRecruitersSource()
    jobs = asyncio.run(source.discover(context()))
    assert source.partial_failures == 1
    assert source.retry_count == 1
    assert source.discovery_diagnostics[0]["code"] == "NETWORK_READ_TIMEOUT"
    assert [job.source_job_id for job in jobs] == ["Devexperts:3"]
    assert calls.count(f"{SmartRecruitersSource.endpoint}/1") == 2


def test_smartrecruiters_all_detail_failures_raise_source_error(monkeypatch):
    async def get(self, url, **kwargs):
        if url == SmartRecruitersSource.endpoint:
            return response(url, {"content": [posting("1")]})
        return response(url, {}, 404)

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(SmartRecruitersSource().discover(context()))


def test_smartrecruiters_discovery_has_a_whole_source_timeout(monkeypatch):
    async def hanging(self, context, verified_jobs):
        await asyncio.Event().wait()

    monkeypatch.setattr(SmartRecruitersSource, "_discover", hanging)
    monkeypatch.setattr(SmartRecruitersSource, "discovery_timeout_seconds", 0.01)
    with pytest.raises(TimeoutError):
        asyncio.run(SmartRecruitersSource().discover(context()))


def test_smartrecruiters_budget_expiry_preserves_prior_verified_details(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append(url)
        if url == SmartRecruitersSource.endpoint:
            return response(url, {"content": [posting("1"), posting("2"), posting("3")]})
        if url.endswith("/1"):
            return response(url, posting("1"))
        await asyncio.Event().wait()

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr(SmartRecruitersSource, "discovery_timeout_seconds", 0.01)
    jobs = asyncio.run(SmartRecruitersSource().discover(context()))
    assert [job.source_job_id for job in jobs] == ["Devexperts:1"]
    assert calls == [SmartRecruitersSource.endpoint, f"{SmartRecruitersSource.endpoint}/1", f"{SmartRecruitersSource.endpoint}/2"]


@pytest.mark.parametrize("first_detail", [posting("1", active=False), posting("1", postingUrl="https://example.com/untrusted")])
def test_smartrecruiters_budget_expiry_without_usable_details_raises_instead_of_empty_success(monkeypatch, first_detail):
    async def get(self, url, **kwargs):
        if url == SmartRecruitersSource.endpoint:
            return response(url, {"content": [posting("1"), posting("2")]})
        if url.endswith("/1"):
            return response(url, first_detail)
        await asyncio.Event().wait()

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr(SmartRecruitersSource, "discovery_timeout_seconds", 0.01)
    with pytest.raises(TimeoutError):
        asyncio.run(SmartRecruitersSource().discover(context()))


def test_smartrecruiters_external_cancellation_does_not_become_partial_success(monkeypatch):
    async def run():
        waiting = asyncio.Event()

        async def get(self, url, **kwargs):
            if url == SmartRecruitersSource.endpoint:
                return response(url, {"content": [posting("1"), posting("2")]})
            if url.endswith("/1"):
                return response(url, posting("1"))
            waiting.set()
            await asyncio.Event().wait()

        monkeypatch.setattr(httpx.AsyncClient, "get", get)
        task = asyncio.create_task(SmartRecruitersSource().discover(context()))
        await waiting.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())


def test_smartrecruiters_rejects_malformed_feed_and_detail_contracts():
    with pytest.raises(ValueError, match="contract unavailable"):
        SmartRecruitersSource.parse_payload({"error": "not a feed"}, context())
    with pytest.raises(ValueError, match="details contract unavailable"):
        SmartRecruitersSource.parse_payload({"content": [posting(jobAd={})]}, context())
