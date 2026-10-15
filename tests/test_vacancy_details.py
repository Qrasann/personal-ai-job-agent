from types import SimpleNamespace

import pytest

from app.domain.job_text import clean_html_text, extract_experience, format_salary, repair_mojibake, salary_period_from_text
from app.sources.adapters.hh import HHSource
from app.telegram.vacancy_view import _published, render_job_details, render_jobs_list


@pytest.mark.parametrize(("value", "expected"), [
    ("2026-10-15T12:30:00+04:00", "15.10.2026 08:30 UTC"),
    ("2026-10-15T12:30:00Z", "15.10.2026 12:30 UTC"),
    ("2026-10-15T12:30:00", "15.10.2026 12:30 (часовой пояс не указан)"),
    ("2026-10-15", "15.10.2026"),
])
def test_published_date_display_preserves_timezone_evidence(value, expected):
    assert _published(value) == expected


def _timezone_card(restrictions, availability=None):
    job = SimpleNamespace(
        id=25, title="Linux Support Engineer", company="Example",
        salary_from=None, salary_to=None, salary_currency=None,
        city=None, country=None, work_mode="remote", remote_scope="worldwide",
        description="Linux support", published_at=None,
    )
    match = SimpleNamespace(
        total_score=82, technical_score=86, geography_score=100,
        salary_score=58, relocation_score=50, reason="",
    )
    return render_job_details({
        "job": job, "match": match, "source": "himalayas", "url": "",
        "details": {"timezone_restrictions": restrictions, "availability": availability},
    })


@pytest.mark.parametrize(("expires_at", "expected"), [
    ("2000-01-01T00:00:00+00:00", "Срок размещения по источнику истёк: 01.01.2000"),
    ("2090-01-01T00:00:00+00:00", "Срок размещения по источнику: 01.01.2090"),
    (None, "Срок размещения: не указан источником"),
    ("invalid", "Срок размещения: не указан источником"),
])
def test_card_discloses_source_expiry_without_promising_employer_hiring(expires_at, expected):
    rendered = _timezone_card([], {"source_field": "expiryDate", "expires_at": expires_at})
    assert expected in rendered
    assert "Match: <b>82/100</b>" in rendered
    assert "вакансия открыта" not in rendered.casefold()
    assert "вакансия закрыта" not in rendered.casefold()
    if expires_at and expires_at != "invalid":
        assert "Статус найма и дедлайн отклика уточняйте у работодателя." in rendered


def test_remote_card_discloses_source_timezones_separately_from_country_scope():
    rendered = _timezone_card(["UTC-5", "UTC+4"])

    assert "⏱ Часовые пояса по источнику: UTC-5, UTC+4" in rendered
    assert "возможность найма в вашей стране нужно подтвердить" in rendered
    assert "Geography: 100/100" in rendered


def test_source_timezone_disclosure_is_clean_escaped_and_bounded():
    rendered = _timezone_card([
        "<b>UTC-5</b>", " UTC-5 ", "UTC+4 &amp; UTC+5",
        *(f"UTC+{index}" for index in range(100)),
    ])
    line = next(line for line in rendered.splitlines() if line.startswith("⏱"))

    assert "<b>UTC-5</b>" not in line
    assert "UTC-5, UTC-5" not in line
    assert "UTC+4 &amp; UTC+5" in line
    assert len(line) <= 260
    assert line.endswith("…")


@pytest.mark.parametrize("restrictions", [
    None, [], "UTC+4", {"offset": "UTC+4"}, [None, {}, 4],
    [" ", "unknown", "unspecified", "n/a"],
])
def test_unknown_or_invalid_timezone_restrictions_make_no_availability_claim(restrictions):
    rendered = _timezone_card(restrictions)

    assert "⏱ Часовые пояса" not in rendered
    assert "все часовые пояса" not in rendered
    assert "возможность найма в вашей стране нужно подтвердить" in rendered


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
    assert clean_html_text("&lt;p&gt;&lt;strong&gt;Linux&lt;/strong&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Docker &amp; Git&lt;/li&gt;&lt;/ul&gt;") == "Linux\nDocker & Git"
    assert format_salary(None, 300000, "RUR") == "до 300 000 ₽"
    assert format_salary(None, None, None, fallback_text="175 000 – 300 000 ₽ за месяц") == "175 000–300 000 ₽ в месяц"
    assert extract_experience("DevOps. Опыт 1-3 года. Linux") == "1-3 года"
    assert (
        extract_experience(
            "Minimum 3 years of hands-on Linux administration experience"
        )
        == "Minimum 3 years"
    )



def test_format_salary_ignores_legacy_bare_numbers_and_prefers_currency_text():
    assert format_salary(14, None, None, fallback_text="DevOps 14 отзывов") == "не указана"
    assert format_salary(585, 736, None, fallback_text="585, Холдинг 4.2 • 736 отзывов") == "не указана"
    assert format_salary(14, None, None, fallback_text="от 160 000 ₽ за месяц") == "от 160 000 ₽ в месяц"


