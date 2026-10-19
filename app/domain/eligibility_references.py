"""Dated official starting points for country-specific work-permit checks."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OfficialEligibilityReference:
    authority: str
    label: str
    url: str
    checked_at: str


_CHECKED_AT = "2026-10-19"
_REFERENCES: dict[str, tuple[OfficialEligibilityReference, ...]] = {
    "AM": (
        OfficialEligibilityReference(
            "Armenia Migration and Citizenship Service",
            "Workpermit.am — foreign worker process",
            "https://workpermit.am/en/home",
            _CHECKED_AT,
        ),
    ),
    "DE": (
        OfficialEligibilityReference(
            "Federal Government of Germany",
            "Make it in Germany — work visa information",
            "https://www.make-it-in-germany.com/en/looking-for-foreign-professionals/entering/german-work-visa",
            _CHECKED_AT,
        ),
    ),
    "GE": (
        OfficialEligibilityReference(
            "Georgia Public Service Development Agency",
            "Migration and work residence permits",
            "https://sda.gov.ge/en/products/migration-residence-permits/",
            _CHECKED_AT,
        ),
        OfficialEligibilityReference(
            "Embassy of Georgia to the Kingdom of Norway",
            "Employment rules update (official embassy notice)",
            "https://norway.mfa.gov.ge/en/news/929284-new-rules-for-the-employed-self-employed-aliens-with-no-permit-for-permanent-residence-in-georgia-sh",
            _CHECKED_AT,
        ),
    ),
}


def official_eligibility_references(country: object) -> tuple[OfficialEligibilityReference, ...]:
    """Return allowlisted national authority links; never assess a candidate."""
    if not isinstance(country, str):
        return ()
    return _REFERENCES.get(country.strip().upper(), ())
