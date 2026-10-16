import asyncio

import httpx
import pytest

from app.sources.adapters.arbeitnow import ArbeitnowSource
from app.sources.base import SourceContext
from app.search.preferences import vacancy_allowed
from app.domain.relocation_evidence import build_relocation_evidence


def test_arbeitnow_maps_german_role_aliases_and_explicit_support():
    payload = {
        "data": [
            {
                "slug": "lager-1",
                "company_name": "Example GmbH",
                "title": "Lagermitarbeiter (m/w/d)",
                "description": "<p>Visa support and relocation assistance are provided.</p>",
                "url": "https://example.invalid/lager-1",
                "location": "Berlin",
                "remote": False,
                "tags": ["Logistik"],
                "created_at": 1791676800,
            },
            {
                "slug": "developer-1",
                "company_name": "Example GmbH",
                "title": "Senior Software Developer",
                "description": "Python",
                "url": "https://example.invalid/developer-1",
                "location": "Munich",
                "remote": True,
                "tags": ["Software"],
            },
        ]
    }
    context = SourceContext(user_id=1, queries=["warehouse worker"])

    jobs = ArbeitnowSource.parse_payload(payload, context)

    assert len(jobs) == 1
    assert jobs[0].title == "Lagermitarbeiter (m/w/d)"
    assert jobs[0].country == "DE"
    assert jobs[0].city == "Berlin"
    assert jobs[0].visa_sponsorship is True
    assert jobs[0].relocation is True
    assert jobs[0].description == "Visa support and relocation assistance are provided."
    assert jobs[0].published_at == "2026-10-11T00:00:00+00:00"


def test_arbeitnow_remote_free_form_location_does_not_confirm_work_country():
    payload = {"data": [{
        "slug": "remote-1", "title": "DevOps Engineer", "location": "Worldwide",
        "remote": True,
    }]}
    job = ArbeitnowSource.parse_payload(payload, SourceContext(user_id=1, queries=["DevOps"]))[0]
    assert job.work_mode == "remote"
    assert job.country is None
    assert job.city is None
    assert job.raw["source_location"] == "Worldwide"
    country = build_relocation_evidence(job)["fields"]["work_country"]
    assert country["status"] == "unknown"
    assert country["excerpt"] == "Worldwide"


def test_arbeitnow_keeps_explicit_remote_location_limit_in_card():
    from types import SimpleNamespace
    from app.database.models import Job
    from app.telegram.vacancy_view import render_job_details

    item = ArbeitnowSource.parse_payload({"data": [{
        "slug": "remote-limit", "title": "DevOps Engineer", "location": "Germany only",
        "remote": True, "description": "Work from anywhere.",
    }]}, SourceContext(user_id=1))[0]
    assert item.remote_scope == "Germany only"
    assert item.country is None
    job = Job(id=1, title=item.title, description=item.description,
              work_mode=item.work_mode, remote_scope=item.remote_scope)
    match = SimpleNamespace(total_score=72, technical_score=94, geography_score=100,
                            salary_score=58, relocation_score=50, reason="")
    card = render_job_details({"job": job, "match": match, "source": "arbeitnow"})
    assert "Germany only указано источником" in card
    assert "по всему миру указано источником" not in card


@pytest.mark.parametrize("created_at", [None, True, "not-a-timestamp", 1e100])
def test_arbeitnow_keeps_invalid_publication_timestamps_unknown(created_at):
    payload = {"data": [{
        "slug": "role-1", "title": "DevOps Engineer", "remote": False,
        "created_at": created_at,
    }]}
    item = ArbeitnowSource.parse_payload(payload, SourceContext(user_id=1, queries=[]))[0]
    assert item.published_at is None


def test_arbeitnow_retries_transient_transport_failure(monkeypatch):
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": []}

    class Client:
        def __init__(self, *, timeout):
            assert timeout == ArbeitnowSource.request_timeout_seconds
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise httpx.ReadTimeout("temporary timeout")
            return Response()

    monkeypatch.setattr("app.sources.adapters.arbeitnow.asyncio.sleep", fake_sleep)
    monkeypatch.setattr("app.sources.adapters.arbeitnow.httpx.AsyncClient", Client)

    source = ArbeitnowSource()
    jobs = asyncio.run(source.discover(SourceContext(user_id=1, queries=[])))

    assert source.retry_count == 1
    assert jobs == []
    assert delays == [0.5]


def test_arbeitnow_does_not_retry_http_status_errors(monkeypatch):
    calls = []

    class Response:
        status_code = 503
        request = httpx.Request("GET", ArbeitnowSource.endpoint)

        def raise_for_status(self):
            raise httpx.HTTPStatusError("unavailable", request=self.request, response=httpx.Response(503, request=self.request))

    class Client:
        def __init__(self, *, timeout):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            self.calls += 1
            calls.append(self.calls)
            return Response()

    monkeypatch.setattr("app.sources.adapters.arbeitnow.httpx.AsyncClient", Client)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(ArbeitnowSource().discover(SourceContext(user_id=1, queries=[])))
    assert calls == [1]


def test_arbeitnow_surfaces_error_after_one_retry(monkeypatch):
    calls = []
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    class Client:
        def __init__(self, *, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            calls.append(1)
            raise httpx.ReadTimeout("still unavailable")

    monkeypatch.setattr("app.sources.adapters.arbeitnow.asyncio.sleep", fake_sleep)
    monkeypatch.setattr("app.sources.adapters.arbeitnow.httpx.AsyncClient", Client)

    with pytest.raises(httpx.ReadTimeout):
        asyncio.run(ArbeitnowSource().discover(SourceContext(user_id=1, queries=[])))

    assert len(calls) == 2
    assert delays == [0.5]


@pytest.mark.parametrize("description, visa, relocation", [
    ("We do not provide visa sponsorship or relocation assistance.", False, False),
    ("No visa sponsorship or relocation assistance is provided.", False, False),
    ("Visa sponsorship and relocation assistance are not available.", False, False),
    ("We provide visa sponsorship and relocation assistance.", True, True),
    ("Must already have the right to work in Germany.", None, None),
    ("Visa sponsorship and relocation assistance may be available.", None, None),
    ("We provide visa sponsorship guidance.", None, None),
])
def test_arbeitnow_preserves_unknown_and_refused_support(description, visa, relocation):
    payload = {"data": [{
        "slug": "role-1", "title": "DevOps Engineer", "description": description,
        "remote": False, "relocation": True, "visa_sponsorship": True,
    }]}
    item = ArbeitnowSource.parse_payload(payload, SourceContext(user_id=1, queries=[]))[0]
    assert item.visa_sponsorship is visa
    assert item.relocation is relocation
    assert vacancy_allowed(item, {"relocation_preferences": {"visa_sponsorship": "require"}}) is (visa is True)
