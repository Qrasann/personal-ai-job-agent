from __future__ import annotations

from dataclasses import dataclass

from app.domain.jobs import SourceCapabilities
from app.geo.countries import load_country_catalog, local_sources


@dataclass(frozen=True)
class SourcePlan:
    source_id: str
    name: str
    scope: str
    transport: str = "unknown"
    capability: str = "discovery"
    implemented: bool = False


IMPLEMENTED = {"hh", "remoteok", "telegram", "jobs_ge", "hr_ge"}


def build_source_plan(current_country: str | None, target_countries: list[str], *, include_international: bool = True) -> list[SourcePlan]:
    plans: dict[str, SourcePlan] = {}
    codes = [x for x in [current_country, *target_countries] if x]
    for code in dict.fromkeys(codes):
        for src in local_sources(code):
            if not src.get("enabled_by_default", True):
                continue
            plans[src["id"]] = SourcePlan(
                source_id=src["id"], name=src.get("name", src["id"]), scope=f"country:{code}",
                transport=src.get("transport", "unknown"), capability=src.get("capability", "discovery"),
                implemented=src["id"] in IMPLEMENTED,
            )
    if include_international:
        for src in load_country_catalog().get("international_sources", []):
            plans[src["id"]] = SourcePlan(
                source_id=src["id"], name=src.get("name", src["id"]), scope=src.get("scope", "global"),
                transport=src.get("transport", "unknown"), capability=src.get("capability", "discovery"),
                implemented=src["id"] in IMPLEMENTED,
            )
    return list(plans.values())


def source_capabilities(source_id: str) -> SourceCapabilities:
    if source_id == "hh":
        return SourceCapabilities(True, True, True, True)
    if source_id in {"remoteok", "telegram"}:
        return SourceCapabilities(True, True, False, False)
    return SourceCapabilities(True, False, False, False)
