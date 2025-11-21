"""Simple helpers to match regions and operators."""
from __future__ import annotations

from typing import Iterable, Set

from ru_mobile_outage_correlator.config.model import ExternalOutageSignal, InternalIncidentSignal


def region_match_score(incident_regions: Iterable[str], external_regions: Iterable[str]) -> float:
    incident_set: Set[str] = {r.lower() for r in incident_regions}
    external_set: Set[str] = {r.lower() for r in external_regions}
    if not incident_set or not external_set:
        return 0.0
    intersection = incident_set & external_set
    return len(intersection) / len(incident_set)


def operator_match_score(operator_hint: str | None, external_operator: str) -> float:
    if not operator_hint:
        return 0.3
    return 1.0 if operator_hint.lower() == external_operator.lower() else 0.0
