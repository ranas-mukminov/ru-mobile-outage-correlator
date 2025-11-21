"""Active probe stubs for latency/availability checks."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import ExternalOutageSignal, Severity


def aggregate_probe_results(results: Iterable[dict]) -> List[ExternalOutageSignal]:
    signals: List[ExternalOutageSignal] = []
    for item in results:
        regions = item.get("regions") or []
        if not regions:
            continue
        severity = Severity.CRITICAL if item.get("loss", 0) > 0.5 else Severity.MAJOR
        signals.append(
            ExternalOutageSignal(
                source_type="probe",
                operator=item.get("operator", "unknown"),
                regions=regions,
                severity=severity,
                start_at=datetime.fromisoformat(item["start_at"]),
                end_at=(datetime.fromisoformat(item["end_at"]) if item.get("end_at") else None),
                confidence=float(item.get("confidence", 0.5)),
                asn=item.get("asn"),
            )
        )
    return signals
