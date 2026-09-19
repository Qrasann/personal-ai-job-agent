import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.export import export_to_json, export_to_markdown, prepare_export_data
from app.telegram import handlers


def test_prepare_export_data_and_serialization():
    match = SimpleNamespace(
        id=101,
        total_score=85,
        technical_score=80,
        geography_score=90,
        salary_score=70,
        relocation_score=100,
        reason="DevOps fit",
        status="saved",
        created_at=None,
    )
    job = SimpleNamespace(
        id=55,
        title="Senior SRE",
        company="TechCorp",
        description="Kubernetes & Terraform operations",
        city="Москва",
        country="RU",
        work_mode="remote",
        remote_scope="RU only",
        relocation=False,
        visa_sponsorship=False,
        salary_from=300000,
        salary_to=400000,
        salary_currency="RUR",
        published_at="2026-09-19",
    )

    urls = {55: "https://hh.ru/vacancy/55"}
    data = prepare_export_data([(match, job)], urls)

    assert len(data) == 1
    assert data[0]["title"] == "Senior SRE"
    assert data[0]["url"] == "https://hh.ru/vacancy/55"
    assert data[0]["total_score"] == 85

    md_output = export_to_markdown(data)
    assert "# ⭐ Сохранённые вакансии" in md_output
    assert "## 1. Senior SRE — TechCorp" in md_output
    assert "https://hh.ru/vacancy/55" in md_output
    assert "Kubernetes & Terraform operations" in md_output

    json_output = export_to_json(data)
    assert '"title": "Senior SRE"' in json_output
    assert '"company": "TechCorp"' in json_output


def test_export_command_when_empty(monkeypatch):
    message = SimpleNamespace(
        text="/export",
        answer=AsyncMock(),
        answer_document=AsyncMock(),
    )
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=1)))
    monkeypatch.setattr(handlers.repo, "saved_matches", AsyncMock(return_value=[]))

    asyncio.run(handlers.export_saved_command(message))

    assert message.answer.await_count == 1
    assert "Сохранённых вакансий пока нет" in message.answer.await_args.args[0]
    assert message.answer_document.await_count == 0


def test_export_command_sends_markdown_file(monkeypatch):
    match = SimpleNamespace(
        id=1,
        total_score=90,
        technical_score=90,
        geography_score=90,
        salary_score=90,
        relocation_score=90,
        reason="Fit",
        status="saved",
    )
    job = SimpleNamespace(
        id=10,
        title="DevOps",
        company="Cloud LLC",
        description="CI/CD",
        city="СПб",
        country="RU",
        work_mode="remote",
        remote_scope="",
        relocation=False,
        visa_sponsorship=False,
        salary_from=200000,
        salary_to=None,
        salary_currency="RUR",
        published_at="",
    )

    message = SimpleNamespace(
        text="/export",
        answer=AsyncMock(),
        answer_document=AsyncMock(),
    )

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=1)))
    monkeypatch.setattr(handlers.repo, "saved_matches", AsyncMock(return_value=[(match, job)]))
    monkeypatch.setattr(handlers.repo, "source_ref", AsyncMock(return_value=SimpleNamespace(url="https://test.link")))

    asyncio.run(handlers.export_saved_command(message))

    assert message.answer_document.await_count == 1
    kwargs = message.answer_document.await_args.kwargs
    doc = kwargs["document"]
    assert doc.filename.endswith(".md")
    assert b"DevOps" in doc.data


def test_export_command_sends_json_file(monkeypatch):
    match = SimpleNamespace(
        id=2,
        total_score=80,
        technical_score=80,
        geography_score=80,
        salary_score=80,
        relocation_score=80,
        reason="Fit",
        status="saved",
    )
    job = SimpleNamespace(
        id=20,
        title="Platform Eng",
        company="Infra Ltd",
        description="K8s",
        city="Москва",
        country="RU",
        work_mode="hybrid",
        remote_scope="",
        relocation=False,
        visa_sponsorship=False,
        salary_from=250000,
        salary_to=300000,
        salary_currency="RUR",
        published_at="",
    )

    message = SimpleNamespace(
        text="/export json",
        answer=AsyncMock(),
        answer_document=AsyncMock(),
    )

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=1)))
    monkeypatch.setattr(handlers.repo, "saved_matches", AsyncMock(return_value=[(match, job)]))
    monkeypatch.setattr(handlers.repo, "source_ref", AsyncMock(return_value=None))

    asyncio.run(handlers.export_saved_command(message))

    assert message.answer_document.await_count == 1
    doc = message.answer_document.await_args.kwargs["document"]
    assert doc.filename.endswith(".json")
    assert b"Platform Eng" in doc.data
