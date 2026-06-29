# LATAM Exchange Rate Pipeline

🚧 **Work in progress.**

A learning project for mastering Apache Airflow, built around a real use case: fetching daily USD exchange rates from LATAM central banks and loading them into a unified data warehouse table.

## What it does

- Extracts daily USD rates from each central bank's own API/web service
- Normalizes each bank's different response shape into one unified schema (`source`, `country`, `currency`, `rate_date`, `rate_buy`, `rate_sell`)
- Validates the data before it's used downstream
- Orchestrates the whole flow as an Airflow DAG, running in Docker

## Status

- **BCU (Uruguay)**: ready — real extractor implemented (`src/extractors/bcu.py`), calling BCU's live SOAP web service (`awsbcucotizaciones`).
- **BCP (Paraguay)**: in process — still mocked (`src/extractors/mock.py`); BCP's site has no API, only an HTML form scrape, not yet built.
- **Other LATAM central banks**: in process — planned next, same pattern as BCP/BCU.
- **Postgres load step**: in process — not implemented yet; the pipeline currently stops at extract → transform → validate → report.

## Running it

```
docker-compose up -d postgres redis
docker-compose up airflow-init
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker
```

Then open `http://localhost:8080` (admin/admin) and trigger `exchange_rate_pipeline` or `mock_exchange_rate_pipeline`.
