"""Core correlation logic."""
from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import (
    CorrelationConfig,
    CorrelationResult,
    ExternalOutageSignal,
    InternalIncidentSignal,
    Severity,
)
from ru_mobile_outage_correlator.correlator.geo_operator_mapper import (
    operator_match_score,
    region_match_score,
)
from ru_mobile_outage_correlator.correlator.timeline_builder import window_overlap

LIKELY_EXTERNAL_OUTAGE = "LIKELY_EXTERNAL_OUTAGE"
LIKELY_INTERNAL_ISSUE = "LIKELY_INTERNAL_ISSUE"
MIXED = "MIXED"
UNKNOWN = "UNKNOWN"

_SEVERITY_ORDER = [Severity.INFO, Severity.MINOR, Severity.MAJOR, Severity.CRITICAL]


def correlate(
    internals: Iterable[InternalIncidentSignal],
    externals: Iterable[ExternalOutageSignal],
    config: CorrelationConfig | None = None,
) -> List[CorrelationResult]:
    cfg = config or CorrelationConfig()
    results: List[CorrelationResult] = []
    for incident in internals:
        matches: List[ExternalOutageSignal] = []
        reasons: List[str] = []
        best_score = 0.0
        for external in externals:
            if _SEVERITY_ORDER.index(external.severity) < _SEVERITY_ORDER.index(cfg.minimal_external_severity):
                continue
            overlap = window_overlap(
                incident.start_at,
                incident.end_at,
                external.start_at - timedelta(minutes=cfg.time_window_minutes),
                (external.end_at + timedelta(minutes=cfg.time_window_minutes)) if external.end_at else None,
            )
            if overlap == 0.0:
                continue
            region_score = region_match_score(incident.regions, external.regions)
            operator_score = operator_match_score(incident.operator_hint, external.operator)
            total = (overlap * 0.4) + (region_score * 0.4) + (operator_score * 0.2)
            total *= external.confidence
            if total > 0.0:
                matches.append(external)
                reasons.append(
                    f"overlap={overlap:.2f} region={region_score:.2f} operator={operator_score:.2f}"
                )
                best_score = max(best_score, total)
        classification = _classify(incident, matches, best_score)
        results.append(
            CorrelationResult(
                incident=incident,
                classification=classification,
                score=round(best_score, 3),
                matched_external=matches,
                reasons=reasons or ["no_external_match"],
            )
        )
    return results


def _classify(
    incident: InternalIncidentSignal, matches: List[ExternalOutageSignal], score: float
) -> str:
    local_magnitude = float(incident.metrics.get("error_rate", 0.0))
    if matches and score >= 0.35:
        return LIKELY_EXTERNAL_OUTAGE
    if matches and score >= 0.1:
        return MIXED
    if not matches and local_magnitude >= 0.1:
        return LIKELY_INTERNAL_ISSUE
    return UNKNOWN
