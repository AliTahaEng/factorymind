"""Test Settings configuration."""
import pytest
from inference_service.config import Settings


def test_settings_defaults():
    s = Settings(
        kafka_bootstrap_servers="localhost:9092",
        schema_registry_url="http://localhost:8081",
    )
    assert s.kafka_input_topic == "raw-inspections"
    assert s.kafka_output_topic == "processed-results"
    assert s.kafka_consumer_group == "inference-service"
    assert s.triton_host == "localhost"
    assert s.triton_port == 8001
    assert s.log_level == "INFO"


def test_settings_env_override():
    s = Settings(
        kafka_bootstrap_servers="kafka:9092",
        schema_registry_url="http://schema-registry:8081",
        enable_triton=True,
        yolo_confidence_threshold=0.5,
    )
    assert s.kafka_bootstrap_servers == "kafka:9092"
    assert s.enable_triton is True
    assert s.yolo_confidence_threshold == 0.5
