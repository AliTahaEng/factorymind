"""Dependency injection container — wires adapters to services."""
import logging

from inference_service.config import Settings
from inference_service.adapters.fake_triton_adapter import FakeTritonAdapter
from inference_service.adapters.kafka_consumer_adapter import KafkaConsumerAdapter
from inference_service.adapters.kafka_publisher_adapter import KafkaPublisherAdapter
from inference_service.services.ensemble_service import EnsembleInferenceService
from inference_service.worker.consumer_worker import ConsumerWorker

logger = logging.getLogger(__name__)

_container: "ServiceContainer | None" = None


class ServiceContainer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._setup_backends(settings)
        self.ensemble = EnsembleInferenceService(
            yolo_backend=self._yolo,
            vit_backend=self._vit,
            anomaly_backend=self._anomaly,
            image_width=settings.image_width,
            image_height=settings.image_height,
            yolo_conf_threshold=settings.yolo_confidence_threshold,
            anomaly_threshold=settings.anomaly_threshold,
            vit_threshold=settings.vit_defect_threshold,
        )
        if settings.enable_kafka_consumer:
            self.consumer = KafkaConsumerAdapter(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                topic=settings.kafka_input_topic,
                group_id=settings.kafka_consumer_group,
            )
            self.publisher = KafkaPublisherAdapter(
                bootstrap_servers=settings.kafka_bootstrap_servers,
            )
            self.worker = ConsumerWorker(
                consumer=self.consumer,
                publisher=self.publisher,
                ensemble=self.ensemble,
                output_topic=settings.kafka_output_topic,
            )
        else:
            self.worker = None

    def _setup_backends(self, settings: Settings):
        if settings.enable_triton:
            try:
                from inference_service.adapters.triton_adapter import TritonAdapter
                self._yolo = TritonAdapter(settings.triton_host, settings.triton_port)
                self._vit = TritonAdapter(settings.triton_host, settings.triton_port)
                self._anomaly = TritonAdapter(settings.triton_host, settings.triton_port)
                logger.info("Using TritonAdapter backends")
                return
            except Exception as exc:
                logger.warning("Triton unavailable, falling back to FakeTritonAdapter: %s", exc)
        self._yolo = FakeTritonAdapter(defect_probability=0.1)
        self._vit = FakeTritonAdapter(defect_probability=0.1)
        self._anomaly = FakeTritonAdapter(defect_probability=0.1)
        logger.info("Using FakeTritonAdapter backends")


def init_container(settings: Settings) -> ServiceContainer:
    global _container
    _container = ServiceContainer(settings)
    return _container


def get_container() -> ServiceContainer:
    if _container is None:
        raise RuntimeError("Container not initialized")
    return _container
