import asyncio

from app.config import Settings, settings
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


def test_hh_public_discovery_searches_each_role_separately_without_details():
    fake = FakeHHClient()
    source = HHSource(fake)
    ctx = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=[],
        queries=["DevOps Engineer", "Linux Administrator"],
    )
    jobs = asyncio.run(source.discover(ctx))
    assert len(fake.search_calls) == 2
    assert [call[0] for call in fake.search_calls] == ["DevOps Engineer", "Linux Administrator"]
    assert all(call[3] == "113" for call in fake.search_calls)
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


def test_hh_falls_back_to_public_web_after_api_403(monkeypatch):
    monkeypatch.setattr(settings, "hh_web_max_pages", 1)
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


def test_normal_hh_html_can_contain_captcha_word_without_being_challenge():
    # Regression fixture: normal HH pages can mention "captcha" inside JS.
    html = '''
    <html><body>
      <script>window.config = {"captcha":"available"}</script>
      <div data-qa="vacancy-serp__vacancy">
        <a data-qa="serp-item__title" href="https://hh.ru/vacancy/1">DevOps Engineer</a>
      </div>
    </body></html>
    '''
    folded = html.casefold()
    has_search_content = any(marker in folded for marker in (
        'data-qa="vacancy-serp__vacancy"',
        'data-qa="serp-item__title"',
        'vacancy-serp',
    ))
    explicit_challenge = any(marker in folded for marker in (
        "проверка, что вы не робот",
        "подтвердите, что вы человек",
        "подтвердите, что вы не робот",
        "пройдите проверку, чтобы продолжить",
    ))
    assert has_search_content is True
    assert explicit_challenge is False


def test_hh_web_parser_keeps_card_text_for_seniority_signals():
    html = '''
    <div data-qa="vacancy-serp__vacancy">
      <a data-qa="serp-item__title" href="https://hh.ru/vacancy/999">DevOps Engineer</a>
      <a data-qa="vacancy-serp__vacancy-employer">Example</a>
      <div data-qa="vacancy-serp__vacancy_snippet_requirement">Linux Docker</div>
      <div>Опыт от 3 лет</div>
    </div>
    '''
    jobs = HHSource.parse_web_html(html)
    assert len(jobs) == 1
    assert "Опыт от 3 лет" in jobs[0].description
    assert "Опыт от 3 лет" in jobs[0].raw["card_text"]

def test_hh_default_web_search_uses_three_pages():
    assert Settings.model_fields["hh_web_max_pages"].default == 3

class FakeHH403Paged:
    def __init__(self):
        self.api_calls = []
        self.web_calls = []

    async def search(self, text, page=0, per_page=20, area=None):
        from app.providers.hh import HHAPIForbidden
        self.api_calls.append(text)
        raise HHAPIForbidden("403")

    async def search_web(self, text, page=0, area=None):
        self.web_calls.append((text, page, area))
        if text == "Infrastructure Engineer" and page == 1:
            return "<html><body></body></html>"
        if text == "DevOps Engineer":
            job_id = str(11 + page)
        elif text == "Linux Administrator":
            job_id = "13" if page == 0 else str(21 + page)
        else:
            job_id = "31"
        return (
            "<div data-qa=\"vacancy-serp__vacancy\">"
            f"<a data-qa=\"serp-item__title\" href=\"https://hh.ru/vacancy/{job_id}\">{text}</a>"
            "</div>"
        )

def test_hh_403_fallback_pages_roles_dedupes_and_stops(monkeypatch):
    monkeypatch.setattr(settings, "hh_web_max_pages", 3)
    fake = FakeHH403Paged()
    source = HHSource(fake)
    ctx = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=[],
        queries=["DevOps Engineer", "Linux Administrator", "Infrastructure Engineer"],
    )
    jobs = asyncio.run(source.discover(ctx))

    assert fake.api_calls == ["DevOps Engineer"]
    assert fake.web_calls == [
        ("DevOps Engineer", 0, "113"),
        ("DevOps Engineer", 1, "113"),
        ("DevOps Engineer", 2, "113"),
        ("Linux Administrator", 0, "113"),
        ("Linux Administrator", 1, "113"),
        ("Linux Administrator", 2, "113"),
        ("Infrastructure Engineer", 0, "113"),
        ("Infrastructure Engineer", 1, "113"),
    ]
    assert [job.source_job_id for job in jobs] == ["11", "12", "13", "22", "23", "31"]
