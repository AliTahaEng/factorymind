"""Inference service configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_input_topic: str = "raw-inspections"
    kafka_output_topic: str = "processed-results"
    kafka_consumer_group: str = "inference-service"
    schema_registry_url: str = "http://localhost:8081"

    # Triton
    triton_host: str = "localhost"
    triton_port: int = 8001  # gRPC port

    # Model names
    yolo_model_name: str = "yolov8_defect"
    vit_model_name: str = "vit_classifier"
    anomaly_model_name: str = "efficientad_anomaly"

    # Image preprocessing
    image_width: int = 640
    image_height: int = 640

    # Thresholds
    yolo_confidence_threshold: float = 0.25
    anomaly_threshold: float = 0.5
    vit_defect_threshold: float = 0.5

    # Observability
    log_level: str = "INFO"

    # AWS
    aws_region: str = "us-east-1"
    s3_exports_bucket: str = "factorymind-exports-dev"
    s3_endpoint_url: str = "http://localhost:4566"

    # Feature flags
    enable_kafka_consumer: bool = True
    enable_triton: bool = False  # disabled until Triton is deployed
