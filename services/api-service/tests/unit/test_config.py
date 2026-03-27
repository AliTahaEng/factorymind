"""Test Settings configuration."""
import pytest
from api_service.config import Settings


def test_settings_defaults():
    s = Settings(
        database_url="postgresql+asyncpg://user:pass@localhost/factorymind",
        redis_url="redis://localhost:6379/0",
        jwt_secret_key="super-secret-key",
        kafka_bootstrap_servers="localhost:9092",
        schema_registry_url="http://localhost:8081",
    )
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_access_token_expire_minutes == 60
    assert s.jwt_refresh_token_expire_days == 7
    assert s.api_prefix == "/api/v1"


def test_settings_require_database_url():
    """Settings should use defaults when required fields have defaults."""
    s = Settings()
    assert s.database_url is not None
