"""Prometheus metrics for API service."""
from prometheus_client import Counter, Histogram, Gauge

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

AUTH_EVENTS = Counter(
    "auth_events_total",
    "Authentication events",
    ["event_type"],
)

INSPECTIONS_INGESTED = Counter(
    "inspections_ingested_total",
    "Total inspection results ingested from Kafka",
    ["result"],
)

ACTIVE_WEBSOCKET_CONNECTIONS = Gauge(
    "active_websocket_connections",
    "Active WebSocket connections",
)

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.5],
)
