"""Camera simulator — reads MVTec AD images and publishes to Kafka."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    schema_registry_url: str = "http://localhost:8081"
    mvtec_data_path: str = "/data/mvtec"
    images_per_second: float = 2.0
    camera_id: str = "camera-01"

    model_config = {"env_file": ".env"}


settings = Settings()


def run() -> None:
    """Main simulator loop — implement in Phase 03."""
    print(f"Camera simulator starting. Data path: {settings.mvtec_data_path}")
    print("Kafka producer will be implemented in Phase 03.")


if __name__ == "__main__":
    run()
