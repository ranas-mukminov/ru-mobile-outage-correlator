"""Pluggable log ingestion helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import InternalIncidentSignal


def parse_log_records(records: Iterable[dict]) -> List[InternalIncidentSignal]:
    incidents: List[InternalIncidentSignal] = []
    for record in records:
        regions = record.get("regions") or []
        if not regions:
            continue
        incidents.append(
            InternalIncidentSignal(
                service_name=record["service_name"],
                endpoint_pattern=record.get("endpoint_pattern", "*"),
                error_type=record.get("error_type", "unknown"),
                regions=regions,
                operator_hint=record.get("operator_hint"),
                metrics=record.get("metrics", {}),
                start_at=datetime.fromisoformat(record["start_at"]),
                end_at=(datetime.fromisoformat(record["end_at"]) if record.get("end_at") else None),
            )
        )
    return incidents
