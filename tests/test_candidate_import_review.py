import pytest

from app.candidates.importer import FactOverlap, FactProposal
from app.candidates.import_review import plan_fact_import
from app.telegram.resume_import_view import render_import_conflict, render_import_preview


def proposals_and_overlap():
    overlap_proposal = FactProposal("skills", "Linux and Docker", 0.92, "skills")
    new_proposal = FactProposal("skills", "PostgreSQL", 0.92, "skills")
    overlap = FactOverlap(overlap_proposal, 42, "Linux Docker in production")
    return (overlap_proposal, new_proposal), (overlap,)


def test_conflicts_default_to_keep_and_new_facts_to_add():
    proposals, overlaps = proposals_and_overlap()
    plan = plan_fact_import(proposals, overlaps)
    assert plan.additions == (proposals[1],)
    assert plan.replacements == ()
    assert plan.kept == 1


@pytest.mark.parametrize("action", ["add", "update", "keep"])
def test_explicit_overlap_choice_has_only_the_selected_effect(action):
    proposals, overlaps = proposals_and_overlap()
    plan = plan_fact_import(proposals, overlaps, {0: action})
    assert (proposals[0] in plan.additions) == (action == "add")
    assert (overlaps[0] in plan.replacements) == (action == "update")
    assert plan.kept == int(action == "keep")
    assert overlaps[0].existing_value == "Linux Docker in production"
    assert proposals[0].experience_type == "unknown"


@pytest.mark.parametrize("choices", [{99: "keep"}, {1: "update"}, {0: "delete"}])
def test_invalid_or_unsupported_choices_do_not_create_a_plan(choices):
    proposals, overlaps = proposals_and_overlap()
    with pytest.raises(ValueError):
        plan_fact_import(proposals, overlaps, choices)


def test_two_replacements_of_one_existing_fact_are_rejected():
    proposals, overlaps = proposals_and_overlap()
    overlaps += (FactOverlap(proposals[1], 42, overlaps[0].existing_value),)
    with pytest.raises(ValueError, match="только один UPDATE"):
        plan_fact_import(proposals, overlaps, {0: "update", 1: "update"})


def test_conflict_view_escapes_text_and_keeps_save_as_separate_confirmation():
    proposal = FactProposal("skills", "Linux <Docker>", 0.92, "skills")
    pending = {"content": "Skills", "language": "en", "proposals": (proposal,),
               "overlaps": (FactOverlap(proposal, 42, "Linux & Docker"),), "choices": {}}
    text, keyboard = render_import_conflict(pending, "token")
    assert "&lt;Docker&gt;" in text and "Linux &amp; Docker" in text
    assert "unknown" in text and "KEEP" in text
    callbacks = [button.callback_data for row in keyboard.inline_keyboard for button in row]
    assert "rchoice:token:0:update" in callbacks
    assert not any(data.startswith("rimp:facts:") for data in callbacks)
    preview, _ = render_import_preview(pending, "token")
    assert "ADD: 0 · UPDATE: 0 · KEEP: 1" in preview
