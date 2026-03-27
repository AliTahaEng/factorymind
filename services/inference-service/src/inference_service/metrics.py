"""Prometheus metrics for inference service."""
from prometheus_client import Counter, Histogram, Gauge

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Ensemble inference latency",
    ["model_name"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

INFERENCE_COUNTER = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["model_name", "result"],
)

DEFECT_COUNTER = Counter(
    "defect_detections_total",
    "Total defect detections",
    ["defect_type"],
)

KAFKA_MESSAGES_PROCESSED = Counter(
    "kafka_messages_processed_total",
    "Kafka messages processed",
    ["topic", "status"],
)

KAFKA_CONSUMER_LAG = Gauge(
    "kafka_consumer_lag",
    "Kafka consumer lag",
    ["topic", "partition"],
)

ACTIVE_CONNECTIONS = Gauge(
    "inference_active_connections",
    "Active inference requests in flight",
)
