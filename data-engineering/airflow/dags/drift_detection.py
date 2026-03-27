"""
DAG: drift_detection
Schedule: every 6 hours
Purpose: Compute PSI drift score. Publish alert and trigger retraining if PSI > 0.2.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta

import numpy as np
import psycopg2
from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
PSI_THRESHOLD = 0.2
REFERENCE_WINDOW_DAYS = 30
RECENT_WINDOW_HOURS = 6
MIN_SAMPLES = 50


def _get_conn():
    from urllib.parse import urlparse
    parsed = urlparse(POSTGRES_URL)
    return psycopg2.connect(
        host=parsed.hostname, port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username, password=parsed.password,
    )


def _compute_psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    ref_scalar = reference.mean(axis=1)
    cur_scalar = current.mean(axis=1)
    edges = np.percentile(ref_scalar, np.linspace(0, 100, bins + 1))
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_counts = np.histogram(ref_scalar, bins=edges)[0]
    cur_counts = np.histogram(cur_scalar, bins=edges)[0]
    ref_pct = (ref_counts + 1e-6) / (len(ref_scalar) + 1e-6 * bins)
    cur_pct = (cur_counts + 1e-6) / (len(cur_scalar) + 1e-6 * bins)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


@dag(
    dag_id="drift_detection",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["mlops", "drift", "monitoring"],
)
def drift_detection():

    @task
    def compute_drift_score() -> dict:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT embedding::text FROM inspection_embeddings ie
            JOIN inspections i ON ie.inspection_id = i.id
            WHERE i.inspected_at >= NOW() - INTERVAL '%s days'
            ORDER BY RANDOM() LIMIT 1000
            """,
            (REFERENCE_WINDOW_DAYS,),
        )
        ref_rows = cursor.fetchall()
        cursor.execute(
            """
            SELECT embedding::text FROM inspection_embeddings ie
            JOIN inspections i ON ie.inspection_id = i.id
            WHERE i.inspected_at >= NOW() - INTERVAL '%s hours'
            ORDER BY i.inspected_at DESC LIMIT 500
            """,
            (RECENT_WINDOW_HOURS,),
        )
        recent_rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if len(ref_rows) < MIN_SAMPLES or len(recent_rows) < MIN_SAMPLES:
            log.warning("Insufficient data: ref=%d recent=%d", len(ref_rows), len(recent_rows))
            return {"psi": 0.0, "drift_detected": False, "reason": "insufficient_data"}

        ref_embeddings = np.array([json.loads(r[0]) for r in ref_rows])
        recent_embeddings = np.array([json.loads(r[0]) for r in recent_rows])
        psi = _compute_psi(ref_embeddings, recent_embeddings)

        log.info("Drift PSI=%.4f (threshold=%.2f)", psi, PSI_THRESHOLD)
        return {
            "psi": psi,
            "drift_detected": psi > PSI_THRESHOLD,
            "ref_samples": len(ref_rows),
            "recent_samples": len(recent_rows),
        }

    @task
    def publish_alert_if_drift(drift_result: dict) -> bool:
        if not drift_result.get("drift_detected"):
            return False
        from confluent_kafka import Producer
        producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})
        alert = {
            "alert_id": str(uuid.uuid4()),
            "alert_type": "MODEL_DRIFT",
            "severity": "HIGH" if drift_result["psi"] > 0.4 else "MEDIUM",
            "message": f"Data drift detected: PSI={drift_result['psi']:.4f} > {PSI_THRESHOLD}",
            "metadata": {"psi": str(drift_result["psi"])},
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
        }
        producer.produce("model-alerts", key=alert["alert_id"],
                         value=json.dumps(alert).encode())
        producer.flush()
        return True

    drift_result = compute_drift_score()
    should_retrain = publish_alert_if_drift(drift_result)

    trigger = TriggerDagRunOperator(
        task_id="trigger_dataset_preparation",
        trigger_dag_id="dataset_preparation",
        wait_for_completion=False,
    )
    should_retrain >> trigger


drift_detection()
