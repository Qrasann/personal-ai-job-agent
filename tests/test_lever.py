import asyncio

import httpx

from app.domain.jobs import NormalizedJob
from app.domain.job_text import format_salary
from app.sources.adapters.lever import LeverSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities


def posting(
    posting_id="3240d98f-b916-46d4-a89e-3ae4aa988338",
    title="Senior DevOps/DevSecOps Engineer (remote from GMT-7 to GMT+4 timezones)",
    *,
    location="Belgrade",
    country="RS",
    workplace_type="remote",
    description="Build and maintain reliable infrastructure with Terraform and Ansible.",
    timezone="GMT-7 to GMT+4",
):
    return {
        "id": posting_id,
        "text": title,
        "categories": {"location": location, "team": "Engineering", "commitment": "Full-Time Remote"},
        "country": country,
        "workplaceType": workplace_type,
        "createdAt": 1787653588686,
        "hostedUrl": f"https://jobs.lever.co/CollectlyInc/{posting_id}",
        "descriptionPlain": f"About the role\n{description}\n{timezone}",
        "lists": [
            {
                "text": "Required Qualifications",
                "content": "<li>Terraform and Ansible</li><li>Fluency in English</li>",
            }
        ],
        "salaryRange": {"currency": "USD", "interval": "per-year", "min": 100000, "max": 140000},
    }


def test_lever_collectly_keeps_remote_timezone_scope_and_hiring_country_unknown():
    job = LeverSource.parse_payload(
        [posting()],
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )[0]

    assert isinstance(job, NormalizedJob)
    assert job.source == "lever"
    assert job.source_job_id == "CollectlyInc:3240d98f-b916-46d4-a89e-3ae4aa988338"
    assert job.company == "Collectly"
    assert job.country is None
    assert job.city is None
    assert job.work_mode == "remote"
    assert job.remote_scope == "GMT-7 to GMT+4 time zones"
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert job.salary_from == 100000
    assert job.salary_to == 140000
    assert job.salary_currency == "USD"
    assert job.salary_period == "per-year"
    assert format_salary(
        job.salary_from, job.salary_to, job.salary_currency, period=job.salary_period,
    ) == "100 000–140 000 $ в год"
    assert "Fluency in English" in job.description
    assert job.raw["source_location"] == "Belgrade"
    assert job.raw["source_country"] == "RS"


def test_lever_only_keeps_role_relevant_remote_jobs_with_plus_four_scope():
    rows = [
        posting(),
        posting(posting_id="onsite", workplace_type="on-site"),
        posting(
            posting_id="no-plus-four",
            title="Senior DevOps/DevSecOps Engineer (remote from GMT-7 to GMT+2 timezones)",
            timezone="GMT-7 to GMT+2",
        ),
        posting(posting_id="unrelated", title="Senior Product Data Analyst"),
        posting(posting_id="bad-url").copy(),
    ]
    rows[-1]["hostedUrl"] = "https://example.com/CollectlyInc/bad-url"

    jobs = LeverSource.parse_payload(
        rows,
        SourceContext(user_id=1, target_countries=["AM"], queries=["DevOps Engineer"]),
    )

    assert [job.source_job_id for job in jobs] == [
        "CollectlyInc:3240d98f-b916-46d4-a89e-3ae4aa988338"
    ]


def test_lever_is_not_requested_without_an_armenia_or_georgia_target(monkeypatch):
    async def unexpected_get(*args, **kwargs):
        raise AssertionError("Lever should only be requested for selected AM/GE markets")

    monkeypatch.setattr(httpx.AsyncClient, "get", unexpected_get)
    assert asyncio.run(
        LeverSource().discover(SourceContext(user_id=1, current_country="RU", queries=["DevOps Engineer"]))
    ) == []


def test_lever_discovery_uses_the_public_postings_api_with_bounded_pagination(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json=[posting()], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(
        LeverSource().discover(
            SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
        )
    )

    assert len(jobs) == 1
    assert calls[0][0] == LeverSource.endpoint
    assert calls[0][1]["params"] == {"mode": "json", "skip": 0, "limit": LeverSource.page_size}


def test_lever_rejects_an_unrecognized_public_api_payload():
    try:
        LeverSource.parse_payload({"error": "unavailable"}, SourceContext(user_id=1, target_countries=["GE"]))
    except ValueError as exc:
        assert "contract unavailable" in str(exc)
    else:
        raise AssertionError("expected malformed Lever payload to be rejected")


def test_lever_is_registered_for_am_ge_as_public_discovery_only():
    plan = next(item for item in build_source_plan("RU", ["GE"]) if item.source_id == "lever")

    assert plan.implemented
    assert plan.scope == "remote · selected AM/GE"
    assert not source_capabilities("lever").apply
    assert not source_capabilities("lever").messages
    assert not any(item.source_id == "lever" for item in build_source_plan("RU", []))
