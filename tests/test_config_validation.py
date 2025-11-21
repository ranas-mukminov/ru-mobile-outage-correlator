from datetime import datetime

import pytest

from ru_mobile_outage_correlator.config.model import CorrelationConfig, ExternalOutageSignal, InternalIncidentSignal, Severity


def test_external_requires_region():
    with pytest.raises(ValueError):
        ExternalOutageSignal(
            source_type="news",
            operator="MTS",
            regions=[],
            severity=Severity.MAJOR,
            start_at=datetime.utcnow(),
            end_at=None,
            confidence=0.5,
        )


def test_internal_requires_region():
    with pytest.raises(ValueError):
        InternalIncidentSignal(
            service_name="api",
            endpoint_pattern="/",
            error_type="5xx",
            regions=[],
            metrics={},
            start_at=datetime.utcnow(),
            end_at=None,
        )


def test_correlation_config_window_guard():
    with pytest.raises(ValueError):
        CorrelationConfig(time_window_minutes=240)
