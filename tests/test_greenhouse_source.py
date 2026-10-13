import asyncio

import httpx
import pytest

from app.sources.adapters.greenhouse import GreenhouseSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities
from app.matching.fact_comparison import extract_requirement_importance


def listing(job_id, title, location, content="", url=None):
    return {
        "id": job_id,
        "title": title,
        "location": {"name": location},
        "absolute_url": url or f"https://job-boards.greenhouse.io/lineate/jobs/{job_id}",
        "updated_at": "2026-10-10T10:00:00-04:00",
        "content": content,
    }


def test_greenhouse_returns_only_role_relevant_jobs_in_selected_target_country():
    payload = {
        "jobs": [
            listing(8018252, "Infrastructure Engineer", "Georgian office"),
            listing(8018253, "Data Engineer", "Yerevan, Yerevan, Armenia"),
            listing(8018254, "Infrastructure Engineer", "New York, NY"),
            listing(8018255, "Office Manager", "Tbilisi, Georgia"),
        ]
    }

    jobs = GreenhouseSource.parse_payload(
        payload,
        SourceContext(
            user_id=1,
            current_country="RU",
            target_countries=["GE"],
            queries=["DevOps Engineer", "Infrastructure Engineer"],
        ),
    )

    assert len(jobs) == 1
    assert jobs[0].source == "greenhouse"
    assert jobs[0].source_job_id == "lineate:8018252"
    assert jobs[0].title == "Infrastructure Engineer"
    assert jobs[0].country == "GE"
    assert jobs[0].city is None
    assert jobs[0].visa_sponsorship is None
    assert jobs[0].relocation is None


def test_greenhouse_parses_armenia_only_when_am_is_selected():
    payload = {"jobs": [listing(99, "Data Engineer", "Yerevan, Yerevan, Armenia")]}

    assert GreenhouseSource.parse_payload(
        payload,
        SourceContext(user_id=1, target_countries=["GE"], queries=["Data Engineer"]),
    ) == []
    armenia_jobs = GreenhouseSource.parse_payload(
        payload,
        SourceContext(user_id=1, target_countries=["AM"], queries=["Data Engineer"]),
    )
    assert len(armenia_jobs) == 1
    assert armenia_jobs[0].country == "AM"
    assert armenia_jobs[0].city == "Yerevan"


