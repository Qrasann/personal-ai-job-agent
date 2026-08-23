from types import SimpleNamespace

from app.domain.job_text import clean_html_text, extract_experience, format_salary, repair_mojibake
from app.sources.adapters.hh import HHSource
from app.telegram.vacancy_view import render_job_details, render_jobs_list


def test_hh_card_salary_falls_back_to_visible_card_text():
    html = '''
    <div data-qa="vacancy-serp__vacancy">
      <a data-qa="serp-item__title" href="https://hh.ru/vacancy/25">DevOps инженер</a>
      <a data-qa="vacancy-serp__vacancy-employer">СИНЕРГИЯ</a>
      <span data-qa="vacancy-serp__vacancy-compensation">Выплаты: Два раза в месяц</span>
      <div data-qa="vacancy-serp__vacancy-address">Москва</div>
      <div>до 300 000 ₽ за месяц, на руки Опыт 3-6 лет Можно удалённо</div>
    </div>
    '''
    jobs = HHSource.parse_web_html(html)
    assert len(jobs) == 1
    assert jobs[0].salary_from is None
    assert jobs[0].salary_to == 300000
    assert jobs[0].salary_currency == "RUR"
    assert jobs[0].raw["salary_text"] == "до 300 000 ₽"


def test_hh_public_vacancy_page_parser_uses_json_ld_and_dom_fields():
    html = '''
    <html><body>
      <div data-qa="vacancy-experience">Опыт 3-6 лет</div>
      <div data-qa="work-formats-text">Удалённо</div>
      <div data-qa="vacancy-salary">до 300 000 ₽ за месяц</div>
      <script type="application/ld+json">
      {
        "@context":"https://schema.org/",
        "@type":"JobPosting",
        "title":"DevOps инженер",
        "description":"<p><strong>Обязанности</strong></p><ul><li>CI/CD</li><li>Linux</li></ul>",
        "datePosted":"2026-08-23T10:38:00+03:00",
        "hiringOrganization":{"@type":"Organization","name":"СИНЕРГИЯ"},
        "jobLocation":{"@type":"Place","address":{"@type":"PostalAddress","addressLocality":"Москва"}},
        "applicantLocationRequirements":{"@type":"Country","name":"Россия"}
      }
      </script>
    </body></html>
    '''
    details = HHSource.parse_vacancy_web_html(html)
    assert details["title"] == "DevOps инженер"
    assert details["company"] == "СИНЕРГИЯ"
    assert details["city"] == "Москва"
    assert details["experience"] == "Опыт 3-6 лет"
    assert details["work_mode"] == "Удалённо"
    assert details["salary_to"] == 300000
    assert "Обязанности" in details["description"]
    assert "CI/CD" in details["description"]


def test_text_helpers_clean_html_repair_mojibake_and_format_salary():
    assert repair_mojibake("tecnolÃ³gico") == "tecnológico"
    assert clean_html_text("<p>Linux</p><ul><li>Docker</li></ul>") == "Linux\nDocker"
    assert format_salary(None, 300000, "RUR") == "до 300 000 ₽"
    assert format_salary(None, None, None, fallback_text="175 000 – 300 000 ₽ за месяц") == "175 000–300 000 ₽"
    assert extract_experience("DevOps. Опыт 1-3 года. Linux") == "1-3 года"



def test_format_salary_ignores_legacy_bare_numbers_and_prefers_currency_text():
    assert format_salary(14, None, None, fallback_text="DevOps 14 отзывов") == "не указана"
    assert format_salary(585, 736, None, fallback_text="585, Холдинг 4.2 • 736 отзывов") == "не указана"
    assert format_salary(14, None, None, fallback_text="от 160 000 ₽ за месяц") == "от 160 000 ₽"


def test_hh_public_vacancy_prefers_json_ld_salary_range():
    html = r'''
    <html><body>
      <div data-qa="vacancy-salary">до 300 000 ₽</div>
      <script type="application/ld+json">
      {
        "@context":"https://schema.org/",
        "@type":"JobPosting",
        "title":"DevOps Engineer",
        "description":"<p>Linux</p>",
        "baseSalary":{
          "@type":"MonetaryAmount",
          "currency":"RUR",
          "value":{
            "@type":"QuantitativeValue",
            "minValue":175000,
            "maxValue":300000,
            "unitText":"MONTH"
          }
        }
      }
      </script>
    </body></html>
    '''
    details = HHSource.parse_vacancy_web_html(html)
    assert details["salary_from"] == 175000
    assert details["salary_to"] == 300000
    assert details["salary_currency"] == "RUR"

def test_jobs_list_includes_job_id_and_details_command():
    job = SimpleNamespace(
        id=25,
        title="DevOps инженер",
        company="СИНЕРГИЯ",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="до 300 000 ₽ за месяц Опыт 3-6 лет Можно удалённо",
        city="Москва",
        country="RU",
        work_mode="Удалённо",
    )
    match = SimpleNamespace(total_score=65)
    text = render_jobs_list([(match, job)])
    assert "#25 · 65/100" in text
    assert "до 300 000 ₽" in text
    assert "/job 25" in text


def test_job_details_separates_source_data_from_agent_score():
    job = SimpleNamespace(
        id=25,
        title="DevOps инженер",
        company="СИНЕРГИЯ",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="short fallback",
        city="Москва",
        country="RU",
        work_mode="Удалённо",
        published_at=None,
    )
    match = SimpleNamespace(
        total_score=65,
        technical_score=54,
        geography_score=95,
        salary_score=58,
        relocation_score=50,
        reason="режим russia; техника 54",
    )
    payload = {
        "job": job,
        "match": match,
        "source": "hh",
        "url": "https://hh.ru/vacancy/25",
        "fallback_salary_text": "DevOps Engineer 175 000–300 000 ₽ за месяц",
        "details": {
            "description": "Обязанности\nCI/CD\nТребования\nLinux Docker",
            "experience": "Опыт 3-6 лет",
            "salary_to": 300000,
            "salary_currency": "RUR",
            "salary_text": "до 300 000 ₽",
            "city": "Москва",
            "work_mode": "Удалённо",
            "published_at": "2026-08-23T10:38:00+03:00",
        },
        "warning": "",
    }
    text = render_job_details(payload)
    assert "Описание вакансии" in text
    assert "CI/CD" in text
    assert "Оценка Job Agent" in text
    assert "💰 175 000–300 000 ₽" in text
    assert "Technical: 54/100" in text
    assert "23.08.2026 10:38" in text
    assert "Открыть оригинал вакансии" in text
