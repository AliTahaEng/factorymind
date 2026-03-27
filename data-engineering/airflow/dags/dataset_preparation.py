"""
DAG: dataset_preparation (triggered on-demand by drift_detection)
Purpose: Sample recent images from S3, version with DVC, trigger training.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT_URL", "")
S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET", "factorymind-raw-dev")
S3_DATASETS_BUCKET = os.environ.get("S3_DATASETS_BUCKET", "factorymind-datasets-dev")
SAMPLE_SIZE = 5000


@dag(
    dag_id="dataset_preparation",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["mlops", "dataset", "dvc"],
)
def dataset_preparation():

    @task
    def sample_recent_images() -> dict:
        import psycopg2
        from urllib.parse import urlparse
        parsed = urlparse(POSTGRES_URL)
        conn = psycopg2.connect(
            host=parsed.hostname, port=parsed.port or 5432,
            dbname=parsed.path.lstrip("/"),
            user=parsed.username, password=parsed.password,
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, image_s3_path, product_category FROM inspections "
            "ORDER BY inspected_at DESC LIMIT %s",
            (SAMPLE_SIZE,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"samples": [{"id": r[0], "s3_path": r[1], "category": r[2]} for r in rows],
                "count": len(rows)}

    @task
    def version_dataset_with_dvc(sample_result: dict) -> str:
        import boto3
        s3 = boto3.client("s3", endpoint_url=S3_ENDPOINT or None, region_name="us-east-1")
        dataset_version = f"v{int(datetime.utcnow().timestamp())}"
        metadata = {
            "version": dataset_version,
            "n_samples": sample_result["count"],
            "created_at": datetime.utcnow().isoformat(),
            "source": "recent_production_images",
        }
        s3.put_object(
            Bucket=S3_DATASETS_BUCKET,
            Key=f"versions/{dataset_version}/metadata.json",
            Body=json.dumps(metadata).encode(),
        )
        return dataset_version

    samples = sample_recent_images()
    version_dataset_with_dvc(samples)


dataset_preparation()
