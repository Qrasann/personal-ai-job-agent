from pathlib import Path

import yaml


def test_ai_job_bot_defaults_keep_georgia_and_armenia_parallel():
    path = Path(__file__).parents[1] / "data" / "profile.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))

    geography = config["geography"]
    assert geography["target_countries"] == ["GE", "AM"]
    assert geography["relocation_countries"] == ["GE", "AM"]
    assert config["candidate"]["english"] == "B1"
    assert config["candidate"]["technical_reading_english"] == "B2"
    assert config["search"]["queries"] == [
        "DevOps Engineer",
        "Infrastructure Engineer",
        "Linux Administrator",
        "Site Reliability Engineer",
    ]
    assert config["search"]["relocation_queries"] == [
        "warehouse worker",
        "production worker",
        "hotel staff",
        "kitchen assistant",
        "cleaner",
        "construction worker",
        "customer support",
    ]
