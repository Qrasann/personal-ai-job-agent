import json
from datetime import datetime, timezone
from pathlib import Path

from app.domain.jobs import NormalizedJob
from app.domain.relocation_evidence import EVIDENCE_FIELDS, build_relocation_evidence


def _fixture_job():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/relocation_evidence/synthetic_job.json").read_text()
    )
    return NormalizedJob(
        source="synthetic_fixture", source_job_id="synthetic-101",
        title=fixture["title"], description=fixture["description"],
        country=fixture["country"], url=fixture["url"],
        raw={"source_location": fixture["source_location"]},
    )


def test_relocation_evidence_keeps_explicit_source_excerpt_and_capture_time():
    captured = datetime(2026, 10, 15, 12, 30, tzinfo=timezone.utc)
    evidence = build_relocation_evidence(_fixture_job(), captured_at=captured)

    assert evidence["schema"] == "relocation_evidence_v1"
    assert set(evidence["fields"]) == set(EVIDENCE_FIELDS)
    assert evidence["fields"]["work_country"] == {
        "status": "confirmed", "value": "DE", "source_id": "synthetic_fixture",
        "source_url": "https://jobs.example.invalid/synthetic-101", "excerpt": "Berlin, Germany",
        "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "source_structured",
    }
    auth = evidence["fields"]["existing_work_authorization_required"]
    assert auth["value"] is True and auth["status"] == "confirmed"
    assert "right to work in Germany" in auth["excerpt"]
    denied = evidence["fields"]["visa_sponsorship"]
    assert denied["value"] is False and "do not provide visa sponsorship" in denied["excerpt"]
    relocation = evidence["fields"]["relocation_assistance"]
    assert relocation["value"] is True and "Relocation assistance is available" in relocation["excerpt"]
    assert evidence["fields"]["language_requirement"]["value"]
    assert evidence["fields"]["start_timing"]["value"]
    assert evidence["fields"]["housing_provided"]["status"] == "unknown"
    assert evidence["fields"]["language_requirement"]["status"] == "confirmed"
    assert evidence["fields"]["start_timing"]["interpretation"]["kind"] == "stated_date"
    assert "Synthetic regression fixture" not in json.dumps(evidence)


def test_missing_relocation_evidence_is_unknown_not_refusal_or_offer():
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="unknown-1", title="Engineer",
        description="Technical role. No relocation details included.",
    )
    evidence = build_relocation_evidence(job)
    for field in EVIDENCE_FIELDS:
        item = evidence["fields"][field]
        assert item["status"] == "unknown"
        assert item["value"] is None
        assert item["excerpt"] is None
        assert item["source_id"] == "synthetic_fixture"
        assert item["captured_at"]
        assert item["confidence"] == "unknown"


def test_residence_restriction_excerpt_is_not_promoted_to_legal_judgment():
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="restriction-1", title="Engineer",
        description="Only candidates currently living in Germany may apply.", country="DE",
    )
    item = build_relocation_evidence(job)["fields"]["citizenship_or_residence_restriction"]
    assert item["status"] == "confirmed"
    assert item["value"] == item["excerpt"]
    assert "currently living in Germany" in item["excerpt"]


def test_housing_requires_explicit_provision_or_refusal_and_language_is_classified():
    def extract(description):
        job = NormalizedJob(
            source="synthetic_fixture", source_job_id="conditions-1",
            title="Engineer", description=description,
        )
        return build_relocation_evidence(job)["fields"]

    offered = extract("Accommodation is provided. English B2 is required.")
    assert offered["housing_provided"]["value"] is True
    assert offered["housing_provided"]["status"] == "confirmed"
    language = offered["language_requirement"]
    assert language["status"] == "confirmed"
    assert language["interpretation"]["requirements"] == [{
        "language": "English", "requirement": "required", "cefr": "B2",
        "excerpt": "English B2",
    }]

    denied = extract("Housing is not provided. German is preferred.")
    assert denied["housing_provided"]["value"] is False
    assert denied["language_requirement"]["interpretation"]["requirements"][0]["requirement"] == "preferred"

    russian_offered = extract("Жилье предоставляется работодателем.")
    assert russian_offered["housing_provided"]["status"] == "confirmed"
    assert russian_offered["housing_provided"]["value"] is True
    russian_denied = extract("Жильё не предоставляется.")
    assert russian_denied["housing_provided"]["status"] == "confirmed"
    assert russian_denied["housing_provided"]["value"] is False

    ambiguous = extract("Housing and English are mentioned in the posting.")
    assert ambiguous["housing_provided"]["status"] == "unknown"
    assert ambiguous["language_requirement"]["status"] == "observed"
    assert ambiguous["language_requirement"]["interpretation"]["requirements"][0]["requirement"] == "unspecified"


