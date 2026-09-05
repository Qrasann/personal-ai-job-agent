import asyncio
from types import SimpleNamespace

from app import services


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

    async def fake_update_source_ref_raw(ref_id, raw):
        assert ref_id == 91
        update_calls.append(dict(raw))
        stored_raw.clear()
        stored_raw.update(raw)

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
    monkeypatch.setattr(services.repo, "update_source_ref_raw", fake_update_source_ref_raw)
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

def test_get_vacancy_details_uses_cached_hh_details(monkeypatch):
    match = SimpleNamespace(profile_id=1)
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
    assert payload["source"] == "hh"
