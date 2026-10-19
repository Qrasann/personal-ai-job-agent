import json
from pathlib import Path

import pytest

from app.sources.telegram_pilot import analyze_sample, load_private_sample


def _profile(path: Path) -> None:
    path.write_text("""
candidate:
  facts: [Linux Docker]
geography:
  remote_worldwide: true
  relocation_enabled: true
search:
  queries: [DevOps Engineer]
  relocation_queries: [Linux Administrator]
  preferred_terms: [linux]
  strong_terms: [docker]
  notify_min_score: 60
  modes: {local_ru: true, remote_international: true, relocation: true}
""", encoding="utf-8")


def _post(message_id: int, text: str) -> dict:
    return {
        "channel_id": -1001134745498, "username": "devops_jobs_feed",
        "message_id": message_id, "text": text,
        "published_at": "2026-10-18T12:00:00+00:00",
        "url": f"https://t.me/devops_jobs_feed/{message_id}",
    }


def test_private_sample_rejects_open_permissions_and_unapproved_channel(tmp_path: Path):
    path = tmp_path / "pilot-sample.json"
    path.write_text(json.dumps({"schema": 1, "posts": [_post(1, "DevOps")]}), encoding="utf-8")
    path.chmod(0o644)
    with pytest.raises(ValueError, match="0600"):
        load_private_sample(path)

    path.chmod(0o600)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["posts"][0]["channel_id"] = -100999
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="approved contract"):
        load_private_sample(path)


def test_analysis_counts_non_vacancy_dedupe_and_scoring(tmp_path: Path):
    profile = tmp_path / "profile.yaml"
    _profile(profile)
    text = "Position: DevOps Engineer\nCompany: Example\nRemote worldwide\nLinux Docker"
    posts = [_post(1, text), _post(2, text), _post(3, "Ищу работу: DevOps")]

    report = analyze_sample(posts, profile)

    assert report["totals"]["posts"] == 3
    assert report["totals"]["non_vacancy"] == 1
    assert report["totals"]["vacancy_candidates"] == 2
    assert report["totals"]["unique_vacancies"] == 1
    assert report["totals"]["duplicates"] == 1
    assert len(report["vacancies"]) == 2


def test_analysis_rejects_candidate_tag_after_channel_metadata(tmp_path: Path):
    profile = tmp_path / "profile.yaml"
    _profile(profile)
    posts = [_post(
        1,
        "Публикатор: Иван\nОбсуждение: @devops_jobs\n"
        "#резюме #devops #remote\nDevOps Engineer\nLinux Docker",
    )]

    report = analyze_sample(posts, profile)

    assert report["totals"] == {"posts": 1, "non_vacancy": 1, "unique_vacancies": 0, "duplicates": 0}
    assert report["vacancies"] == []
