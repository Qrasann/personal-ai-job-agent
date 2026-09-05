import asyncio
from types import SimpleNamespace

from app import services
from app.domain.jobs import NormalizedJob


def _result(technical, total):
    return SimpleNamespace(
        resume_id=None,
        technical_score=technical,
        geography_score=95,
        salary_score=58,
        relocation_score=50,
        total_score=total,
        reason="test score",
        track="russia",
    )


def test_hh_ingest_rechecks_plausible_job_with_full_details(monkeypatch):
    normalized = NormalizedJob(
        source="hh",
        source_job_id="123",
        title="DevOps Engineer",
        company="Example",
        description="Linux Docker DevOps Engineer",
        country="RU",
    )

    job = SimpleNamespace(
        id=24,
        title="DevOps Engineer",
        company="Example",
        description=normalized.description,
        country="RU",
        city=None,
        salary_from=None,
        salary_to=None,
        salary_currency=None,
    )
    ref = SimpleNamespace(
        id=91,
        source_id="hh",
        source_job_id="123",
        url="https://hh.ru/vacancy/123",
        raw={},
    )
    user = SimpleNamespace(id=7, telegram_chat_id="777")
    profile = SimpleNamespace(id=8)
    search = SimpleNamespace(
        id=9,
        settings={"notify_min_score": 65},
    )

    score_calls = []
    details_calls = []
    statuses = []
    match_status = {"value": "existing"}

    async def fake_upsert_job(value):
        return job, False

    async def fake_source_ref(job_id, source_id=None):
        return ref

    async def fake_users():
        return [user]

    async def fake_state(user_id, key, default=""):
        return "false"

    async def fake_profile(user_id):
        return profile

    async def fake_facts(profile_id):
        return []

    async def fake_resumes(profile_id):
        return []

    async def fake_searches(profile_id):
        return [search]

    async def fake_save_match(**kwargs):
        return SimpleNamespace(id=301, status=match_status["value"])

    async def fake_set_status(match_id, status):
        statuses.append((match_id, status))

    async def fake_details(job_id):
        details_calls.append(job_id)
        return {
            "description": (
                "Требования:\n"
                "Linux\n"
                "Docker\n"
                "Kubernetes\n"
                "Nginx"
            )
        }

    def fake_score(job_arg, search_arg, facts, resumes, *, technical_text=None):
        score_calls.append(technical_text)
        if technical_text is None:
            return _result(60, 68)
        return _result(43, 60)

    monkeypatch.setattr(services.repo, "upsert_job", fake_upsert_job)
    monkeypatch.setattr(services.repo, "source_ref", fake_source_ref)
    monkeypatch.setattr(services.repo, "list_active_users", fake_users)
    monkeypatch.setattr(services.repo, "get_state", fake_state)
    monkeypatch.setattr(services.repo, "active_profile", fake_profile)
    monkeypatch.setattr(services.repo, "list_facts", fake_facts)
    monkeypatch.setattr(services.repo, "list_resumes", fake_resumes)
    monkeypatch.setattr(services.repo, "list_search_profiles", fake_searches)
    monkeypatch.setattr(services.repo, "save_match", fake_save_match)
    monkeypatch.setattr(services.repo, "set_match_status", fake_set_status)
    monkeypatch.setattr(services, "get_cached_hh_details", fake_details)
    monkeypatch.setattr(services, "score_job", fake_score)

    counters = asyncio.run(
        services.ingest_and_match(
            bot=object(),
            normalized=normalized,
            only_user_id=7,
        )
    )

    assert details_calls == [24]
    assert score_calls == [
        None,
        "Требования:\nLinux\nDocker\nKubernetes\nNginx",
    ]
    assert counters["processed"] == 1
    assert counters["qualified"] == 0
    assert counters["filtered"] == 1
    assert statuses == [(301, "filtered")]

    details_calls.clear()
    score_calls.clear()
    statuses.clear()

    monkeypatch.setattr(
        services,
        "_can_reach_threshold_with_technical",
        lambda result, threshold: False,
    )

    asyncio.run(
        services.ingest_and_match(
            bot=object(),
            normalized=normalized,
            only_user_id=7,
        )
    )

    assert details_calls == []
    assert score_calls == [None]

    details_calls.clear()
    score_calls.clear()
    statuses.clear()
    match_status["value"] = "saved"
    monkeypatch.setattr(services, "_can_reach_threshold_with_technical", lambda result, threshold: True)

    counters = asyncio.run(services.ingest_and_match(bot=object(), normalized=normalized, only_user_id=7))

    assert counters["filtered"] == 1
    assert statuses == []

def test_technical_prefilter_fetches_when_score_can_reach_threshold():
    result = _result(80, 55)
    assert services._can_reach_threshold_with_technical(result, 65) is True


def test_technical_prefilter_skips_when_even_perfect_technical_cannot_reach_threshold():
    result = _result(80, 54)
    assert services._can_reach_threshold_with_technical(result, 65) is False

def test_refresh_match_score_updates_scores_without_status(monkeypatch):
    match = SimpleNamespace(
        user_id=7, profile_id=8, search_profile_id=9, status="notified"
    )
    job = SimpleNamespace(id=24)
    search = SimpleNamespace(id=9)
    saved = {}

    async def facts(profile_id): return []
    async def resumes(profile_id): return []
    async def searches(profile_id): return [search]

    async def save_match(**kwargs):
        saved.update(kwargs)
        return SimpleNamespace(**kwargs, status="notified")

    def score(*args, technical_text=None, **kwargs):
        assert technical_text == "Требования:\nLinux"
        return _result(43, 60)

    monkeypatch.setattr(services.repo, "list_facts", facts)
    monkeypatch.setattr(services.repo, "list_resumes", resumes)
    monkeypatch.setattr(services.repo, "list_search_profiles", searches)
    monkeypatch.setattr(services.repo, "save_match", save_match)
    monkeypatch.setattr(services, "score_job", score)

    refreshed = asyncio.run(
        services.refresh_match_score(
            match, job, technical_text="Требования:\nLinux"
        )
    )

    assert refreshed.technical_score == 43
    assert refreshed.total_score == 60
    assert "status" not in saved
