"""Helpers for ingesting aggregated metrics from files or pushes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from ru_mobile_outage_correlator.config.model import InternalIncidentSignal
from ru_mobile_outage_correlator.sources_internal.logs_parser import parse_log_records


def load_from_file(path: Path) -> List[InternalIncidentSignal]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Metrics files must contain a list of incidents")
    return parse_log_records(data)
