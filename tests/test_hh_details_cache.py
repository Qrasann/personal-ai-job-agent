import asyncio
from types import SimpleNamespace

from app import services
from app.domain.source_posting import posting_snapshot_digest, source_posting_view


def test_hh_details_cache_fetches_once_then_reuses_source_ref_raw(monkeypatch):
    stored_raw = {}
    ref = SimpleNamespace(
        id=91,
        job_id=24,
        source_id="hh",
        source_job_id="134520461",
        raw=stored_raw,
    )
    vacancy_calls = []
    update_calls = []

    async def fake_source_ref(job_id, source_id=None):
        assert job_id == 24
        assert source_id == "hh"
        return ref

    async def fake_save_source_ref_detail_cache(ref_id, details, *, expected_posting_digest=None):
        assert ref_id == 91
        assert expected_posting_digest is None
        update_calls.append(dict(details))
        stored_raw["details_cache_v1"] = dict(details)

    async def fake_vacancy_web(source_job_id):
        vacancy_calls.append(source_job_id)
        return "<html>full vacancy</html>"

    def fake_parse(html):
        assert html == "<html>full vacancy</html>"
        return {
            "description": "Требования:\\nLinux\\nDocker",
            "salary_to": 300000,
            "salary_currency": "RUR",
        }

    monkeypatch.setattr(services.repo, "source_ref", fake_source_ref)
    monkeypatch.setattr(services.repo, "save_source_ref_detail_cache", fake_save_source_ref_detail_cache)
    monkeypatch.setattr(services.hh_client, "vacancy_web", fake_vacancy_web)
    monkeypatch.setattr(services.HHSource, "parse_vacancy_web_html", staticmethod(fake_parse))

    first = asyncio.run(services.get_cached_hh_details(24))
    second = asyncio.run(services.get_cached_hh_details(24))

    assert first == second
    assert first["description"] == "Требования:\\nLinux\\nDocker"
    assert vacancy_calls == ["134520461"]
    assert len(update_calls) == 1
    assert stored_raw["details_cache_v1"] == first


def test_hh_details_cache_returns_empty_without_hh_source(monkeypatch):
    async def fake_source_ref(job_id, source_id=None):
        return None

    monkeypatch.setattr(services.repo, "source_ref", fake_source_ref)

    result = asyncio.run(services.get_cached_hh_details(999))

    assert result == {}


def test_changed_source_snapshot_does_not_overlay_old_verified_details():
    old = {"schema": "normalized_posting_v1", "title": "Engineer", "description": "Old card"}
    current = {"schema": "normalized_posting_v1", "title": "Engineer", "description": "New card"}
    job = SimpleNamespace(id=24, title="Canonical", company="Example", description="Canonical text")
    ref = SimpleNamespace(raw={
        "normalized_posting_v1": current,
        "details_cache_v1": {"description": "Old full details"},
        "details_cache_posting_digest_v1": posting_snapshot_digest(old),
    })

    view = source_posting_view(job, ref)

    assert view.description == "New card"
    assert ref.raw["details_cache_v1"]["description"] == "Old full details"


def test_stale_hh_details_cache_refetches_after_source_card_changes(monkeypatch):
    old = {"schema": "normalized_posting_v1", "title": "Engineer", "description": "Old card"}
    current = {"schema": "normalized_posting_v1", "title": "Engineer", "description": "New card"}
    ref = SimpleNamespace(id=91, source_job_id="134520461", raw={
        "normalized_posting_v1": current,
        "details_cache_v1": {"description": "Old full details"},
        "details_cache_posting_digest_v1": posting_snapshot_digest(old),
    })
    fetched = []
    saved = []

    async def fake_web(source_job_id):
        fetched.append(source_job_id)
        return "<html>new full details</html>"

    async def fake_save(ref_id, details, *, expected_posting_digest=None):
        saved.append((ref_id, dict(details), expected_posting_digest))

    monkeypatch.setattr(services.repo, "source_ref", lambda *_: asyncio.sleep(0, result=ref))
    monkeypatch.setattr(services.hh_client, "vacancy_web", fake_web)
    monkeypatch.setattr(services.HHSource, "parse_vacancy_web_html", staticmethod(
        lambda _: {"description": "New full details"}
    ))
    monkeypatch.setattr(services.repo, "save_source_ref_detail_cache", fake_save)

    result = asyncio.run(services.get_cached_hh_details(24))

    assert result == {"description": "New full details"}
    assert fetched == ["134520461"]
    assert saved == [(91, result, posting_snapshot_digest(current))]

def test_get_vacancy_details_uses_cached_hh_details(monkeypatch):
    match = SimpleNamespace(profile_id=1, search_profile_id=3)
    job = SimpleNamespace(
        id=24,
        description="short card text",
    )
    ref = SimpleNamespace(
        id=91,
        job_id=24,
        source_id="hh",
        source_job_id="134520461",
        url="https://hh.ru/vacancy/134520461",
        raw={},
    )
    cache_calls = []
    refresh_calls = []

    async def fake_match(user_id, job_id):
        assert user_id == 7
        assert job_id == 24
        return match

    async def fake_job(job_id):
        assert job_id == 24
        return job

    async def fake_source_ref(job_id, source_id=None):
        if source_id == "hh":
            return ref
        return None

    async def fake_cached(job_id):
        cache_calls.append(job_id)
        return {
            "description": "Требования:\nLinux\nDocker",
            "salary_to": 300000,
            "salary_currency": "RUR",
        }

    async def fake_refresh(match_arg, job_arg, *, technical_text=""):
        refresh_calls.append(technical_text)
        return match_arg

    async def forbidden_direct_fetch(*args, **kwargs):
        raise AssertionError("get_vacancy_details must use HH cache helper")

    monkeypatch.setattr(
        services.repo,
        "get_match_for_user_job",
        fake_match,
    )
    monkeypatch.setattr(
        services.repo,
        "get_job",
        fake_job,
    )
    monkeypatch.setattr(
        services.repo,
        "source_ref",
        fake_source_ref,
    )
    monkeypatch.setattr(
        services,
        "get_cached_hh_details",
        fake_cached,
    )
    monkeypatch.setattr(
        services,
        "refresh_match_score",
        fake_refresh,
    )
    async def fake_searches(profile_id):
        assert profile_id == 1
        return [SimpleNamespace(id=3, name="Career-first")]

    monkeypatch.setattr(services.repo, "list_search_profiles", fake_searches)
    monkeypatch.setattr(
        services.hh_client,
        "vacancy_web",
        forbidden_direct_fetch,
    )

    payload = asyncio.run(
        services.get_vacancy_details(7, 24)
    )

    assert cache_calls == [24]
    assert refresh_calls == ["Требования:\nLinux\nDocker"]
    assert payload["details"]["description"] == "Требования:\nLinux\nDocker"
    assert payload["search_profile_name"] == "Career-first"
    assert payload["source"] == "hh"
