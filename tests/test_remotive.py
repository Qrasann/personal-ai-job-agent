import asyncio
from types import SimpleNamespace

import httpx
import pytest

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.domain.relocation_evidence import build_relocation_evidence
from app.sources.adapters.remotive import RemotiveSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities
from app.telegram.vacancy_view import render_jobs_list


def posting(job_id, title, location, **extra):
    return {
        "id": job_id,
        "title": title,
        "company_name": "Example Corp",
        "category": "Devops",
        "job_type": "full_time",
        "publication_date": "2026-10-10T12:00:00",
        "candidate_required_location": location,
        "salary": "$80,000 - $100,000",
        "description": "<p>Linux, Docker, monitoring and incident response.</p>",
        "url": f"https://remotive.com/remote/jobs/devops/{job_id}",
        **extra,
    }


def test_remotive_keeps_worldwide_and_selected_markets_but_rejects_country_only_mismatch():
    jobs = RemotiveSource.parse_payload(
        {
            "jobs": [
                posting(1, "DevOps Engineer", "Worldwide"),
                posting(2, "Linux Administrator", "Armenia, Georgia"),
                posting(3, "DevOps Engineer", "USA Only"),
                posting(4, "DevOps Engineer", "Europe"),
                posting(5, "Software Engineer", "Worldwide"),
                posting(6, "DevOps Engineer", "Worldwide", category="Software Development"),
                posting(11, "DevOps Engineer", "Russia Only"),
            ]
        },
        SourceContext(user_id=1, current_country="RU", target_countries=["GE", "AM"], queries=["DevOps Engineer", "Linux Administrator"]),
    )

    assert [job.source_job_id for job in jobs] == ["1", "2", "4"]
    worldwide, selected, regional = jobs
    assert worldwide.remote_scope == "worldwide"
    assert worldwide.country is None
    assert selected.remote_scope == "Armenia, Georgia"
    assert selected.country == "GE"
    assert regional.remote_scope == "Europe"
    assert regional.country is None
    assert all(job.work_mode == "remote" for job in jobs)
    assert all(job.visa_sponsorship is None and job.relocation is None for job in jobs)