def test_multiple_language_conditions_keep_independent_evidence_and_conflict_unknown():
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="language-multiple", title="Engineer",
        description="English B2 preferred. German is required. English B1 is mandatory.",
    )
    evidence = build_relocation_evidence(job)["fields"]["language_requirement"]
    requirements = evidence["interpretation"]["requirements"]
    assert [(item["language"], item["requirement"]) for item in requirements] == [
        ("English", "conflicting"), ("German", "required"),
    ]
    assert "English B2" in requirements[0]["excerpt"]
    assert "English B1" in requirements[0]["excerpt"]
    assert "German is required" in requirements[1]["excerpt"]


def test_citizenship_and_residence_restrictions_keep_separate_observed_scope():
    citizenship = NormalizedJob(
        source="synthetic_fixture", source_job_id="citizens-only", title="Engineer",
        description="US citizens only.",
    )
    residence = NormalizedJob(
        source="synthetic_fixture", source_job_id="residents-only", title="Engineer",
        description="Candidates must currently reside in Germany.",
    )
    fields_a = build_relocation_evidence(citizenship)["fields"]
    fields_b = build_relocation_evidence(residence)["fields"]
    assert fields_a["citizenship_or_residence_restriction"]["interpretation"]["scope"] == "citizenship"
    assert fields_b["citizenship_or_residence_restriction"]["interpretation"]["scope"] == "residence"
    assert "Germany" in fields_b["citizenship_or_residence_restriction"]["excerpt"]


def test_existing_work_authorization_requirement_distinguishes_explicit_no_from_unknown():
    def extract(description):
        job = NormalizedJob(
            source="synthetic_fixture", source_job_id="auth-condition",
            title="Engineer", description=description,
        )
        return build_relocation_evidence(job)["fields"]["existing_work_authorization_required"]

    not_required = extract("No EU work permit required.")
    assert not_required["status"] == "confirmed"
    assert not_required["value"] is False
    assert "No EU work permit required" in not_required["excerpt"]

    absent = extract("Linux operations role.")
    assert absent["status"] == "unknown" and absent["value"] is None

    conflicting = extract(
        "Must already have the right to work in Germany, but right to work is not required."
    )
    assert conflicting["status"] == "unknown" and conflicting["value"] is None
    assert conflicting["confidence"] == "conflicting_text"


def test_start_timing_keeps_explicit_kind_and_original_excerpt():
    cases = [
        ("We need someone to start immediately.", "immediate"),
        ("Available to start within 2 weeks.", "relative_window"),
        ("Starting date: 2026-11-01.", "stated_date"),
        ("The notice period is 30 days.", "notice_period"),
        ("Start date is negotiable.", "negotiable"),
        ("Начать можно сразу.", "immediate"),
        ("Выход на работу по договорённости.", "negotiable"),
    ]
    for text, expected_kind in cases:
        job = NormalizedJob(
            source="synthetic_fixture", source_job_id=expected_kind,
            title="Engineer", description=text,
        )
        item = build_relocation_evidence(job)["fields"]["start_timing"]
        assert item["status"] == "observed"
        assert item["interpretation"]["kind"] == expected_kind
        assert text.rstrip(".") in item["excerpt"]


def test_conflicting_support_statements_remain_unknown_with_both_source_quotes():
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="support-conflict", title="Engineer",
        description="We provide visa sponsorship. Visa sponsorship is not available.",
    )
    item = build_relocation_evidence(job)["fields"]["visa_sponsorship"]
    assert item["status"] == "unknown" and item["value"] is None
    assert item["confidence"] == "conflicting_text"
    assert "provide visa sponsorship" in item["excerpt"]
    assert "not available" in item["excerpt"]


def test_support_for_one_component_does_not_inherit_another_components_refusal():
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="support-separate", title="Engineer",
        description="We do not provide relocation assistance and visa sponsorship is available.",
    )
    fields = build_relocation_evidence(job)["fields"]
    assert fields["relocation_assistance"]["value"] is False
    visa = fields["visa_sponsorship"]
    assert visa["value"] is None
    assert visa["status"] == "unknown"
    assert visa["confidence"] == "ambiguous_text"


def test_german_relocation_conditions_are_extracted_without_legal_conclusions():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/relocation_evidence/synthetic_de_job.json").read_text()
    )
    job = NormalizedJob(
        source="synthetic_fixture", source_job_id="synthetic-de-1",
        title=fixture["title"], country=fixture["country"],
        description=fixture["description"],
    )
    fields = build_relocation_evidence(job)["fields"]
    restriction = fields["citizenship_or_residence_restriction"]
    assert restriction["interpretation"]["scope"] == "residence"
    auth = fields["existing_work_authorization_required"]
    assert auth["status"] == "confirmed" and auth["value"] is True
    housing = fields["housing_provided"]
    assert housing["status"] == "confirmed" and housing["value"] is False
    language = fields["language_requirement"]
    assert language["interpretation"]["requirements"][0]["language"] == "German"
    assert language["interpretation"]["requirements"][0]["requirement"] == "preferred"
    assert fields["start_timing"]["interpretation"]["kind"] == "negotiable"