def test_non_salary_description_numbers_are_not_used_without_explicit_fallback():
    assert format_salary(None, None, None) == "не указана"


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
    # List rows have no source metadata, so arbitrary description numbers must
    # not be treated as salary. Structured values are rendered when present.
    assert "💰 не указана" in text
    assert "/job 25" in text


def test_himalayas_job_list_item_includes_visible_source_attribution_link():
    job = SimpleNamespace(
        id=26,
        title="DevOps Engineer",
        company="Example Corp",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        salary_period=None,
        description="Remote Linux role",
        city=None,
        country=None,
        work_mode="remote",
    )
    match = SimpleNamespace(total_score=70)

    text = render_jobs_list(
        [(match, job)],
        source_links={26: "https://himalayas.app/companies/example/jobs/devops"},
    )

    assert 'Источник: <a href="https://himalayas.app/companies/example/jobs/devops">Himalayas</a>' in text


def test_jobs_list_marks_below_threshold_for_manual_review():
    job = SimpleNamespace(
        id=31,
        title="Warehouse Worker",
        company="Example Logistics",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        salary_period=None,
        description="",
        city="Tbilisi",
        country="GE",
        work_mode=None,
    )
    match = SimpleNamespace(total_score=54)

    text = render_jobs_list([(match, job)], below_threshold=65)

    assert "Ниже порога 65 · ручной просмотр" in text
    assert "право на работу и условия переезда не подтверждены автоматически" in text
    assert "#31 · 54/100" in text


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
        recommendation_scores={
            "growth": {"score": None, "evidence": "not provided"},
            "competition": {"score": None, "evidence": "no public data"},
        },
        reason="режим russia; техника 54",
    )
    payload = {
        "job": job,
        "match": match,
        "source": "hh",
        "url": "https://hh.ru/vacancy/25",
        "fallback_salary_text": "DevOps Engineer 175 000–300 000 ₽ за месяц",
        "details": {
            "description": "&lt;p&gt;Обязанности&lt;/p&gt;&lt;p&gt;CI/CD&lt;/p&gt;&lt;p&gt;Требования&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Linux Docker&lt;/li&gt;&lt;/ul&gt;",
            "experience": "Опыт 3-6 лет",
            "salary_to": 300000,
            "salary_currency": "RUR",
            "salary_text": "до 300 000 ₽",
            "city": "Москва",
            "work_mode": "Удалённо",
            "published_at": "2026-08-23T10:38:00+03:00",
        },
        "warning": "",
        "search_profile_name": "Relocation-first <manual>",
    }
    text = render_job_details(payload)
    assert "Описание вакансии" in text
    assert "&lt;p&gt;" not in text
    assert "CI/CD" in text
    assert "Оценка Job Agent" in text
    assert "💰 175 000–300 000 ₽ в месяц" in text
    assert "Technical: 54/100" in text
    assert "Recommendation v2" in text
    assert "Рост: н/д" in text
    assert "Конкуренция н/д" in text
    assert "23.08.2026 07:38 UTC" in text
    assert "Открыть оригинал вакансии" in text
    assert "Профиль: Relocation-first &lt;manual&gt;" in text


@pytest.mark.parametrize(("evidence", "expected"), [
    ("175 000–300 000 ₽ за месяц", "monthly"),
    ("Salary: 80 000–100 000 USD per year", "annual"),
    ("Salary: 20 000 GEL", None),
    ("20.50 hourly", None),
    ("100 000 ₽; review contract in one month", None),
])
def test_salary_period_is_extracted_only_from_explicit_nearby_evidence(evidence, expected):
    assert salary_period_from_text(evidence) == expected


def test_display_uses_explicit_text_period_but_does_not_override_structured_period():
    assert format_salary(175000, 300000, "RUR", fallback_text="175 000–300 000 ₽ за месяц") == "175 000–300 000 ₽ в месяц"
    assert format_salary(
        175000, 300000, "RUR", period="annual", fallback_text="175 000–300 000 ₽ за месяц"
    ) == "175 000–300 000 ₽ в год"


def test_job_details_separate_mobility_evidence_from_personal_eligibility():
    job = SimpleNamespace(
        id=44, title="Infrastructure Engineer", company="ACME",
        salary_from=None, salary_to=None, salary_currency=None,
        description="We provide relocation support. No visa sponsorship. "
                    "You must already have the right to work.",
        city="Berlin", country="DE", work_mode="hybrid", published_at=None,
        relocation=None, visa_sponsorship=None,
    )
    match = SimpleNamespace(
        total_score=70, technical_score=70, geography_score=60,
        salary_score=58, relocation_score=40, recommendation_scores={}, reason="",
    )

    text = render_job_details({
        "job": job, "match": match, "source": "greenhouse",
        "url": "https://example.com/jobs/44", "details": {},
    })

    assert "Право на работу и переезд" in text
    assert "Visa sponsorship: явно не предоставляется" in text
    assert "Помощь с переездом: явно предлагается" in text
    assert "Помощь с разрешением на работу: не подтверждено вакансией" in text
    assert "Предварительное право на работу: явно требуется" in text
    assert "не подтверждают личную юридическую eligibility" in text


