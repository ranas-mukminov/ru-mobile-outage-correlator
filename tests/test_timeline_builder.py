from datetime import datetime

from ru_mobile_outage_correlator.correlator.timeline_builder import window_overlap


def test_overlap_fraction():
    start_a = datetime.fromisoformat("2024-03-01T09:00:00")
    end_a = datetime.fromisoformat("2024-03-01T10:00:00")
    start_b = datetime.fromisoformat("2024-03-01T09:30:00")
    end_b = datetime.fromisoformat("2024-03-01T09:45:00")
    assert window_overlap(start_a, end_a, start_b, end_b) == 0.25


def test_no_overlap():
    start_a = datetime.fromisoformat("2024-03-01T09:00:00")
    end_a = datetime.fromisoformat("2024-03-01T10:00:00")
    start_b = datetime.fromisoformat("2024-03-01T11:00:00")
    end_b = datetime.fromisoformat("2024-03-01T12:00:00")
    assert window_overlap(start_a, end_a, start_b, end_b) == 0.0
