import asyncio

import httpx
import pytest

from app.sources.adapters import georgia
from app.sources.base import SourceContext


def test_georgia_queries_require_a_specific_role_token():
    assert georgia._matches("DevOps Engineer", ["DevOps Engineer"])
    assert not georgia._matches("Electrical Engineer", ["DevOps Engineer"])
    assert not georgia._matches("Engineer", ["DevOps Engineer"])
    assert georgia._matches("Warehouse Operative", ["warehouse worker"])
    assert georgia._city_from_text("Tbilisi is our regional head office") is None
    assert georgia._city_from_text("Work Location: Tbilisi, Georgia") == "Tbilisi"


def test_hr_ge_salary_needs_explicit_currency_and_period():
    assert georgia._salary_from_text("Salary: Fixed 2 000 - 3 000") == (
        None,
        None,
        None,
        None,
        "Salary: Fixed 2 000 - 3 000",
    )
    assert georgia._salary_from_text("Salary: GEL 2 000 - 3 000") == (
        None,
        None,
        None,
        None,
        "Salary: GEL 2 000 - 3 000",
    )
    assert georgia._salary_from_text("Salary: GEL 2 000 - 3 000 monthly") == (
        2000,
        3000,
        "GEL",
        "month",
        "Salary: GEL 2 000 - 3 000 monthly",
    )
    salary = georgia._salary_from_text("Salary: 2 000 GEL - 3 000 USD")
    assert salary[:4] == (None, None, None, None)
    assert salary[4] == "Salary: 2 000 GEL - 3 000 USD"
    assert georgia._salary_from_text("Salary: $2,000-$3,000 per year") == (
        None,
        None,
        None,
        None,
        "Salary: $2,000-$3,000 per year",
    )
    assert georgia._salary_from_text("Salary: $2,000-$3,000 monthly")[:4] == (
        None,
        None,
        None,
        None,
    )


def test_hr_ge_detail_does_not_guess_currency_work_mode_or_relocation(monkeypatch):
    async def fake_sleep(delay):
        return None

    monkeypatch.setattr(georgia.asyncio, "sleep", fake_sleep)
    listing = '<a href="/en/announcement/123/DevOps-Engineer">DevOps Engineer</a>'
    detail = """<main>
      Company: Example Systems
      Work Location: Tbilisi
      Salary: Fixed 2 000 - 3 000
      Relocation support is not provided.
    </main>"""

    class Response:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    client_config = {}

    class Client:
        def __init__(self, *args, **kwargs):
            client_config.update(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url):
            return Response(listing if url == georgia.HRGESource.base else detail)

    monkeypatch.setattr(georgia.httpx, "AsyncClient", Client)
    jobs = asyncio.run(georgia.HRGESource().discover(SourceContext(user_id=1, queries=["DevOps Engineer"])))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.company == "Example Systems"
    assert job.city == "Tbilisi"
    assert job.salary_from is None
    assert job.salary_to is None
    assert job.salary_currency is None
    assert job.salary_period is None
    assert job.raw["source_salary_text"] == "Salary: Fixed 2 000 - 3 000"
    assert job.work_mode is None
    assert job.relocation is None
    assert client_config["timeout"].connect == 5.0
    assert client_config["timeout"].read == georgia.REQUEST_TIMEOUT_SECONDS


def test_detail_fetch_is_bounded_and_keeps_successes_after_http_errors(monkeypatch):
    delays = []

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(georgia.asyncio, "sleep", fake_sleep)

    class Response:
        text = "Example vacancy"

        def raise_for_status(self):
            return None

    class Client:
        def __init__(self):
            self.calls = []

        async def get(self, url):
            self.calls.append(url)
            if url == "detail-2":
                raise httpx.ConnectError("temporary failure")
            return Response()

    client = Client()
    built = []

    def build_job(title, url, text, soup):
        built.append(url)
        return url

    links = [(f"title-{n}", f"detail-{n}") for n in range(10)]
    jobs = asyncio.run(georgia._fetch_details(client, links, "HR.ge", build_job))

    assert len(client.calls) == georgia.MAX_DETAILS_PER_SOURCE
    assert len(jobs) == georgia.MAX_DETAILS_PER_SOURCE - 1
    assert "detail-2" not in built
    assert delays == [georgia.REQUEST_INTERVAL_SECONDS] * georgia.MAX_DETAILS_PER_SOURCE


def test_detail_fetch_reports_total_failure(monkeypatch):
    async def fake_sleep(delay):
        return None

    monkeypatch.setattr(georgia.asyncio, "sleep", fake_sleep)

    class Client:
        async def get(self, url):
            raise httpx.ConnectError("temporary failure")

    async def run():
        await georgia._fetch_details(
            Client(),
            [("DevOps Engineer", "detail-1")],
            "HR.ge",
            lambda *args: None,
        )

    with pytest.raises(httpx.ConnectError):
        asyncio.run(run())