def test_greenhouse_support_requires_explicit_employer_evidence():
    offered = GreenhouseSource.parse_payload(
        {"jobs": [listing(1, "Infrastructure Engineer", "Georgian office", "We offer visa sponsorship and relocation assistance.")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    unknown = GreenhouseSource.parse_payload(
        {"jobs": [listing(2, "Infrastructure Engineer", "Georgian office", "Candidates may need a visa.")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    refused = GreenhouseSource.parse_payload(
        {"jobs": [listing(3, "Infrastructure Engineer", "Georgian office", "No visa sponsorship. Relocation assistance is not available.")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]

    assert offered.visa_sponsorship is True
    assert offered.relocation is True
    assert offered.raw["support_evidence"]["visa_sponsorship"] == "We offer visa sponsorship"
    assert unknown.visa_sponsorship is None
    assert unknown.relocation is None
    assert refused.visa_sponsorship is False
    assert refused.relocation is False


def test_greenhouse_cleans_html_entities_in_posting_content():
    job = GreenhouseSource.parse_payload(
        {
            "jobs": [
                listing(
                    4,
                    "Infrastructure Engineer",
                    "Georgian office",
                    "&lt;p&gt;&lt;strong&gt;Linux&lt;/strong&gt;&lt;/p&gt;"
                    "&lt;ul&gt;&lt;li&gt;We offer visa sponsorship.&lt;/li&gt;&lt;/ul&gt;",
                )
            ]
        },
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]

    assert job.description == "Linux\nWe offer visa sponsorship."
    assert job.visa_sponsorship is True


@pytest.mark.parametrize("description", [
    "We offer visa sponsorship guidance.",
    "We provide information about visa sponsorship.",
    "We may offer visa sponsorship and relocation assistance.",
    "Visa sponsorship is required.",
])
def test_greenhouse_guidance_and_conditional_support_remain_unknown(description):
    job = GreenhouseSource.parse_payload(
        {"jobs": [listing(42, "Infrastructure Engineer", "Tbilisi, Georgia", description)]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert job.raw["support_evidence"] == {}


def test_greenhouse_later_explicit_refusal_outranks_offer():
    job = GreenhouseSource.parse_payload(
        {"jobs": [listing(42, "Infrastructure Engineer", "Tbilisi, Georgia",
                          "We offer visa sponsorship. We cannot provide visa sponsorship.")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    assert job.visa_sponsorship is False
    assert "visa_sponsorship" not in job.raw["support_evidence"]


def test_greenhouse_hybrid_location_is_not_promoted_to_fully_remote():
    job = GreenhouseSource.parse_payload(
        {"jobs": [listing(42, "Infrastructure Engineer", "Tbilisi, Georgia (hybrid / remote)")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    assert job.work_mode == "hybrid"
    assert job.country == "GE"


def test_greenhouse_remote_location_keeps_explicit_country_limit():
    from app.agents.job_signals import analyze_job_signals
    from app.database.models import Job

    job = GreenhouseSource.parse_payload(
        {"jobs": [listing(42, "Infrastructure Engineer", "Remote - Tbilisi, Georgia",
                          "Work from anywhere.")]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]
    assert job.remote_scope == "Remote - Tbilisi, Georgia"
    result = analyze_job_signals(Job(title=job.title, description=job.description,
                                    country=job.country, work_mode=job.work_mode,
                                    remote_scope=job.remote_scope))
    assert result.remote_eligibility == "uncertain"


def test_greenhouse_preserves_lineate_singular_qualification_heading():
    job = GreenhouseSource.parse_payload(
        {
            "jobs": [
                listing(
                    5,
                    "Infrastructure Engineer",
                    "Georgian office",
                    "&lt;h3&gt;Necessary Qualification:&lt;/h3&gt;"
                    "&lt;ul&gt;&lt;li&gt;Minimum 3 years of Linux system administration experience.&lt;/li&gt;"
                    "&lt;li&gt;Minimum 2 years of AWS production experience.&lt;/li&gt;&lt;/ul&gt;",
                )
            ]
        },
        SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"]),
    )[0]

    importance = extract_requirement_importance(job.description)
    assert importance["Linux"] == "required"
    assert importance["AWS"] == "required"


def test_greenhouse_discovery_uses_the_public_board_api(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(
            200,
            json={"jobs": [listing(8018252, "Infrastructure Engineer", "Georgian office")]},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(
        GreenhouseSource().discover(
            SourceContext(user_id=1, target_countries=["GE"], queries=["Infrastructure Engineer"])
        )
    )

    assert len(jobs) == 1
    assert calls[0][0] == GreenhouseSource.endpoint
    assert calls[0][1]["params"] == {"content": "true"}


def test_greenhouse_does_not_request_a_board_for_unselected_markets(monkeypatch):
    async def unexpected_get(*args, **kwargs):
        raise AssertionError("no board request should be made")

    monkeypatch.setattr(httpx.AsyncClient, "get", unexpected_get)
    assert asyncio.run(
        GreenhouseSource().discover(
            SourceContext(user_id=1, current_country="RU", queries=["DevOps Engineer"])
        )
    ) == []


def test_greenhouse_rejects_an_unrecognized_api_payload():
    with pytest.raises(ValueError, match="contract unavailable"):
        GreenhouseSource.parse_payload({"error": "unavailable"}, SourceContext(user_id=1, target_countries=["GE"]))


def test_greenhouse_is_registered_as_public_discovery_only():
    plans = build_source_plan("RU", ["GE"])
    greenhouse = next(plan for plan in plans if plan.source_id == "greenhouse")
    assert greenhouse.implemented
    assert not source_capabilities("greenhouse").apply
    assert not any(plan.source_id == "greenhouse" for plan in build_source_plan("RU", []))