def test_foreign_job_details_keep_missing_mobility_evidence_unknown():
    job = SimpleNamespace(
        id=45, title="Linux Engineer", company="ACME",
        salary_from=None, salary_to=None, salary_currency=None,
        description="Linux operations", city="Tbilisi", country="GE",
        work_mode="onsite", published_at=None, relocation=None,
        visa_sponsorship=None,
    )
    match = SimpleNamespace(
        total_score=70, technical_score=70, geography_score=60,
        salary_score=58, relocation_score=50, recommendation_scores={}, reason="",
    )

    text = render_job_details({
        "job": job, "match": match, "source": "greenhouse", "url": "",
        "details": {},
    })

    assert "Visa sponsorship: не подтверждено вакансией" in text
    assert "Помощь с переездом: не подтверждено вакансией" in text
    assert "Предварительное право на работу: явного требования не найдено" in text


def test_structured_relocation_evidence_displays_per_signal_source_and_unknowns():
    job = SimpleNamespace(
        id=46, title="Synthetic Infrastructure Engineer", company="Fixture Co",
        salary_from=None, salary_to=None, salary_currency=None,
        description="Synthetic fixture description", city=None, country="DE",
        work_mode=None, published_at=None, relocation=None, visa_sponsorship=None,
    )
    match = SimpleNamespace(
        total_score=50, technical_score=50, geography_score=50,
        salary_score=50, relocation_score=50, recommendation_scores={}, reason="",
    )
    evidence = {
        "captured_at": "2026-10-15T12:30:00+00:00",
        "fields": {
            "work_country": {"status": "confirmed", "value": "DE", "source_id": "fixture", "source_url": "https://example.invalid", "excerpt": "DE", "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "source_structured"},
            "visa_sponsorship": {"status": "unknown", "value": None, "source_id": "fixture", "excerpt": None, "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "unknown"},
            "citizenship_or_residence_restriction": {"status": "confirmed", "value": "Candidates must currently reside in Germany", "source_id": "fixture", "excerpt": "Candidates must currently reside in Germany", "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "explicit_text", "interpretation": {"scope": "residence"}},
            "housing_provided": {"status": "confirmed", "value": False, "source_id": "fixture", "excerpt": "Housing is not provided", "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "explicit_text"},
            "language_requirement": {"status": "confirmed", "value": "English B2 required", "source_id": "fixture", "excerpt": "English B2 required", "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "explicit_requirement", "interpretation": {"language": "English", "requirement": "required", "cefr": "B2"}},
        },
    }
    text = render_job_details({
        "job": job, "match": match, "source": "fixture", "url": "",
        "details": {}, "relocation_evidence": evidence,
    })
    assert "Страна работы по источнику: DE (сообщено источником)" in text
    assert "Visa sponsorship: неизвестно по доступному тексту" in text
    assert "ограничение по месту проживания (текст источника)" in text
    assert "Обеспечение жильём: явно не предоставляется" in text
    assert "Языковое требование: English · требуется · CEFR B2" in text
    assert "(fixture; 2026-10-15T12:30:00+00:00; unknown)" in text


def test_remote_job_details_show_source_geography_without_claiming_work_eligibility():
    match = SimpleNamespace(
        total_score=70,
        technical_score=70,
        geography_score=50,
        salary_score=58,
        relocation_score=50,
        recommendation_scores={},
        reason="",
    )

    def render(scope, work_mode="remote"):
        job = SimpleNamespace(
            id=1273,
            title="Associate Linux Support Engineer",
            company="Canonical",
            salary_from=72000,
            salary_to=96000,
            salary_currency="USD",
            salary_period="annual",
            description="Linux support",
            city=None,
            country=None,
            work_mode=work_mode,
            remote_scope=scope,
            published_at=None,
        )
        return render_job_details({
            "job": job,
            "match": match,
            "source": "himalayas",
            "url": "https://himalayas.app/jobs/1273",
            "details": {},
        })

    unknown = render("unknown")
    worldwide = render("worldwide")
    limited = render("Armenia, Georgia")
    timezone = render("GMT-7 to GMT+4 time zones")
    non_remote = render("unknown", work_mode="onsite")

    assert "страны найма не указаны источником" in unknown
    assert "возможность найма в вашей стране нужно подтвердить" in worldwide
    assert "Armenia, Georgia указано источником" in limited
    assert "GMT-7 to GMT+4 time zones указано источником" in timezone
    assert "возможность найма в вашей стране нужно подтвердить" in timezone
    assert "🌍 География remote:" in unknown
    assert "72 000–96 000 $ в год" in unknown
    assert "🌍 География remote:" not in non_remote
