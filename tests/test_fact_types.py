from app.candidates.fact_types import (
    ALLOWED_EXPERIENCE_TYPES,
    experience_type_label,
    is_commercial_type,
    normalize_experience_type,
)
from app.database.models import CandidateFact


def test_allowed_fact_types_are_explicit():
    assert ALLOWED_EXPERIENCE_TYPES == ("commercial", "lab", "learning", "unknown")


def test_fact_type_aliases_normalize():
    assert normalize_experience_type("commercial") == "commercial"
    assert normalize_experience_type("коммерческий") == "commercial"
    assert normalize_experience_type("lab") == "lab"
    assert normalize_experience_type("проект") == "lab"
    assert normalize_experience_type("study") == "learning"
    assert normalize_experience_type("обучение") == "learning"
    assert normalize_experience_type("unknown") == "unknown"
    assert normalize_experience_type("invented") is None


def test_commercial_is_derived_from_type():
    assert is_commercial_type("commercial") is True
    assert is_commercial_type("lab") is False
    assert is_commercial_type("learning") is False


def test_fact_type_labels_are_stable():
    assert experience_type_label("commercial") == "[commercial]"
    assert experience_type_label("lab") == "[lab]"
    assert experience_type_label("learning") == "[learning]"
    assert experience_type_label(None) == "[unknown]"


def test_candidate_fact_model_has_experience_type():
    assert hasattr(CandidateFact, "experience_type")
