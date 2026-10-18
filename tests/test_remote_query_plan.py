from pathlib import Path

import pytest
import yaml

from app.sources.query_plan import remote_discovery_queries


def test_default_relocation_remote_plan_includes_selected_customer_support():
    profile = yaml.safe_load((Path(__file__).parents[1] / "data/profile.yaml").read_text())
    selected = profile["search"]["relocation_queries"]
    original = selected.copy()

    planned = remote_discovery_queries(selected)

    assert planned == ["customer support", "warehouse worker", "production worker", "hotel staff"]
    assert selected == original
    assert set(planned).issubset(selected)


def test_default_career_query_order_remains_unchanged():
    profile = yaml.safe_load((Path(__file__).parents[1] / "data/profile.yaml").read_text())
    selected = profile["search"]["queries"]

    assert remote_discovery_queries(selected) == selected


def test_planner_preserves_text_and_order_within_both_groups_without_adding_roles():
    selected = ["warehouse worker", " Technical Support Engineer ", "cleaner",
                "Help Desk", "data-entry", "DevOps Engineer", "customer support"]

    assert remote_discovery_queries(selected) == [
        "Technical Support Engineer", "Help Desk", "data-entry", "DevOps Engineer",
    ]
    assert remote_discovery_queries(["warehouse worker", "cleaner"]) == ["warehouse worker", "cleaner"]


@pytest.mark.parametrize("role", [
    "customer support", "customer service representative", "technical support engineer",
    "helpdesk", "Help Desk Agent", "Service Desk Analyst", "data entry clerk",
    "Linux Administrator", "DevOps Engineer", "Infrastructure Engineer", "Site Reliability Engineer",
    "Техническая поддержка", "специалист поддержки", "системный администратор", "ввод данных",
])
def test_conservative_remote_role_phrases_get_a_request_slot_before_physical_work(role):
    assert remote_discovery_queries(["cleaner", role], limit=1) == [role]


@pytest.mark.parametrize("role", [
    "customer relationship warehouse", "customer success warehouse worker",
    "warehouse technical support", "support engineering at a factory",
    "engineer", "operator", "administrator", "production worker", "hotel staff",
    "kitchen assistant", "cleaner", "construction worker", "warehouse worker",
    "customer supporter", "unsupported engineer", "DevOpsy warehouse",
])
def test_generic_partial_or_physical_terms_do_not_claim_remote_compatibility(role):
    assert remote_discovery_queries(["Unclassified role", role], limit=1) == ["Unclassified role"]


def test_equivalent_queries_and_blanks_do_not_consume_request_budget():
    selected = [" ", " Help-Desk ", "help desk", "HELPDESK", "data entry", "Data-Entry",
                "Linux Administrator", "linux   administrator", "customer support"]

    assert remote_discovery_queries(selected) == [
        "Help-Desk", "data entry", "Linux Administrator", "customer support",
    ]


@pytest.mark.parametrize(("limit", "expected"), [(0, 0), (-1, 0), (1, 1), (3, 3), (4, 4), (20, 4)])
def test_remote_plan_obeys_requested_limit_and_absolute_four_query_bound(limit, expected):
    selected = ["helpdesk", "data entry", "customer support", "DevOps", "SRE", "cleaner"]
    assert len(remote_discovery_queries(selected, limit=limit)) == expected


@pytest.mark.parametrize("selected", [None, [], [None, 7, {}, ""]])
def test_empty_or_invalid_selected_queries_do_not_add_a_default_role(selected):
    assert remote_discovery_queries(selected) == []
