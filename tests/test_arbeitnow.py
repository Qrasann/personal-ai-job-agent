from app.sources.adapters.arbeitnow import ArbeitnowSource
from app.sources.base import SourceContext


def test_arbeitnow_maps_german_role_aliases_and_explicit_support():
    payload = {
        "data": [
            {
                "slug": "lager-1",
                "company_name": "Example GmbH",
                "title": "Lagermitarbeiter (m/w/d)",
                "description": "<p>Visa support and relocation assistance are provided.</p>",
                "url": "https://example.invalid/lager-1",
                "location": "Berlin",
                "remote": False,
                "tags": ["Logistik"],
                "created_at": 1791676800,
            },
            {
                "slug": "developer-1",
                "company_name": "Example GmbH",
                "title": "Senior Software Developer",
                "description": "Python",
                "url": "https://example.invalid/developer-1",
                "location": "Munich",
                "remote": True,
                "tags": ["Software"],
            },
        ]
    }
    context = SourceContext(user_id=1, queries=["warehouse worker"])

    jobs = ArbeitnowSource.parse_payload(payload, context)

    assert len(jobs) == 1
    assert jobs[0].title == "Lagermitarbeiter (m/w/d)"
    assert jobs[0].country == "DE"
    assert jobs[0].city == "Berlin"
    assert jobs[0].visa_sponsorship is True
    assert jobs[0].relocation is True
    assert jobs[0].description == "Visa support and relocation assistance are provided."
