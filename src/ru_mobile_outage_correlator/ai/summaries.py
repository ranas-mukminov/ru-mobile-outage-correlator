"""Local AI-like summaries using templates."""
from __future__ import annotations

from typing import Protocol

from ru_mobile_outage_correlator.config.model import CorrelationResult


class SummaryGenerator(Protocol):
    def for_postmortem(self, result: CorrelationResult) -> str: ...

    def for_status_page(self, result: CorrelationResult) -> str: ...


class TemplateSummaryGenerator:
    def for_postmortem(self, result: CorrelationResult) -> str:
        regions = ", ".join(result.incident.regions)
        operator = result.incident.operator_hint or "несколько операторов"
        return (
            f"{result.incident.start_at:%H:%M}–{result.incident.end_at or '...'} — "
            f"классфикация: {result.classification}, оператор: {operator}, регионы: {regions}, "
            f"ошибки: {result.incident.metrics.get('error_rate', 'нет данных')}"
        )

    def for_status_page(self, result: CorrelationResult) -> str:
        regions = ", ".join(result.incident.regions)
        operator = result.incident.operator_hint or "операторы"
        return (
            f"Замечены проблемы для {regions}; возможная связь с {operator}. "
            f"Вероятность внешнего сбоя: {result.score:.2f}."
        )
