from types import SimpleNamespace

import pytest

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.domain.remote_evidence import remote_location_restriction, remote_residence_requirement
from app.sources.adapters.himalayas import HimalayasSource
from app.sources.base import SourceContext
from app.telegram.vacancy_view import render_job_details


@pytest.mark.parametrize("label", ["Germany only", "Canada only", "US-only", "EU only", "Georgia only"])
def test_explicit_location_labels_are_preserved_without_mapping_to_work_country(label):
    assert remote_location_restriction(label) == label


@pytest.mark.parametrize("label", [
    None, {}, "Worldwide", "Germany", "Berlin, Germany", "Germany only preferred",
    "Not Germany only", "Germany only?", "Our office in Germany only", "remote only",
    "Worldwide only", "Office only", "Germany only. Work from anywhere.", "x" * 513,
])
def test_office_global_negated_and_unrecognized_labels_are_not_limits(label):
    assert remote_location_restriction(label) is None


@pytest.mark.parametrize("text", [
    "Must be based in Europe or Asia or LatAM.",
    "Candidates must reside in Canada. Work from anywhere.",
    "<p>You need to live in Georgia.</p>",
    "What you bring\n• Must be located in Armenia.",
])
def test_direct_residence_requirements_are_preserved_as_evidence(text):
    evidence = remote_residence_requirement(text)
    assert evidence
    assert " in " in evidence
    signals = analyze_job_signals(Job(title="Support", description=text, work_mode="remote", remote_scope="worldwide"))
    assert signals.remote_eligibility == "uncertain"
    assert "worldwide" not in signals.remote_reason


@pytest.mark.parametrize("text", [
    "You are not required to reside in Georgia.",
    "Candidates must not reside in Canada.",
    "Our company is based in Georgia.",
    "We support customers who must be based in Canada.",
    "Must be based in Georgia?",
    "Must be based in Georgia is not mandatory.",
    "Must live in any country.",
    "Work from anywhere.",
])
def test_narrative_negated_or_global_locations_are_not_candidate_requirements(text):
    assert remote_residence_requirement(text) is None


def test_structured_country_scope_outranks_global_boilerplate_without_new_gate():
    job = Job(title="Support", description="Work from anywhere.", work_mode="remote", country="GE", remote_scope="Georgia")
    result = analyze_job_signals(job)
    assert result.remote_eligibility == "uncertain"
    assert "remote_international" in result.tracks
    job.remote_scope = "worldwide"
    assert analyze_job_signals(job).remote_eligibility == "yes"


def test_himalayas_empty_provider_scope_cannot_erase_explicit_residence_and_cached_card_rechecks():
    description = "Must be based in Europe or Asia or LatAM. Work from anywhere."
    item = HimalayasSource.parse_payload({"jobs": [{
        "guid": "support", "title": "Customer Support", "companyName": "Example",
        "locationRestrictions": [], "description": description,
        "applicationLink": "https://himalayas.app/companies/example/jobs/support",
    }]}, SourceContext(user_id=1, target_countries=["GE", "AM"], queries=["customer support"]))[0]
    assert item.remote_scope == "Must be based in Europe or Asia or LatAM"
    assert item.country is None
    assert item.visa_sponsorship is None
    job = Job(id=1, title=item.title, company=item.company, description=description,
              work_mode="remote", remote_scope="worldwide")  # Stored before this fix.
    match = SimpleNamespace(total_score=72, technical_score=94, geography_score=100,
                            salary_score=58, relocation_score=50, reason="")
    card = render_job_details({"job": job, "match": match, "source": "himalayas"})
    assert "в описании: Must be based in Europe or Asia or LatAM" in card
    assert "по всему миру указано источником" not in card
    assert "найм в вашей стране нужно подтвердить" in card


def test_existing_explicit_us_only_restriction_still_uses_existing_denial():
    result = analyze_job_signals(Job(title="Support", description="US-only remote.", work_mode="remote", remote_scope="worldwide"))
    assert result.remote_eligibility == "no"
