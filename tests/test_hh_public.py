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


class FakeHH403ThenWeb:
    def __init__(self):
        self.api_calls = 0
        self.web_calls = 0

    async def search(self, text, page=0, per_page=20, area=None):
        from app.providers.hh import HHAPIForbidden
        self.api_calls += 1
        raise HHAPIForbidden("403")

    async def search_web(self, text, page=0, area=None):
        self.web_calls += 1
        return '''
        <html><body>
          <div data-qa="vacancy-serp__vacancy">
            <a data-qa="serp-item__title" href="https://hh.ru/vacancy/777?from=serp">
              <span data-qa="serp-item__title-text">Junior DevOps Engineer</span>
            </a>
            <a data-qa="vacancy-serp__vacancy-employer" href="/employer/1">Example Cloud</a>
            <span data-qa="vacancy-serp__vacancy-compensation">от 180 000 ₽ за месяц, на руки</span>
            <div data-qa="vacancy-serp__vacancy-address">Москва</div>
            <div data-qa="vacancy-serp__vacancy_snippet_requirement">Linux Docker GitLab CI</div>
            <div>Можно удалённо</div>
          </div>
        </body></html>
        '''


def test_hh_falls_back_to_public_web_after_api_403():
    fake = FakeHH403ThenWeb()
    source = HHSource(fake)
    ctx = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=[],
        queries=["DevOps Engineer"],
    )
    jobs = asyncio.run(source.discover(ctx))
    assert fake.api_calls == 1
    assert fake.web_calls == 1
    assert len(jobs) == 1
    assert jobs[0].source_job_id == "777"
    assert jobs[0].title == "Junior DevOps Engineer"
    assert jobs[0].company == "Example Cloud"
    assert jobs[0].salary_from == 180000
    assert jobs[0].salary_currency == "RUR"
    assert jobs[0].work_mode == "Удалённо"
    assert jobs[0].raw["transport"] == "web"


def test_hh_web_salary_range_parser():
    assert HHSource._salary("180 000 – 250 000 ₽ за месяц") == (180000, 250000, "RUR")
    assert HHSource._salary("до 250 000 ₽") == (None, 250000, "RUR")
