"""Utilities to align signals on a common timeline."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ru_mobile_outage_correlator.config.model import ExternalOutageSignal, InternalIncidentSignal


def sort_external(signals: Iterable[ExternalOutageSignal]) -> List[ExternalOutageSignal]:
    return sorted(signals, key=lambda s: s.start_at)


def sort_internal(signals: Iterable[InternalIncidentSignal]) -> List[InternalIncidentSignal]:
    return sorted(signals, key=lambda s: s.start_at)


def window_overlap(a_start: datetime, a_end: datetime | None, b_start: datetime, b_end: datetime | None) -> float:
    a_end_real = a_end or b_end or a_start
    b_end_real = b_end or a_end or b_start
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end_real, b_end_real)
    if latest_start >= earliest_end:
        return 0.0
    a_duration = (a_end_real - a_start).total_seconds() or 1.0
    overlap = (earliest_end - latest_start).total_seconds()
    return max(0.0, min(1.0, overlap / a_duration))
