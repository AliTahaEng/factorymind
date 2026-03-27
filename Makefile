.PHONY: up down build test-api test-inference test-all lint format simulate dbt-run dbt-test

up:
	docker compose up --build -d

down:
	docker compose down -v

build:
	docker compose build

up-infra:
	docker compose up postgres redis kafka schema-registry localstack mlflow-server -d

test-api:
	cd services/api-service && python -m pytest tests/ -v --cov=src

test-inference:
	cd services/inference-service && python -m pytest tests/ -v --cov=src

test-all: test-api test-inference

lint:
	cd services/api-service && ruff check src/
	cd services/inference-service && ruff check src/

format:
	cd services/api-service && ruff format src/
	cd services/inference-service && ruff format src/

simulate:
	docker compose --profile simulation up camera-simulator -d

dbt-run:
	cd data-engineering/dbt/factorymind && dbt run

dbt-test:
	cd data-engineering/dbt/factorymind && dbt test
