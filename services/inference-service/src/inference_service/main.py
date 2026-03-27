"""FastAPI application factory with lifespan startup/shutdown."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from inference_service.config import Settings
from inference_service.container import init_container, get_container
from inference_service.api.routes import router
from inference_service.api.middleware import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    logging.getLogger().setLevel(settings.log_level)
    container = init_container(settings)
    logger.info("FactoryMind Inference Service starting up")
    if container.worker:
        await container.worker.start()
        logger.info("Kafka consumer worker started")
    yield
    if container.worker:
        await container.worker.stop()
    logger.info("FactoryMind Inference Service shut down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FactoryMind Inference Service",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(router)
    return app


app = create_app()
