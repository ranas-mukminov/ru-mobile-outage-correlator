"""Polling helpers for public status pages within allowed terms."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import ExternalOutageSignal, Severity


def parse_status_feed(entries: Iterable[dict], operator: str) -> List[ExternalOutageSignal]:
    signals: List[ExternalOutageSignal] = []
    for item in entries:
        regions = item.get("regions") or []
        if not regions:
            continue
        signals.append(
            ExternalOutageSignal(
                source_type="status_page",
                operator=operator,
                regions=regions,
                asn=item.get("asn"),
                severity=Severity(item.get("severity", Severity.MINOR)),
                start_at=datetime.fromisoformat(item["start_at"]),
                end_at=(datetime.fromisoformat(item["end_at"]) if item.get("end_at") else None),
                confidence=float(item.get("confidence", 0.5)),
            )
        )
    return signals
