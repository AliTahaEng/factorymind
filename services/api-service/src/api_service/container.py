"""Service container — DI wiring."""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api_service.config import Settings
from api_service.adapters.redis_token_store import RedisTokenStore
from api_service.services.auth_service import AuthService
from api_service.services.result_ingestion_service import ResultIngestionService

logger = logging.getLogger(__name__)

_container: "ServiceContainer | None" = None


class ServiceContainer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        self._token_store = RedisTokenStore(settings.redis_url)
        self.auth_service = AuthService(settings, self._token_store)
        self.ingestion_service = ResultIngestionService(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            topic=settings.kafka_results_topic,
            group_id=settings.kafka_consumer_group,
            session_factory=self.session_factory,
        )

    async def startup(self) -> None:
        await self.ingestion_service.start()
        logger.info("ServiceContainer started")

    async def shutdown(self) -> None:
        await self.ingestion_service.stop()
        await self._engine.dispose()
        logger.info("ServiceContainer stopped")


def init_container(settings: Settings) -> ServiceContainer:
    global _container
    _container = ServiceContainer(settings)
    return _container


def get_container() -> ServiceContainer:
    if _container is None:
        raise RuntimeError("Container not initialized")
    return _container
