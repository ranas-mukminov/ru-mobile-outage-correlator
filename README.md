# ru-mobile-outage-correlator

Helper to correlate internal incidents with Russian telecom/mobile outages. Focused on legal, low-impact observability for operators like MTS, MegaFon, Tele2, Beeline, Rostelecom, and Yota.

- Primary documentation: [README.ru.md](README.ru.md)
- Services and consulting: **https://run-as-daemon.ru**

## Features
- Normalizes external outage signals (status pages, news, probes) and internal incidents.
- Correlates by time, region, operator/ASN, and incident magnitude.
- Generates Russian summaries for postmortems and status pages (pluggable AI interface).

## Architecture
Library + CLI (`ru-mobile-outage-correlator`) with modules for data models, collectors, correlation engine, and reporting.

## Legal & Safety
- Respect robots.txt and ToS; no aggressive probing.
- Synthetic examples only; anonymize production data before use.
- Licensed under Apache-2.0.
