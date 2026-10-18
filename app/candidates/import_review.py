from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence

from app.candidates.importer import FactOverlap, FactProposal


@dataclass(frozen=True)
class FactImportPlan:
    additions: tuple[FactProposal, ...]
    replacements: tuple[FactOverlap, ...]
    kept: int


def plan_fact_import(
    proposals: Sequence[FactProposal],
    overlaps: Sequence[FactOverlap],
    choices: Mapping[int, str] | None = None,
) -> FactImportPlan:
    """Resolve explicit choices; overlapping facts default to KEEP."""
    choices = choices or {}
    if any(not isinstance(index, int) or not 0 <= index < len(proposals) for index in choices):
        raise ValueError("Некорректный номер предлагаемого факта.")
    overlap_map = {item.proposal: item for item in overlaps}
    additions, replacements = [], []
    updated_ids: set[int] = set()
    kept = 0
    for index, proposal in enumerate(proposals):
        overlap = overlap_map.get(proposal)
        action = choices.get(index, "keep" if overlap else "add")
        if action == "keep":
            kept += 1
        elif action == "add":
            additions.append(proposal)
        elif action == "update" and overlap:
            if overlap.existing_id in updated_ids:
                raise ValueError("Для одного существующего факта выбери только один UPDATE.")
            updated_ids.add(overlap.existing_id)
            replacements.append(overlap)
        else:
            raise ValueError("UPDATE доступен только для пересечения; выбери ADD или KEEP.")
    return FactImportPlan(tuple(additions), tuple(replacements), kept)
