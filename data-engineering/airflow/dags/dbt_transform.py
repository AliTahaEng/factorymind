"""
DAG: dbt_transform
Schedule: daily at midnight
Purpose: Run all dbt models to refresh analytics tables.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timedelta

from airflow.decorators import dag, task

DBT_PROJECT_DIR = "/opt/airflow/dbt/factorymind"
DBT_PROFILES_DIR = "/opt/airflow/dbt"


@dag(
    dag_id="dbt_transform",
    schedule="0 0 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=10)},
    tags=["dbt", "analytics", "transform"],
)
def dbt_transform():

    @task
    def run_dbt_deps() -> None:
        result = subprocess.run(
            ["dbt", "deps", "--project-dir", DBT_PROJECT_DIR, "--profiles-dir", DBT_PROFILES_DIR],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"dbt deps failed:\n{result.stderr}")

    @task
    def run_dbt_models() -> dict:
        result = subprocess.run(
            ["dbt", "run", "--project-dir", DBT_PROJECT_DIR, "--profiles-dir", DBT_PROFILES_DIR],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"dbt run failed:\n{result.stderr}")
        return {"output": result.stdout[-2000:]}

    @task
    def run_dbt_tests() -> dict:
        result = subprocess.run(
            ["dbt", "test", "--project-dir", DBT_PROJECT_DIR, "--profiles-dir", DBT_PROFILES_DIR],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"dbt test failed:\n{result.stderr}")
        return {"output": result.stdout[-2000:]}

    deps = run_dbt_deps()
    models = run_dbt_models()
    tests = run_dbt_tests()
    deps >> models >> tests


dbt_transform()
