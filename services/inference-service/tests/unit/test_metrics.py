"""Test Prometheus metric registration."""
from prometheus_client import REGISTRY


def test_inference_latency_registered():
    names = {m.name for m in REGISTRY.collect()}
    assert "inference_latency_seconds" in names


def test_inference_counter_registered():
    names = {m.name for m in REGISTRY.collect()}
    assert "inference_requests_total" in names


def test_defect_counter_registered():
    names = {m.name for m in REGISTRY.collect()}
    assert "defect_detections_total" in names


def test_kafka_counter_registered():
    names = {m.name for m in REGISTRY.collect()}
    assert "kafka_messages_processed_total" in names
