"""应用入口。"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.errors.handlers import register_exception_handlers
from backend.presentation.http.middleware import register_middlewares
from backend.presentation.http.router import API_PREFIX, create_api_router, create_health_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
        func_app: FastAPI,
):
    try:
        logger.info("Opening application resources")
        await settings.cache_clients.open_all()
        yield
    finally:
        await settings.cache_clients.close_all()
        await settings.database_engine.dispose()
        logger.info("Closed application resources")


def create_app(
        lifespan_=lifespan,
        cors_settings=None,
) -> FastAPI:
    from backend.config.settings import CorsSettings  # noqa: F401  保持导入兼容

    app_ = FastAPI(lifespan=lifespan_)
    register_middlewares(app_, cors_settings or settings.cors)
    register_exception_handlers(app_)
    app_.include_router(create_health_router())
    app_.include_router(create_api_router(), prefix=API_PREFIX)
    return app_


app = create_app()
