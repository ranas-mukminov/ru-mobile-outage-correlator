"""Parse simplified news/outage JSON feeds."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import ExternalOutageSignal, Severity


def parse_news_items(items: Iterable[dict]) -> List[ExternalOutageSignal]:
    signals: List[ExternalOutageSignal] = []
    for item in items:
        operator = item.get("operator")
        regions = item.get("regions") or []
        if not operator or not regions:
            continue
        signals.append(
            ExternalOutageSignal(
                source_type="news",
                operator=operator,
                regions=regions,
                severity=Severity(item.get("severity", Severity.MINOR)),
                start_at=datetime.fromisoformat(item["start_at"]),
                end_at=(datetime.fromisoformat(item["end_at"]) if item.get("end_at") else None),
                confidence=float(item.get("confidence", 0.4)),
                asn=item.get("asn"),
            )
        )
    return signals
