import pytest

from app.domain.support_evidence import existing_work_authorization_required, support_evidence


@pytest.mark.parametrize("text", [
    "We do not provide visa sponsorship or relocation assistance.",
    "We cannot offer visa sponsorship and relocation assistance.",
    "We don’t provide visa sponsorship or relocation assistance.",
    "Visa sponsorship and relocation assistance are not available.",
    "No visa sponsorship or relocation assistance is provided.",
])
def test_shared_refusal_negates_each_named_support_component(text):
    evidence = support_evidence(text)
    assert evidence["visa_sponsorship"] is False
    assert evidence["relocation"] is False
    assert evidence["relocation_package"] is False
    assert not any(value is True for value in evidence.values())


@pytest.mark.parametrize("text", [
    "We provide visa sponsorship and relocation assistance.",
    "Visa sponsorship and relocation assistance are provided.",
    "No previous experience required; we offer visa sponsorship and relocation assistance.",
    "<p>We provide visa sponsorship.</p><p>Relocation assistance is available.</p>",
])
def test_affirmative_employer_offer_remains_useful(text):
    evidence = support_evidence(text)
    assert evidence["visa_sponsorship"] is True
    assert evidence["relocation"] is True
    assert evidence["relocation_package"] is True


@pytest.mark.parametrize("text", [
    "Visa sponsorship and relocation assistance.",
    "Visa sponsorship may be available. Relocation assistance might be provided.",
    "We provide visa sponsorship guidance and relocation support information.",
    "We offer information about visa sponsorship and relocation assistance.",
    "Visa sponsorship required; relocation assistance eligibility is discussed during hiring.",
    "Relocation is required. Candidates must already have the right to work in Germany.",
    "No relocation required. No visa sponsorship needed.",
])
def test_mentions_guidance_conditions_and_prerequisites_stay_unknown(text):
    assert all(value is None for value in support_evidence(text).values())


def test_unrelated_support_status_does_not_apply_to_another_subject():
    evidence = support_evidence("Visa sponsorship required, relocation assistance is provided.")
    assert evidence["visa_sponsorship"] is None
    assert evidence["relocation"] is True


def test_component_refusals_do_not_contaminate_separate_offers():
    evidence = support_evidence("Relocation assistance is provided and visa sponsorship is not available.")
    assert evidence["relocation"] is True
    assert evidence["visa_sponsorship"] is False
    evidence = support_evidence("We do not provide relocation assistance, but we offer visa sponsorship.")
    assert evidence["relocation"] is False
    assert evidence["visa_sponsorship"] is True


def test_later_explicit_refusal_overrides_an_earlier_offer():
    evidence = support_evidence("We provide visa sponsorship. Visa sponsorship is not available.")
    assert evidence["visa_sponsorship"] is False


@pytest.mark.parametrize("text, key, expected", [
    ("We provide a relocation package and work permit support.", "work_permit", True),
    ("Work permit support is not available.", "work_permit", False),
    ("Work permit required.", "work_permit", None),
    ("You must obtain a work permit.", "work_permit", None),
    ("We provide work permit information.", "work_permit", None),
    ("Wir bieten Visum-Unterstützung und Umzugshilfe.", "visa_sponsorship", True),
    ("Wir bieten keine Visum-Unterstützung und Umzugshilfe.", "relocation", False),
    ("Предоставляем визовую поддержку и релокационный пакет.", "relocation", True),
    ("Не предоставляем визовую поддержку и релокационный пакет.", "visa_sponsorship", False),
])
def test_permit_assistance_and_supported_multilingual_phrases(text, key, expected):
    assert support_evidence(text)[key] is expected


def test_existing_authorization_requirement_is_separate_from_support():
    text = "Must already have the right to work in Germany."
    assert existing_work_authorization_required(text)
    assert support_evidence(text)["work_permit"] is None
    assert not existing_work_authorization_required("We offer work permit support.")
    assert not existing_work_authorization_required("No EU work permit required.")


@pytest.mark.parametrize("text", [
    "Warehouse worker with relocation assistance",
    "Remote worldwide with relocation assistance.",
    "Junior DevOps Engineer with visa sponsorship.",
])
def test_concrete_vacancy_with_support_is_an_affirmative_benefit(text):
    evidence = support_evidence(text)
    key = "visa_sponsorship" if "visa sponsorship" in text else "relocation"
    assert evidence[key] is True


@pytest.mark.parametrize("text, expected", [
    ("Remote worldwide with no relocation assistance.", False),
    ("Warehouse worker with no relocation assistance.", False),
    ("Remote worldwide with questions about relocation assistance.", None),
    ("Warehouse worker with relocation assistance guidance.", None),
    ("Remote worldwide with potential relocation assistance.", None),
    ("Warehouse worker with relocation assistance may be available.", None),
    ("Remote worldwide with relocation assistance if approved.", None),
    ("Warehouse worker with relocation assistance required.", None),
])
def test_with_descriptor_preserves_refusal_information_and_conditions(text, expected):
    assert support_evidence(text)["relocation"] is expected
