from types import SimpleNamespace

import pytest

from app.domain.job_text import clean_html_text
from app.matching.fact_comparison import compare_facts, extract_requirement_importance
from app.matching.technical_score import score_technical_v2


# The headings are from the public Devexperts posting checked on 2026-10-13:
# https://api.smartrecruiters.com/v1/companies/Devexperts/postings/744000138376969
# The body below paraphrases its relevant qualifications. CI/CD and Jenkins
# appear only in the separate synthetic optional-section regression.
# The posting presents Python as one language alternative. It is evidence of
# a mention, not a separate mandatory Python requirement.
QUALIFICATIONS_HTML = """
<p><strong>What we expect from candidates:</strong>&#xa0;<br>&#xa0;</p>
<ul>
<li>Comfort operating Linux consoles with Bash.</li>
<li>Basic programming knowledge, with Python among the language alternatives.</li>
<li>Understanding IP/TCP networking and infrastructure.</li>
<li>Client-facing communication and resilience during changing priorities.</li>
</ul>
<p><strong>As a Plus:</strong><br>&#xa0;</p>
<ul>
<li>Prior production operations and improvements to team workflows.</li>
</ul>
"""


def test_devexperts_html_headings_classify_only_explicit_technical_requirements():
    importance = extract_requirement_importance(clean_html_text(QUALIFICATIONS_HTML))

    assert importance == {
        "Linux": "required",
        "Bash": "required",
        "Python": "unknown",
        "Networking": "required",
    }
    # No inference of a particular cloud, education/language level, or a
    # Candidate Fact from the general infrastructure and communication wording.
    comparison = compare_facts(clean_html_text(QUALIFICATIONS_HTML), [])
    assert comparison.total_for_importance("required") == 3
    assert comparison.present_for_importance("required") == 0
    assert all(item.status == "missing" and item.fact_ids == () for item in comparison.requirements)


def test_alternative_example_does_not_penalize_missing_python():
    text = clean_html_text(QUALIFICATIONS_HTML)
    facts = [SimpleNamespace(
        id=1,
        value="Commercial Linux and Bash administration with networking.",
        experience_type="commercial",
        active=True,
        deleted_at=None,
    )]

    assert score_technical_v2(text, facts) == 100
    assert extract_requirement_importance(
        "Requirements:\nPython is mandatory.\n"
        "Basic programming knowledge, with Python among the language alternatives."
    )["Python"] == "required"


@pytest.mark.parametrize("heading", [
    "What we expect from candidates", "WHAT WE EXPECT FROM CANDIDATES:",
    "What we expect from candidates: Linux",
])
def test_devexperts_required_heading_supports_standalone_and_inline_text(heading):
    assert extract_requirement_importance(f"{heading}\nLinux")["Linux"] == "required"


@pytest.mark.parametrize("heading", ["As a Plus", "AS A PLUS:", "As a Plus: CI/CD with Jenkins"])
def test_devexperts_preferred_heading_supports_standalone_and_inline_text(heading):
    assert extract_requirement_importance(f"{heading}\nCI/CD with Jenkins")["CI/CD"] == "preferred"


@pytest.mark.parametrize("heading", [
    "What we expect from candidates worldwide",
    "Our note: What we expect from candidates",
    "What we expect from candidateship",
    "As a Plus engineer",
    "In practice, As a Plus",
    "As a Plus size project",
])
def test_devexperts_near_matches_do_not_create_requirement_sections(heading):
    assert extract_requirement_importance(f"{heading}\nLinux\nCI/CD") == {
        "Linux": "unknown", "CI/CD": "unknown",
    }


def test_devexperts_optional_ci_does_not_enter_required_coverage():
    # Synthetic optional technologies exercise the boundary independently of
    # the actual posting; they are not claimed as live Devexperts requirements.
    text = clean_html_text(QUALIFICATIONS_HTML) + "\nCI/CD with Jenkins\n"
    facts = [SimpleNamespace(
        id=1,
        value="Linux administration, Bash and Python automation, and networking.",
        experience_type="commercial",
        active=True,
        deleted_at=None,
    )]

    comparison = compare_facts(text, facts)

    assert {item.skill for item in comparison.items_for_importance("required")} == {
        "Linux", "Bash", "Networking",
    }
    assert comparison.present_for_importance("required") == 3
    assert [(item.skill, item.status) for item in comparison.items_for_importance("preferred")] == [
        ("CI/CD", "missing"),
    ]
    # The existing 85/15 weighting stays intact: full required coverage with
    # no optional CI evidence is 85, rather than lowering required coverage.
    assert score_technical_v2(text, facts) == 85


def test_devexperts_required_mention_wins_over_the_optional_section():
    importance = extract_requirement_importance(
        "What we expect from candidates:\nLinux\nAs a Plus:\nLinux and CI/CD"
    )
    assert importance == {"Linux": "required", "CI/CD": "preferred"}
