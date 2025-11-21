from datetime import datetime

from ru_mobile_outage_correlator.config.model import (
    CorrelationConfig,
    ExternalOutageSignal,
    InternalIncidentSignal,
    Severity,
)
from ru_mobile_outage_correlator.correlator import engine


def make_external(**kwargs):
    defaults = dict(
        source_type="news",
        operator="MegaFon",
        regions=["Самарская область"],
        severity=Severity.MAJOR,
        start_at=datetime.fromisoformat("2024-03-01T09:30:00"),
        end_at=datetime.fromisoformat("2024-03-01T10:10:00"),
        confidence=0.9,
    )
    defaults.update(kwargs)
    return ExternalOutageSignal(**defaults)


def make_internal(**kwargs):
    defaults = dict(
        service_name="api",
        endpoint_pattern="/v1",
        error_type="5xx",
        regions=["Самарская область"],
        operator_hint="MegaFon",
        metrics={"error_rate": 0.3},
        start_at=datetime.fromisoformat("2024-03-01T09:40:00"),
        end_at=datetime.fromisoformat("2024-03-01T10:00:00"),
    )
    defaults.update(kwargs)
    return InternalIncidentSignal(**defaults)


def test_basic_correlation_external_outage():
    results = engine.correlate([make_internal()], [make_external()])
    assert results[0].classification == engine.LIKELY_EXTERNAL_OUTAGE


def test_internal_only_issue():
    internal = make_internal(metrics={"error_rate": 0.2})
    results = engine.correlate([internal], [])
    assert results[0].classification == engine.LIKELY_INTERNAL_ISSUE


def test_mixed_case():
    external = make_external(confidence=0.3)
    results = engine.correlate([make_internal()], [external])
    assert results[0].classification == engine.MIXED


def test_regional_megafon_regression():
    external = make_external(operator="MTS", regions=["Москва", "Татарстан"], start_at=datetime.fromisoformat("2024-03-01T09:00:00"))
    internal = make_internal(operator_hint="MTS", regions=["Татарстан"], start_at=datetime.fromisoformat("2024-03-01T09:05:00"))
    results = engine.correlate([internal], [external])
    assert results[0].classification == engine.LIKELY_EXTERNAL_OUTAGE


def test_macro_outage_multiple_services():
    external_common = make_external(operator="Tele2", regions=["Москва", "Тверь"], confidence=0.7)
    incidents = [
        make_internal(service_name="billing", regions=["Москва"], operator_hint=None),
        make_internal(service_name="auth", regions=["Тверь"], operator_hint=None),
    ]
    results = engine.correlate(incidents, [external_common])
    assert all(r.classification in {engine.LIKELY_EXTERNAL_OUTAGE, engine.MIXED} for r in results)
