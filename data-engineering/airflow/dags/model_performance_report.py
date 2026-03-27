"""
DAG: model_performance_report
Schedule: daily at 06:00 UTC
Purpose: Query MLflow, compute model performance KPIs, write to PostgreSQL for API.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")


def _get_conn():
    from urllib.parse import urlparse
    parsed = urlparse(POSTGRES_URL)
    import psycopg2
    return psycopg2.connect(
        host=parsed.hostname, port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username, password=parsed.password,
    )


@dag(
    dag_id="model_performance_report",
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["mlops", "reporting", "mlflow"],
)
def model_performance_report():

    @task
    def fetch_production_metrics() -> dict:
        """Query MLflow for production model metrics from last 24h."""
        import mlflow
        mlflow.set_tracking_uri(MLFLOW_URI)
        client = mlflow.tracking.MlflowClient()

        metrics = {}
        for model_name in ["factorymind-yolo", "factorymind-vit", "factorymind-efficientad"]:
            try:
                versions = client.get_latest_versions(model_name, stages=["Production"])
                if versions:
                    v = versions[0]
                    run = client.get_run(v.run_id)
                    metrics[model_name] = {
                        "version": v.version,
                        "run_id": v.run_id,
                        "metrics": dict(run.data.metrics),
                        "status": "production",
                    }
            except Exception as exc:
                log.warning("Could not fetch metrics for %s: %s", model_name, exc)
                metrics[model_name] = {"status": "not_found"}

        return metrics

    @task
    def compute_live_defect_rate() -> dict:
        """Compute last 24h defect rate from inspections table."""
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN is_defective THEN 1 ELSE 0 END) as defective,
                product_category
            FROM inspections
            WHERE inspected_at >= NOW() - INTERVAL '24 hours'
            GROUP BY product_category
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        result = {}
        for row in rows:
            total, defective, category = row
            result[category] = {
                "total": total,
                "defective": defective or 0,
                "defect_rate": (defective or 0) / total if total > 0 else 0.0,
            }
        return result

    @task
    def write_performance_report(model_metrics: dict, defect_rates: dict) -> None:
        """Write combined report to PostgreSQL model_performance_reports table."""
        import json
        conn = _get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance_reports (
                id SERIAL PRIMARY KEY,
                report_date DATE NOT NULL DEFAULT CURRENT_DATE,
                model_metrics JSONB,
                defect_rates JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        cursor.execute(
            """
            INSERT INTO model_performance_reports (report_date, model_metrics, defect_rates)
            VALUES (CURRENT_DATE, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (json.dumps(model_metrics), json.dumps(defect_rates)),
        )
        conn.commit()
        cursor.close()
        conn.close()
        log.info("Performance report written for %s", datetime.utcnow().date())

    metrics = fetch_production_metrics()
    defect_rates = compute_live_defect_rate()
    write_performance_report(metrics, defect_rates)


model_performance_report()
