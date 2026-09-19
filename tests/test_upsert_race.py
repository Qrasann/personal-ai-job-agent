import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from app.database import repository as repo
from app.domain.jobs import NormalizedJob


def test_upsert_job_handles_integrity_error_on_race(monkeypatch):
    job = NormalizedJob(
        source="hh",
        source_job_id="test_race_999",
        url="https://hh.ru/vacancy/test_race_999",
        title="DevOps Engineer",
        company="Race Corp",
        description="Race condition handling test",
        country="RU",
        city="Тверь",
        raw={},
    )

    mock_existing_job = MagicMock(id=42, fingerprint=job.canonical_fingerprint())

    # Моделируем сессию БД:
    # 1. source_ref -> None
    # 2. scalar(Job by fingerprint) -> None (оба потока не видят запись)
    # 3. flush() внутри begin_nested() -> выбрасывает IntegrityError (другой поток успел вставить)
    # 4. scalar(Job by fingerprint) в except блоке -> возвращает mock_existing_job
    # 5. ref_existing -> None
    # 6. flush() для JobSourceRef -> успешно
    scalar_mock = AsyncMock(side_effect=[None, None, mock_existing_job, None])
    flush_mock = AsyncMock(side_effect=[IntegrityError("duplicate key", params=None, orig=Exception()), None])
    commit_mock = AsyncMock()
    refresh_mock = AsyncMock()

    class DummyNested:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    class DummySession:
        scalar = scalar_mock
        flush = flush_mock
        commit = commit_mock
        refresh = refresh_mock

        def add(self, obj):
            pass

        def begin_nested(self):
            return DummyNested()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    monkeypatch.setattr(repo, "SessionLocal", lambda: DummySession())

    result_job, created = asyncio.run(repo.upsert_job(job))

    assert result_job.id == 42
    assert created is False
    assert commit_mock.await_count == 1
