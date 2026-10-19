from __future__ import annotations

import re

from app.geo.countries import normalize_country


_REMOTE_OR_REGION = re.compile(
    r"\b(?:remote|hybrid|worldwide|global|anywhere|emea|apac|latam|europe|asia|americas)\b",
    re.I,
)
_US_GEORGIA_CITIES = {"atlanta", "savannah", "augusta", "macon", "columbus", "athens", "roswell"}
_US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
    "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}


def parse_city_country(value: object) -> tuple[str | None, str | None]:
    """Parse only a simple city + exact supported country label.

    This is for office/location fields, not remote eligibility. Regional,
    multi-country, remote and ambiguous US Georgia strings stay unresolved.
    """
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        return None, None
    text = " ".join(value.split())
    if _REMOTE_OR_REGION.search(text) or any(mark in text for mark in ("/", "|", ";")):
        return None, None
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 2 or not all(parts):
        return None, None
    city, country_label = parts
    # Two-letter suffixes overlap US state abbreviations (e.g. CA, DE, IN).
    # Do not silently turn an ambiguous city/state into a country.
    if country_label.upper() in _US_STATE_CODES:
        return None, None
    country = normalize_country(country_label)
    if not country or len(city) > 96:
        return None, None
    if country == "GE" and city.casefold() in _US_GEORGIA_CITIES:
        return None, None
    if not re.fullmatch(r"[\w .'-]+", city, re.UNICODE):
        return None, None
    return city, country
