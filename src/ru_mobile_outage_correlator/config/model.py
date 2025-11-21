from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ExternalOutageSignal(BaseModel):
    source_type: str = Field(..., description="Origin of the signal: status_page/news/probe/custom")
    operator: str = Field(..., description="Operator name, e.g. MTS, MegaFon")
    regions: List[str] = Field(default_factory=list, description="Regions or cities affected")
    asn: Optional[int] = Field(None, description="ASN if provided")
    severity: Severity = Field(..., description="Severity level")
    start_at: datetime = Field(..., description="Start timestamp")
    end_at: Optional[datetime] = Field(None, description="Optional end timestamp")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")

    @field_validator("regions")
    @classmethod
    def ensure_regions(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("At least one region must be provided for external signals")
        return value


class InternalIncidentSignal(BaseModel):
    service_name: str = Field(...)
    endpoint_pattern: str = Field(...)
    error_type: str = Field(...)
    regions: List[str] = Field(default_factory=list)
    operator_hint: Optional[str] = None
    metrics: dict = Field(default_factory=dict)
    start_at: datetime = Field(...)
    end_at: Optional[datetime] = None

    @field_validator("regions")
    @classmethod
    def ensure_regions(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("At least one region must be provided for internal incidents")
        return value


class CorrelationConfig(BaseModel):
    time_window_minutes: int = Field(5, ge=0)
    minimal_external_severity: Severity = Severity.MINOR
    minimal_error_rate_increase: float = Field(0.05, ge=0.0)

    @field_validator("time_window_minutes")
    @classmethod
    def validate_window(cls, value: int) -> int:
        if value > 120:
            raise ValueError("Time window should be within two hours for meaningful correlation")
        return value


class CorrelationResult(BaseModel):
    incident: InternalIncidentSignal
    classification: str
    score: float
    matched_external: List[ExternalOutageSignal]
    reasons: List[str]
