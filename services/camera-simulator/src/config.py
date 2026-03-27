"""Camera simulator configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    schema_registry_url: str = "http://localhost:8081"
    mvtec_data_path: str = "/data/mvtec"
    images_per_second: float = 2.0
    camera_id: str = "camera-01"
    loop_dataset: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
