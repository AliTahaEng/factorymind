"""
DAG: model_training (triggered on-demand)
Purpose: Trigger ML training jobs on EC2 Spot instances.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task

MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
S3_DATASETS_BUCKET = os.environ.get("S3_DATASETS_BUCKET", "factorymind-datasets-dev")
S3_MODELS_BUCKET = os.environ.get("S3_MODELS_BUCKET", "factorymind-models-dev")


@dag(
    dag_id="model_training",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={"retries": 0},
    tags=["mlops", "training"],
)
def model_training():

    @task
    def prepare_training_config(**context) -> dict:
        conf = context.get("dag_run", {}).conf or {}
        dataset_version = conf.get("dataset_version", "latest")
        return {
            "dataset_version": dataset_version,
            "mlflow_uri": MLFLOW_URI,
            "s3_datasets_bucket": S3_DATASETS_BUCKET,
            "s3_models_bucket": S3_MODELS_BUCKET,
            "run_id": f"auto-{int(datetime.utcnow().timestamp())}",
        }

    @task
    def register_training_run(config: dict) -> str:
        """Register an MLflow experiment run for this training job."""
        import mlflow
        mlflow.set_tracking_uri(config["mlflow_uri"])
        mlflow.set_experiment("factorymind-auto-retrain")
        with mlflow.start_run(run_name=config["run_id"]) as run:
            mlflow.log_params({
                "dataset_version": config["dataset_version"],
                "trigger": "automated",
            })
            return run.info.run_id

    @task
    def notify_training_queued(run_id: str, config: dict) -> dict:
        """In production: submit EC2 Spot job. Here: log intent."""
        return {
            "status": "queued",
            "mlflow_run_id": run_id,
            "dataset_version": config["dataset_version"],
            "message": "Training job queued. In production: EC2 Spot instance launched.",
        }

    config = prepare_training_config()
    run_id = register_training_run(config)
    notify_training_queued(run_id, config)


model_training()
