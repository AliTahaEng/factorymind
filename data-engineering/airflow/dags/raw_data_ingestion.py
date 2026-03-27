"""
DAG: raw_data_ingestion
Schedule: every 5 minutes
Purpose: Consume raw-inspections Kafka topic, store images to S3, metadata to PostgreSQL.
"""
from __future__ import annotations

import io
import json
import os
from datetime import datetime, timedelta

import fastavro
import psycopg2
from airflow.decorators import dag, task
from airflow.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT_URL", "")
S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET", "factorymind-raw-dev")
BATCH_SIZE = 100
POLL_TIMEOUT = 30.0

RAW_SCHEMA = {
    "type": "record",
    "name": "RawInspection",
    "namespace": "com.factorymind",
    "fields": [
        {"name": "image_id", "type": "string"},
        {"name": "camera_id", "type": "string"},
        {"name": "product_category", "type": "string"},
        {"name": "image_bytes", "type": "bytes"},
        {"name": "timestamp", "type": "long"},
        {"name": "conveyor_speed", "type": "float", "default": 1.0},
    ],
}


def _get_conn():
    from urllib.parse import urlparse
    parsed = urlparse(POSTGRES_URL)
    return psycopg2.connect(
        host=parsed.hostname, port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username, password=parsed.password,
    )


@dag(
    dag_id="raw_data_ingestion",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
    tags=["ingestion", "kafka", "s3"],
)
def raw_data_ingestion():

    @task
    def consume_and_store() -> dict:
        import boto3
        from confluent_kafka import Consumer

        consumer = Consumer({
            "bootstrap.servers": KAFKA_BOOTSTRAP,
            "group.id": "airflow-raw-ingestion",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        consumer.subscribe(["raw-inspections"])

        s3 = boto3.client("s3", endpoint_url=S3_ENDPOINT or None,
                          region_name="us-east-1")
        conn = _get_conn()
        cursor = conn.cursor()
        parsed_schema = fastavro.parse_schema(RAW_SCHEMA)

        stored = 0
        for _ in range(BATCH_SIZE):
            msg = consumer.poll(timeout=POLL_TIMEOUT / BATCH_SIZE)
            if msg is None or msg.error():
                break
            try:
                buf = io.BytesIO(msg.value())
                record = fastavro.schemaless_reader(buf, parsed_schema)
            except Exception as e:
                log.warning("Failed to decode message: %s", e)
                consumer.commit(msg)
                continue

            ts = datetime.fromtimestamp(record["timestamp"] / 1000)
            s3_key = (
                f"images/{ts.year}/{ts.month:02d}/{ts.day:02d}/"
                f"{record['camera_id']}/{record['image_id']}.jpg"
            )
            s3.put_object(
                Bucket=S3_RAW_BUCKET,
                Key=s3_key,
                Body=record["image_bytes"],
                ContentType="image/jpeg",
            )

            cursor.execute(
                """
                INSERT INTO inspections (id, camera_id, product_category, image_s3_path, inspected_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (record["image_id"], record["camera_id"], record["product_category"],
                 f"s3://{S3_RAW_BUCKET}/{s3_key}", ts),
            )
            conn.commit()
            consumer.commit(msg)
            stored += 1

        cursor.close()
        conn.close()
        consumer.close()
        log.info("Stored %d images in this run", stored)
        return {"stored": stored, "run_at": datetime.utcnow().isoformat()}

    consume_and_store()


raw_data_ingestion()
