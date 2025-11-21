from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ru_mobile_outage_correlator.ai.summaries import TemplateSummaryGenerator
from ru_mobile_outage_correlator.config.model import (
    CorrelationConfig,
    CorrelationResult,
    ExternalOutageSignal,
    InternalIncidentSignal,
)
from ru_mobile_outage_correlator.correlator.engine import correlate
from ru_mobile_outage_correlator.sources_external.news_feed_parser import parse_news_items
from ru_mobile_outage_correlator.sources_external.status_pages import parse_status_feed
from ru_mobile_outage_correlator.sources_internal.metrics_ingest import load_from_file

app = typer.Typer(help="Корреляция внутренних инцидентов с внешними сбоями операторов")
console = Console()


@app.command("collect-external")
def collect_external(
    source: Path = typer.Argument(..., help="Path to JSON feed"),
    source_type: str = typer.Option("news", help="news or status_page"),
    operator: Optional[str] = typer.Option(None, help="Operator name for status pages"),
    output: Path = typer.Option(Path("external_signals.json"), help="Where to store normalized data"),
):
    items = json.loads(source.read_text(encoding="utf-8"))
    signals = (
        parse_news_items(items)
        if source_type == "news"
        else parse_status_feed(items, operator or "unknown")
    )
    output.write_text(json.dumps([s.model_dump() for s in signals], ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"Saved {len(signals)} external signals to {output}")


@app.command("collect-internal")
def collect_internal(
    path: Path = typer.Argument(..., help="Path to aggregated metrics JSON"),
    output: Path = typer.Option(Path("internal_incidents.json"), help="Where to write normalized data"),
):
    incidents = load_from_file(path)
    output.write_text(json.dumps([i.model_dump() for i in incidents], ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"Saved {len(incidents)} internal incidents to {output}")


@app.command("correlate")
def run_correlate(
    internal_path: Path = typer.Argument(...),
    external_path: Path = typer.Argument(...),
    time_window: int = typer.Option(5, help="Time window in minutes"),
    min_severity: str = typer.Option("minor"),
    output: Path = typer.Option(Path("correlation_report.json")),
):
    internal_data = json.loads(internal_path.read_text(encoding="utf-8"))
    external_data = json.loads(external_path.read_text(encoding="utf-8"))
    internals = [InternalIncidentSignal(**i) for i in internal_data]
    externals = [ExternalOutageSignal(**e) for e in external_data]
    config = CorrelationConfig(time_window_minutes=time_window, minimal_external_severity=min_severity)
    results = correlate(internals, externals, config)
    output.write_text(
        json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    console.print(f"Report saved to {output}")


@app.command("report")
def render_report(report_path: Path = typer.Argument(...), format: str = typer.Option("markdown")):
    raw = json.loads(report_path.read_text(encoding="utf-8"))
    results = [CorrelationResult(**item) for item in raw]
    generator = TemplateSummaryGenerator()
    if format == "json":
        console.print_json(raw)
        return
    table = Table(title="Корреляция инцидентов")
    table.add_column("Сервис")
    table.add_column("Классификация")
    table.add_column("Баллы")
    table.add_column("Краткое резюме")
    for result in results:
        summary = generator.for_status_page(result)
        table.add_row(
            result.incident.service_name,
            result.classification,
            str(result.score),
            summary,
        )
    console.print(table)


if __name__ == "__main__":
    app()
