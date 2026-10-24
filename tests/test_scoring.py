from app.agents.scoring import score_vacancy


def test_good_devops():
    v = {
        "name": "Junior DevOps Engineer",
        "description": "Linux Docker Nginx Git Bash Prometheus",
        "experience": {"id": "between1And3"},
        "work_format": [{"id": "REMOTE", "name": "Удаленно"}],
        "salary": {"from": 150000, "currency": "RUR", "gross": False},
    }
    score, _ = score_vacancy(v)
    assert score >= 80


def test_betting_sector_is_not_a_default_exclusion():
    v = {"name": "DevOps Engineer", "description": "betting platform", "experience": {"id": "between1And3"}}
    score, _ = score_vacancy(v)
    assert score > 0
