"""FastAPI application factory with lifespan."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_service.config import Settings
from api_service.container import init_container
from api_service.api.middleware import RequestIDMiddleware
from api_service.api.v1 import auth, inspections, analytics, models, websocket

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    logging.getLogger().setLevel(settings.log_level)
    container = init_container(settings)
    logger.info("FactoryMind API Service starting up")
    await container.startup()
    yield
    await container.shutdown()
    logger.info("FactoryMind API Service shut down")


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(
        title="FactoryMind API Service",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins + ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    prefix = settings.api_prefix
    app.include_router(auth.router, prefix=prefix)
    app.include_router(inspections.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)
    app.include_router(models.router, prefix=prefix)
    app.include_router(websocket.router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/ready")
    async def ready():
        return {"status": "ready"}

    @app.get("/metrics")
    async def metrics():
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
