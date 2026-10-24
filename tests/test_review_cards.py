from types import SimpleNamespace

from app.telegram.handlers import (
    _render_review_card,
    _render_saved_card,
    _render_stretch_card,
)
from app.matching.engine import MATCH_ASSESSMENT_VERSION


def _match():
    return SimpleNamespace(
        total_score=82,
        technical_score=86,
        geography_score=95,
        salary_score=72,
        relocation_score=50,
        reason="роль: devops engineer; совпадения: linux, docker, nginx",
        recommendation_scores={"_meta": {"match_assessment_version": MATCH_ASSESSMENT_VERSION}},
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
    assert "Подходит по текущему профилю" in text
    assert "82/100" not in text
    assert "Отклики: Нет открытых данных" in text
    assert "Иностранный найм" in text
    assert "Tech 86" not in text
    assert "совпадения: linux, docker, nginx" in text
    assert "2 из 7" in text


def test_review_card_flags_explicit_volunteer_work_as_unpaid():
    job = _job()
    job.title = "Makerble DevOps Volunteer"
    job.description = "This is an unpaid volunteer opportunity."

    text = _render_review_card(_match(), job, 1, 1)

    assert "Оплачиваемость: нет — явно волонтёрская/неоплачиваемая" in text


def test_stale_good_assessment_is_not_presented_as_current_good():
    job = _job()
    job.title = "DevOps Volunteer"
    match = _match()

    text = _render_review_card(match, job, 1, 1)

    assert "🟢 Good" not in text
    assert "Требует повторной проверки" in text
    assert "сохранённая оценка может быть устаревшей" in text.casefold()
    assert "88/100" not in text
    assert "волонтёрская/неоплачиваемая роль" in text


def test_legacy_good_without_assessment_version_hides_old_score_and_requests_scan():
    match = _match()
    match.recommendation_scores = {}

    text = _render_review_card(match, _job(), 1, 1)

    assert "Good" not in text
    assert "Требует обновления оценки" in text
    assert "устарела" in text
    assert "/scan" in text
    assert "82/100" not in text


def test_queue_cards_use_truthful_lane_labels():
    assert "🟢 Good" in _render_review_card(_match(), _job(), 1, 1)
    assert "🟡 Stretch" in _render_stretch_card(_match(), _job(), 1, 1)
    assert "⭐ Saved" in _render_saved_card(_match(), _job(), 1, 1)