@pytest.mark.parametrize("qualifier", ["USA", "U.S.A.", "U.S.", "United States", "United States of America"])
def test_remotive_disambiguates_georgia_us_state_from_georgia_country(qualifier):
    location = f"Georgia, {qualifier}"
    row = posting(21, "DevOps Engineer", location)

    georgia_jobs = RemotiveSource.parse_payload(
        {"jobs": [row]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )
    country_jobs = RemotiveSource.parse_payload(
        {"jobs": [posting(22, "DevOps Engineer", "Georgia")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )

    assert georgia_jobs == []
    assert RemotiveSource._country_codes_in_location(location) == {"US"}
    assert len(country_jobs) == 1 and country_jobs[0].country == "GE"


def test_remotive_disambiguates_georgia_with_us_state_postal_code():
    row = posting(26, "DevOps Engineer", "Georgia, GA")
    country_jobs = RemotiveSource.parse_payload(
        {"jobs": [row]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )
    gabon_jobs = RemotiveSource.parse_payload(
        {"jobs": [row]},
        SourceContext(user_id=1, target_countries=["GA"], queries=["DevOps Engineer"]),
    )

    assert RemotiveSource._country_codes_in_location("Georgia, GA") == {"US"}
    assert country_jobs == []
    assert gabon_jobs == []


@pytest.mark.parametrize(
    ("location", "target_countries", "market_country"),
    [("Georgia", ["GE"], "GE"), ("Armenia, Georgia", ["AM"], "AM")],
)
def test_remotive_candidate_location_is_not_reported_as_physical_work_country(
    location, target_countries, market_country,
):
    job = RemotiveSource.parse_payload(
        {"jobs": [posting(23, "DevOps Engineer", location)]},
        SourceContext(user_id=1, target_countries=target_countries, queries=["DevOps Engineer"]),
    )[0]

    assert job.country == market_country  # Retained as market identity for filtering/dedupe.
    assert job.remote_scope == location
    evidence = build_relocation_evidence(job)["fields"]
    assert evidence["work_country"]["status"] == "unknown"
    assert evidence["work_country"]["value"] is None


@pytest.mark.parametrize("location", ["GE", "GE Only", "Remote - GE", "Georgia (GE)"])
def test_remotive_recognizes_unambiguous_georgia_country_code_locations(location):
    jobs = RemotiveSource.parse_payload(
        {"jobs": [posting(24, "DevOps Engineer", location)]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )

    assert len(jobs) == 1
    assert jobs[0].country == "GE"


def test_remotive_country_code_only_location_excludes_other_markets():
    jobs = RemotiveSource.parse_payload(
        {"jobs": [posting(25, "DevOps Engineer", "GE Only")]},
        SourceContext(user_id=1, target_countries=["AM"], queries=["DevOps Engineer"]),
    )

    assert jobs == []


def test_remotive_country_code_detection_does_not_match_lowercase_common_words():
    assert RemotiveSource._country_codes_in_location("in") == set()
    assert RemotiveSource._country_codes_in_location("am") == set()
    assert RemotiveSource._country_codes_in_location("GE Only") == {"GE"}


def test_remotive_missing_candidate_location_stays_unknown_and_free_text_salary_is_not_structured():
    row = posting(7, "Linux Administrator", "")
    row.pop("candidate_required_location")
    job = RemotiveSource.parse_payload(
        {"jobs": [row]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Linux Administrator"]),
    )[0]

    assert job.remote_scope == "unknown"
    assert job.country is None
    assert job.salary_from is None and job.salary_to is None
    assert job.raw["salary_text"] == "$80,000 - $100,000"
    signals = analyze_job_signals(
        Job(
            fingerprint="remotive-unknown-location",
            title=job.title,
            description=job.description,
            country=job.country,
            work_mode=job.work_mode,
            remote_scope=job.remote_scope,
        )
    )
    assert signals.remote_eligibility == "uncertain"


def test_remotive_publication_dates_normalize_explicit_timezones_and_reject_ambiguous_values():
    assert RemotiveSource._published_at("Sun, 11 Oct 2026 12:00:00 GMT") == "2026-10-11T12:00:00+00:00"
    assert RemotiveSource._published_at("2026-10-11T14:00:00+02:00") == "2026-10-11T12:00:00+00:00"
    assert RemotiveSource._published_at("2026-10-11T12:00:00") is None
    assert RemotiveSource._published_at("not a date") is None


def test_remotive_uses_official_devops_rss_feed_and_normalizes_entries(monkeypatch):
    calls = []
    feed = b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><item>
      <guid>https://remotive.com/remote-jobs/devops/devops-engineer-8</guid>
      <title>DevOps Engineer</title>
      <link>https://remotive.com/remote-jobs/devops/devops-engineer-8</link>
      <description><![CDATA[<p>Linux, Docker and Kubernetes.</p>]]></description>
      <pubDate>Sun, 11 Oct 2026 12:00:00 GMT</pubDate>
      <category>Devops</category>
      <company-name>Example Corp</company-name>
    </item></channel></rss>"""

    async def get(self, url, **kwargs):
        calls.append((url, kwargs, self.headers.get("Accept")))
        return httpx.Response(
            200,
            content=feed,
            headers={"content-type": "application/rss+xml"},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(
        RemotiveSource().discover(
            SourceContext(user_id=1, target_countries=["AM"], queries=["DevOps Engineer"])
        )
    )

    assert len(jobs) == 1
    assert jobs[0].company == "Example Corp"
    assert jobs[0].skills == ["Devops"]
    assert jobs[0].remote_scope == "unknown"
    assert jobs[0].published_at == "2026-10-11T12:00:00+00:00"
    assert calls[0][0] == "https://remotive.com/remote-jobs/devops/feed"
    assert calls[0][1] == {}
    assert "application/rss+xml" in calls[0][2]


def test_remotive_accepts_a_valid_empty_rss_feed():
    payload = RemotiveSource.parse_feed(
        b"<rss version='2.0'><channel><title>Devops jobs</title></channel></rss>"
    )

    assert payload == {"jobs": [], "job-count": 0}


def test_remotive_rejects_malformed_payload_and_non_remotive_links():
    try:
        RemotiveSource.parse_payload({"error": "unavailable"}, SourceContext(user_id=1))
    except ValueError as exc:
        assert "contract unavailable" in str(exc)
    else:
        raise AssertionError("expected malformed Remotive payload to be rejected")

    for content in (b"<rss>", b"<html></html>"):
        try:
            RemotiveSource.parse_feed(content)
        except ValueError:
            pass
        else:
            raise AssertionError("expected malformed or non-RSS feed to be rejected")

    row = posting(9, "DevOps Engineer", "Worldwide")
    row["url"] = "https://example.com/jobs/9"
    assert RemotiveSource.parse_payload(
        {"jobs": [row]}, SourceContext(user_id=1, queries=["DevOps Engineer"])
    ) == []


def test_remotive_is_registered_as_global_remote_discovery_only():
    plan = next(item for item in build_source_plan("RU", ["GE"]) if item.source_id == "remotive")

    assert plan.implemented
    assert plan.scope == "remote · DevOps/Sysadmin"
    assert not source_capabilities("remotive").apply
    assert not source_capabilities("remotive").messages


def test_remotive_attribution_is_visible_as_a_clickable_source_link():
    job = SimpleNamespace(
        id=10,
        title="DevOps Engineer",
        company="Example Corp",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="Linux Docker",
        city=None,
        country=None,
        work_mode="remote",
    )
    match = SimpleNamespace(total_score=80)

    rendered = render_jobs_list(
        [(match, job)],
        source_links={10: [("https://remotive.com/remote/jobs/devops/10", "Remotive")]},
    )

    assert '<a href="https://remotive.com/remote/jobs/devops/10">Remotive</a>' in rendered
