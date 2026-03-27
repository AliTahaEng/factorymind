"""API service configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://factorymind:secret@localhost:5435/factorymind"

    # Redis
    redis_url: str = "redis://localhost:6381/0"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    schema_registry_url: str = "http://localhost:8081"
    kafka_results_topic: str = "processed-results"
    kafka_consumer_group: str = "api-service"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3002"]

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"

    # Observability
    log_level: str = "INFO"
