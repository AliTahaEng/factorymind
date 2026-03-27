# FactoryMind — Integration & E2E Test Suite

## Overview

This directory contains the full integration and end-to-end test suite for the
FactoryMind MLOps platform (Phase 12). Tests are organized into four categories:

| Directory          | Coverage                                      |
|--------------------|-----------------------------------------------|
| `e2e/`             | Auth flow, inspection CRUD, inference service |
| `drift/`           | Data-drift simulation (pixel distribution)    |
| `model_promotion/` | Model version state-machine (promote/rollback)|
| `load/`            | Concurrent requests, rate-limit smoke test    |
| `fixtures/`        | Shared image-generation helpers (not tests)   |

---

## Prerequisites

- Docker + Docker Compose v2
- The `factorymind` Docker network must exist:
  ```bash
  docker network create factorymind
  ```

---

## Running tests

### 1. Start the test stack

```bash
# From the project root (factorymind/)
docker compose -f docker-compose.yml -f tests/docker-compose.test.yml up -d --build
```

Wait for all services to become healthy:

```bash
docker compose -f docker-compose.yml -f tests/docker-compose.test.yml ps
```

### 2. Install test dependencies (host-side runner)

```bash
pip install -r tests/requirements.txt
```

### 3. Run the full suite

```bash
API_BASE_URL=http://localhost:8000 \
INFERENCE_BASE_URL=http://localhost:8001 \
pytest tests/ -v
```

### 4. Run a specific category

```bash
# Auth flow only
pytest tests/e2e/test_auth_flow.py -v

# Drift tests only
pytest tests/drift/ -v

# Load tests only
pytest tests/load/ -v
```

---

## Environment variables

| Variable                | Default               | Description                        |
|-------------------------|-----------------------|------------------------------------|
| `API_BASE_URL`          | `http://localhost:8000` | Base URL of the api-service        |
| `INFERENCE_BASE_URL`    | `http://localhost:8001` | Base URL of the inference-service  |
| `TEST_ADMIN_USERNAME`   | `admin`               | Admin account username             |
| `TEST_ADMIN_PASSWORD`   | `admin`               | Admin account password             |
| `TEST_VIEWER_USERNAME`  | `viewer`              | Viewer-role account username       |
| `TEST_VIEWER_PASSWORD`  | `viewer`              | Viewer-role account password       |

---

## Tear down

```bash
docker compose -f docker-compose.yml -f tests/docker-compose.test.yml down -v
```
