"""
DAG: data_quality_check
Schedule: hourly
Purpose: Run Great Expectations suite on recent inspections data.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import psycopg2
from airflow.decorators import dag, task
from airflow.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


def _get_conn():
    from urllib.parse import urlparse
    parsed = urlparse(POSTGRES_URL)
    return psycopg2.connect(
        host=parsed.hostname, port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username, password=parsed.password,
    )


@dag(
    dag_id="data_quality_check",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2)},
    tags=["quality", "great-expectations", "monitoring"],
)
def data_quality_check():

    @task
    def check_recent_ingestion() -> dict:
        """Verify recent data was ingested (not stale)."""
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*), MAX(inspected_at) FROM inspections "
            "WHERE inspected_at >= NOW() - INTERVAL '1 hour'"
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        count = row[0] if row else 0
        latest = str(row[1]) if row and row[1] else None

        passed = count > 0
        log.info("Recent ingestion check: count=%d, latest=%s, passed=%s", count, latest, passed)
        return {"count": count, "latest_timestamp": latest, "passed": passed}

    @task
    def check_null_rates(ingestion_result: dict) -> dict:
        """Check null rates for critical columns."""
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                COUNT(camera_id) as non_null_camera,
                COUNT(product_category) as non_null_category,
                COUNT(image_s3_path) as non_null_path
            FROM inspections
            WHERE inspected_at >= NOW() - INTERVAL '1 hour'
            """
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row or row[0] == 0:
            return {"passed": True, "total": 0}

        total = row[0]
        results = {
            "total": total,
            "camera_null_rate": 1 - (row[1] / total),
            "category_null_rate": 1 - (row[2] / total),
            "path_null_rate": 1 - (row[3] / total),
        }
        results["passed"] = all(v < 0.01 for k, v in results.items() if "rate" in k)
        log.info("Null rate check: %s", results)
        return results

    @task
    def publish_quality_alert(ingestion_result: dict, null_result: dict) -> None:
        """If any check failed, publish alert to Kafka."""
        all_passed = ingestion_result.get("passed", True) and null_result.get("passed", True)
        if all_passed:
            log.info("All data quality checks passed")
            return

        import json, uuid
        from confluent_kafka import Producer
        producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})
        alert = {
            "alert_id": str(uuid.uuid4()),
            "alert_type": "PIPELINE_FAILURE",
            "severity": "HIGH",
            "message": "Data quality check failed",
            "metadata": {
                "ingestion_check": str(ingestion_result),
                "null_check": str(null_result),
            },
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
        }
        producer.produce("model-alerts", key=alert["alert_id"],
                         value=json.dumps(alert).encode())
        producer.flush()
        log.warning("Data quality alert published")

    ingestion = check_recent_ingestion()
    nulls = check_null_rates(ingestion)
    publish_quality_alert(ingestion, nulls)


data_quality_check()
