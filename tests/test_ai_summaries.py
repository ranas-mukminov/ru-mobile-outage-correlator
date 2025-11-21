from datetime import datetime

from ru_mobile_outage_correlator.ai.summaries import TemplateSummaryGenerator
from ru_mobile_outage_correlator.config.model import CorrelationResult, ExternalOutageSignal, InternalIncidentSignal, Severity


def test_template_summary_contains_classification():
    generator = TemplateSummaryGenerator()
    result = CorrelationResult(
        incident=InternalIncidentSignal(
            service_name="api",
            endpoint_pattern="/v1",
            error_type="5xx",
            regions=["Москва"],
            operator_hint="MTS",
            metrics={"error_rate": 0.2},
            start_at=datetime.fromisoformat("2024-03-01T09:00:00"),
            end_at=datetime.fromisoformat("2024-03-01T09:30:00"),
        ),
        classification="LIKELY_EXTERNAL_OUTAGE",
        score=0.8,
        matched_external=[
            ExternalOutageSignal(
                source_type="news",
                operator="MTS",
                regions=["Москва"],
                severity=Severity.MAJOR,
                start_at=datetime.fromisoformat("2024-03-01T08:50:00"),
                end_at=datetime.fromisoformat("2024-03-01T09:40:00"),
                confidence=0.8,
            )
        ],
        reasons=["overlap=0.5"],
    )
    text = generator.for_postmortem(result)
    assert "LIKELY_EXTERNAL_OUTAGE" in text
    assert "Москва" in text
