from app.matching.language_fit import compare_english_level, extract_english_level


def test_extracts_explicit_english_cefr_in_english_and_russian():
    assert extract_english_level("English level B2 is required.") == (
        "B2", "English level B2",
    )
    assert extract_english_level("Английский язык не ниже B1+.") == (
        "B1+", "Английский язык не ниже B1+",
    )
    assert extract_english_level("C1 English required") == (
        "C1", "C1 English",
    )


def test_language_fit_compares_only_normalized_profile_level():
    assert compare_english_level("English B1+", "B2").status == "meets"
    assert compare_english_level("English B1+", "B1").status == "below"
    assert compare_english_level("English B2", "upper-intermediate").status == "unknown"


def test_language_fit_keeps_missing_and_ambiguous_evidence_unknown():
    assert compare_english_level("Fluent English required", "B2") is None
    assert compare_english_level("English course from B1 to B2", "B2") is None
    assert compare_english_level("Python B2B platform", "B2") is None


def test_language_fit_reports_only_explicit_required_or_preferred_status():
    assert compare_english_level("English B2 required", "B2").requirement == "required"
    assert compare_english_level("English B2 preferred", "B2").requirement == "preferred"
    assert compare_english_level("English B2", "B2").requirement == "unspecified"
    assert compare_english_level("Английский B1 будет плюсом", "B2").requirement == "preferred"
    assert compare_english_level("English B2 preferred and mandatory", "B2").requirement == "unspecified"
    assert compare_english_level("English B2 is not required", "B2").requirement == "unspecified"
    assert compare_english_level("Английский B1 не требуется", "B2").requirement == "unspecified"
