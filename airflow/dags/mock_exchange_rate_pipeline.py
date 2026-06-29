"""Phase 1 learning DAG: extract -> transform -> validate -> report, using
mocked BCP/BCU responses (no network calls, no DB writes yet). The point is
to see DAGs, task dependencies, and XCom working end-to-end in the Airflow
UI before swapping in real extractors and a Postgres load in Phase 2.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.extractors.mock import fetch_bcp_rate, fetch_bcu_rate
from src.transforms.normalize import normalize_bcp, normalize_bcu
from src.validation.checks import validate_records

logger = logging.getLogger(__name__)

default_args = {
    "owner": "data-eng",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def extract_bcp(**context):
    rate_date = datetime.strptime(context["ds"], "%Y-%m-%d").date()
    raw = fetch_bcp_rate(rate_date)
    logger.info("BCP raw response: %s", raw)
    return raw


def extract_bcu(**context):
    rate_date = datetime.strptime(context["ds"], "%Y-%m-%d").date()
    raw = fetch_bcu_rate(rate_date)
    logger.info("BCU raw response: %s", raw)
    return raw


def transform(**context):
    ti = context["ti"]
    bcp_raw = ti.xcom_pull(task_ids="extract_bcp")
    bcu_raw = ti.xcom_pull(task_ids="extract_bcu")
    records = [normalize_bcp(bcp_raw), normalize_bcu(bcu_raw)]
    logger.info("Normalized records: %s", records)
    return records


def validate(**context):
    records = context["ti"].xcom_pull(task_ids="transform")
    validate_records(records)
    logger.info("All %d records passed validation", len(records))
    return records


def report(**context):
    records = context["ti"].xcom_pull(task_ids="validate")
    for r in records:
        logger.info(
            "%s %s %s %s buy=%s sell=%s",
            r["source"], r["country"], r["currency"], r["rate_date"], r["rate_buy"], r["rate_sell"],
        )


with DAG(
    dag_id="mock_exchange_rate_pipeline",
    description="Phase 1: mocked BCP/BCU extraction, normalization, validation (no DB writes yet)",
    default_args=default_args,
    start_date=datetime(2026, 6, 1),
    schedule="@daily",
    catchup=False,
    tags=["learning", "phase1", "mock"],
) as dag:

    extract_bcp_task = PythonOperator(task_id="extract_bcp", python_callable=extract_bcp)
    extract_bcu_task = PythonOperator(task_id="extract_bcu", python_callable=extract_bcu)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    validate_task = PythonOperator(task_id="validate", python_callable=validate)
    report_task = PythonOperator(task_id="report", python_callable=report)

    [extract_bcp_task, extract_bcu_task] >> transform_task >> validate_task >> report_task
