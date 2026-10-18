import pytest

from app.domain.support_evidence import support_evidence
from app.sources.adapters.telegram_ingest import parse_telegram_job


@pytest.mark.parametrize("text,expected", [
    ("We sponsor visas.", True),
    ("Our company can sponsor your work visa.", True),
    ("We cannot sponsor visas.", False),
    ("We can't sponsor a work visa.", False),
    ("The employer does visa guidance.", None),
    ("We sponsor visa guidance.", None),
    ("We may sponsor visas.", None),
    ("We can sponsor visas if approved.", None),
    ("Applicants can sponsor visas.", None),
])
def test_direct_employer_visa_predicate_is_explicit_and_separate(text, expected):
    evidence = support_evidence(text)
    assert evidence["visa_sponsorship"] is expected
    assert evidence["relocation"] is None
    assert evidence["work_permit"] is None


@pytest.mark.parametrize("text", [
    "We offer visa sponsorship. We cannot sponsor visas.",
    "We cannot sponsor visas. We offer visa sponsorship.",
])
def test_explicit_verb_refusal_outranks_offer_in_both_orders_and_telegram(text):
    assert support_evidence(text)["visa_sponsorship"] is False
    assert parse_telegram_job(text, source_ref="fixture").visa_sponsorship is False
