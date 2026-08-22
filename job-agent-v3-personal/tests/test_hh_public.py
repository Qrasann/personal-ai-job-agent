import asyncio

from app.sources.adapters.hh import HHSource
from app.sources.base import SourceContext
from app.sources.registry import source_capabilities


class FakeHHClient:
    def __init__(self):
        self.search_calls = []
        self.vacancy_calls = 0

    async def search(self, text, page=0, per_page=20, area=None):
        self.search_calls.append((text, page, per_page, area))
        return {
            "items": [
                {
                    "id": "123",
                    "name": "DevOps Engineer",
                    "employer": {"name": "Example"},
                    "area": {"name": "Москва"},
                    "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
                    "snippet": {"requirement": "Linux, Docker", "responsibility": "CI/CD"},
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "published_at": "2026-08-22T12:00:00+0300",
                    "work_format": [{"name": "Удалённо"}],
                }
            ]
        }

    async def vacancy(self, vacancy_id):
        self.vacancy_calls += 1
        raise AssertionError("public discover must not fan out into detail calls")


def test_hh_is_discovery_only_in_personal_public_build():
    caps = source_capabilities("hh")
    assert caps.discovery is True
    assert caps.apply is False
    assert caps.messages is False


def test_hh_combines_multiple_roles_into_one_query():
    query = HHSource._combined_query(["DevOps Engineer", "Linux Administrator"])
    assert " OR " in query
    assert "DevOps Engineer" in query
    assert "Linux Administrator" in query


def test_hh_public_discovery_is_single_request_without_details():
    fake = FakeHHClient()
    source = HHSource(fake)
    ctx = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=[],
        queries=["DevOps Engineer", "Linux Administrator"],
    )
    jobs = asyncio.run(source.discover(ctx))
    assert len(fake.search_calls) == 1
    assert fake.search_calls[0][3] == "113"
    assert fake.vacancy_calls == 0
    assert len(jobs) == 1
    assert jobs[0].source_job_id == "123"
    assert jobs[0].country == "RU"
