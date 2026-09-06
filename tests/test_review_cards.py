from types import SimpleNamespace

from app.telegram.handlers import (
    _render_review_card,
    _render_saved_card,
    _render_stretch_card,
)


def _match():
    return SimpleNamespace(
        total_score=82,
        technical_score=86,
        geography_score=95,
        salary_score=72,
        relocation_score=50,
        reason="роль: devops engineer; совпадения: linux, docker, nginx",
    )


def _job():
    return SimpleNamespace(
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker Nginx",
        city="Тверь",
        country="RU",
        work_mode="Гибрид",
        salary_from=120000,
        salary_to=160000,
        salary_currency="RUB",
    )


def test_review_card_shows_rich_match_context():
    text = _render_review_card(_match(), _job(), 2, 7)
    assert "🟢 Good" in text
    assert "DevOps Engineer" in text
    assert "ACME" in text
    assert "120 000–160 000 ₽" in text
    assert "Тверь" in text
    assert "Гибрид" in text
    assert "82/100" in text
    assert "Tech 86" in text
    assert "Geo 95" in text
    assert "Salary 72" in text
    assert "Reloc 50" in text
    assert "совпадения: linux, docker, nginx" in text
    assert "2 из 7" in text


def test_queue_cards_use_truthful_lane_labels():
    assert "🟢 Good" in _render_review_card(_match(), _job(), 1, 1)
    assert "🟡 Stretch" in _render_stretch_card(_match(), _job(), 1, 1)
    assert "⭐ Saved" in _render_saved_card(_match(), _job(), 1, 1)
