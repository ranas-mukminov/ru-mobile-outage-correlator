# ru-mobile-outage-correlator 📡

[![CI](https://github.com/ranas-mukminov/ru-mobile-outage-correlator/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/ru-mobile-outage-correlator/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

🇬🇧 English | 🇷🇺 [Русская версия](README.ru.md)

**ru-mobile-outage-correlator** is an SRE-focused tool that correlates internal service incidents with public outage signals from major Russian telecom operators (MTS, MegaFon, Tele2, Beeline, Rostelecom, Yota). It helps DevOps and SRE teams quickly identify whether degraded service performance is caused by upstream telecom failures, reducing time to diagnosis and improving incident response.

Licensed under **Apache-2.0**, this project is production-ready for commercial use and consulting engagements.

## Key Features

- **Multi-source external signal collection**: Status pages, news feeds, custom probe results
- **Internal incident normalization**: Import from logs, metrics (Prometheus, Loki, ELK), or custom JSON
- **Intelligent time-aware correlation**: Configurable time windows and severity thresholds
- **Geo and operator matching**: Region-based and ASN/operator-aware correlation with confidence scoring
- **AI-powered Russian summaries**: Generate postmortem and status page texts (pluggable LLM interface)
- **CLI-first design**: Library + CLI for automation and scripting
- **Privacy and compliance aware**: No hard-coded secrets, respect for robots.txt and ToS
- **CI/CD ready**: Automated linting, testing, and security scanning with GitHub Actions

## Architecture / Components

```
┌──────────────────────────────────────────────────────────────────┐
│                     ru-mobile-outage-correlator                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │ External Sources │         │ Internal Sources │              │
│  │ • Status pages   │         │ • Prometheus     │              │
│  │ • News feeds     │         │ • Loki / ELK logs│              │
│  │ • Custom probes  │         │ • JSON exports   │              │
│  └────────┬─────────┘         └────────┬─────────┘              │
│           │                            │                         │
│           └────────────┬───────────────┘                         │
│                        │                                         │
│              ┌─────────▼─────────┐                               │
│              │ Correlation Engine │                              │
│              │ • Time windows     │                              │
│              │ • Region matching  │                              │
│              │ • Operator hints   │                              │
│              │ • Confidence score │                              │
│              └─────────┬─────────┘                               │
│                        │                                         │
│              ┌─────────▼─────────┐                               │
│              │  Report Generator  │                              │
│              │ • JSON / Markdown  │                              │
│              │ • AI summaries     │                              │
│              └────────────────────┘                              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Core modules:**
- `config/model.py`: Data models and schemas (Pydantic-based)
- `sources_external/`: Parsers for status pages, news, and probes
- `sources_internal/`: Metrics and log ingesters
- `correlator/engine.py`: Correlation algorithm with configurable rules
- `ai/summaries.py`: Pluggable summary generation (local templates or external LLM)
- `cli.py`: Command-line interface for all operations

## Requirements

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+, Rocky/Alma 8+)
- **Python**: 3.10 or later
- **RAM**: 512 MB minimum (small datasets); 2 GB+ recommended for production
- **Disk**: 100 MB for installation, additional space for logs and reports

### Access and Dependencies
- Internet access for external signal collection (respecting robots.txt and ToS)
- Optional: Access to Prometheus, Loki, or ELK for internal metric export
- Optional: OpenAI or compatible LLM API for AI-powered summaries (see [AI integration docs](docs/ai_integration.md))

### Python Dependencies
Automatically installed via `pip`:
- `pydantic>=2.6` (data validation)
- `typer>=0.12` (CLI framework)
- `pyyaml>=6.0` (configuration)
- `rich>=13.7` (terminal output)

## Quick Start (TL;DR)

```bash
# 1. Clone the repository
git clone https://github.com/ranas-mukminov/ru-mobile-outage-correlator.git
cd ru-mobile-outage-correlator

# 2. Install dependencies
pip install -e .

# 3. Run correlation with example data
ru-mobile-outage-correlator correlate \
  examples/demo_small_saas/internal_incidents.json \
  examples/demo_small_saas/external_signals.json \
  --output report.json

# 4. View the report
ru-mobile-outage-correlator report report.json
```

**Default output**: Markdown table with service name, classification, score, and summary.

## Detailed Installation

### Install on Ubuntu / Debian

```bash
# Update package list
sudo apt update

# Install Python 3.10+ and pip
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone https://github.com/ranas-mukminov/ru-mobile-outage-correlator.git
cd ru-mobile-outage-correlator

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Verify installation
ru-mobile-outage-correlator --help
```

### Install on RHEL / Rocky / Alma

```bash
# Install Python 3.10+ (RHEL 8+)
sudo dnf install python3.11 python3.11-pip git -y

# Clone repository
git clone https://github.com/ranas-mukminov/ru-mobile-outage-correlator.git
cd ru-mobile-outage-correlator

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Verify
ru-mobile-outage-correlator --help
```

### Install for Development

```bash
# Clone and navigate
git clone https://github.com/ranas-mukminov/ru-mobile-outage-correlator.git
cd ru-mobile-outage-correlator

# Install with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linter
ruff check src tests
```

## Configuration

The tool uses JSON-based configuration for correlation parameters. Example configuration:

```python
# Correlation configuration (in code or via CLI options)
{
  "time_window_minutes": 5,          # Time buffer before/after external signals
  "minimal_external_severity": "minor",  # Filter low-severity external signals
  "minimal_error_rate_increase": 0.05   # Threshold for internal incident severity
}
```

### External Signal Format

External signals should be in JSON format:

```json
[
  {
    "source_type": "news",
    "operator": "MegaFon",
    "regions": ["Самарская область", "Татарстан"],
    "severity": "major",
    "start_at": "2024-03-01T09:30:00",
    "end_at": "2024-03-01T10:15:00",
    "confidence": 0.8
  }
]
```

**Fields:**
- `source_type`: `news`, `status_page`, `probe`, or `custom`
- `operator`: Operator name (e.g., `MTS`, `MegaFon`, `Beeline`, `Tele2`, `Rostelecom`, `Yota`)
- `regions`: List of affected regions or cities
- `severity`: `info`, `minor`, `major`, `critical`
- `start_at`, `end_at`: ISO 8601 timestamps
- `confidence`: Float between 0.0-1.0

### Internal Incident Format

```json
[
  {
    "service_name": "payments",
    "endpoint_pattern": "/api/pay",
    "error_type": "5xx",
    "regions": ["Самарская область"],
    "operator_hint": "MegaFon",
    "metrics": {"error_rate": 0.35, "latency_p95": 2.1, "rps_change": -0.1},
    "start_at": "2024-03-01T09:34:00",
    "end_at": "2024-03-01T10:05:00"
  }
]
```

**Fields:**
- `service_name`: Internal service identifier
- `endpoint_pattern`: Affected API endpoint or component
- `error_type`: Error category (e.g., `5xx`, `timeout`, `connection`)
- `regions`: Affected regions (should match external signals for correlation)
- `operator_hint`: Optional operator hint for better matching
- `metrics`: Arbitrary metrics (error rate, latency, RPS changes)

## Usage & Common Tasks

### Collect External Signals

Normalize raw external data (news, status pages) into the standard format:

```bash
# From news feed
ru-mobile-outage-correlator collect-external \
  raw_news.json \
  --source-type news \
  --output external_signals.json

# From status page
ru-mobile-outage-correlator collect-external \
  raw_status.json \
  --source-type status_page \
  --operator "MegaFon" \
  --output external_signals.json
```

### Collect Internal Incidents

Export metrics from Prometheus/Loki and convert to internal incident format:

```bash
# Example: Export from JSON dump
ru-mobile-outage-correlator collect-internal \
  prometheus_export.json \
  --output internal_incidents.json
```

### Run Correlation

```bash
ru-mobile-outage-correlator correlate \
  internal_incidents.json \
  external_signals.json \
  --time-window 10 \
  --min-severity major \
  --output correlation_report.json
```

**Options:**
- `--time-window`: Time buffer in minutes (default: 5)
- `--min-severity`: Minimum external severity to consider (`info`, `minor`, `major`, `critical`)
- `--output`: Path to save JSON report

### View Report

```bash
# Markdown table (default)
ru-mobile-outage-correlator report correlation_report.json

# JSON output
ru-mobile-outage-correlator report correlation_report.json --format json
```

**Report fields:**
- **Service**: Internal service name
- **Classification**: `LIKELY_EXTERNAL_OUTAGE`, `LIKELY_INTERNAL_ISSUE`, `MIXED`, `UNKNOWN`
- **Score**: Correlation confidence (0.0-1.0)
- **Summary**: AI-generated or template-based description

## Update / Upgrade

```bash
# Navigate to repository
cd ru-mobile-outage-correlator

# Pull latest changes
git pull origin main

# Reinstall package
pip install -e .

# Run tests to verify
pytest
```

**Breaking changes**: Check [CHANGELOG.md](CHANGELOG.md) (if available) or commit messages for migration notes.

## Logs, Monitoring, Troubleshooting

### Logs

The CLI outputs to `stdout`/`stderr` by default. Redirect to files for persistent logs:

```bash
ru-mobile-outage-correlator correlate \
  internal.json external.json \
  --output report.json 2>&1 | tee correlation.log
```

### Common Issues & Fixes

**Issue: `ModuleNotFoundError: No module named 'ru_mobile_outage_correlator'`**

**Fix:**
```bash
pip install -e .
```

**Issue: Empty correlation results**

**Causes & fixes:**
- **Time mismatch**: Increase `--time-window` (e.g., `--time-window 15`)
- **Region mismatch**: Ensure `regions` in both internal and external signals match exactly
- **Severity threshold**: Lower `--min-severity` to `minor` or `info`
- **No overlapping timestamps**: Verify timestamps in input JSON are correct

**Issue: `ValueError: At least one region must be provided`**

**Fix:** Ensure all internal and external signals include at least one region in the `regions` list.

**Issue: Permission denied when running CLI**

**Fix:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall if needed
pip install -e .
```

### Performance Tips

- For large datasets (>10,000 incidents), consider pre-filtering by time range before correlation
- Use `--min-severity major` to reduce noise from low-severity external signals
- Batch processing: Split large datasets into time-based chunks for parallel processing

## Security Notes

> [!WARNING]
> This tool processes operational data and may contain sensitive information. Follow these best practices:

- **Change defaults**: No default passwords exist, but ensure API keys for external LLMs are stored securely (see [AI integration](docs/ai_integration.md))
- **Restrict access**: Run the tool in isolated environments or behind VPN if processing production data
- **Anonymize data**: Use synthetic or anonymized data for testing and examples (see `examples/` directory)
- **Respect ToS**: When collecting external signals, comply with robots.txt, rate limits, and terms of service
- **Do not expose sensitive ports**: This is a CLI tool with no network server; no ports are exposed
- **Audit logs**: If integrating with external LLMs, ensure data processing agreements (DPAs) are in place

**Legal compliance**: When processing Russian operator data, consider 152-FZ (personal data protection) if user identifiers are present. Anonymize or hash identifiers before correlation.

## Project Structure

```
.
├── src/ru_mobile_outage_correlator/  # Main package
│   ├── ai/                            # AI summary generation
│   ├── config/                        # Data models and schemas
│   ├── correlator/                    # Correlation engine
│   ├── sources_external/              # External signal parsers
│   ├── sources_internal/              # Internal incident loaders
│   └── cli.py                         # CLI entry point
├── tests/                             # Unit and integration tests
├── examples/                          # Synthetic demo data
├── docs/                              # Extended documentation
├── .github/workflows/                 # CI/CD pipelines
├── pyproject.toml                     # Project metadata
├── LICENSE                            # Apache-2.0 license
└── README.md                          # This file
```

## Contributing

We welcome contributions! To contribute:

1. **Open an issue** to discuss new features, bugs, or improvements
2. **Fork the repository** and create a feature branch
3. **Follow code style**:
   - Use `ruff` for linting: `ruff check src tests`
   - Use type hints (Python 3.10+ syntax)
   - Write unit tests for new functionality
4. **Submit a pull request** with a clear description of changes

**Code review**: All PRs require CI checks (linting, tests) to pass before merge.

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for full text.

You are free to use, modify, and distribute this software for commercial and non-commercial purposes, provided you include the original license and copyright notice.

## Author and Commercial Support

**Author**: [Ranas Mukminov](https://github.com/ranas-mukminov)

For production-grade setup, infrastructure audits, custom integrations, and team training, visit **https://run-as-daemon.ru** (Russian) or contact the author via GitHub profile.

**Commercial services include:**
- SRE/observability stack setup and optimization
- Custom correlation rule development for your infrastructure
- Integration with Prometheus, Grafana, Loki, and other monitoring tools
- Team training on incident management and root cause analysis
- Support and maintenance contracts
