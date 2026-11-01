"""数据库 Engine 构建，全局复用。"""

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from backend.infrastructure.database.config import DatabaseSettings


def build_database_url(settings: DatabaseSettings) -> str:
    password = settings.password.get_secret_value()
    return (
        f"mysql+asyncmy://{settings.user}:{password}"
        f"@{settings.host}:{settings.port}/{settings.database}?charset=utf8mb4"
    )


def create_database_engine(settings: DatabaseSettings) -> AsyncEngine:
    return _create_async_engine(
        build_database_url(settings),
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_recycle=settings.pool_recycle,
        pool_pre_ping=settings.pool_pre_ping,
        echo=settings.echo,
    )


def create_test_engine(settings: DatabaseSettings) -> AsyncEngine:
    test_settings = settings.model_copy(update={"database": settings.test_database})
    return create_database_engine(test_settings)


def build_server_url(settings: DatabaseSettings) -> str:
    """不指定库的连接 URL，用于创建和删除数据库。"""

    password = settings.password.get_secret_value()
    return f"mysql+asyncmy://{settings.user}:{password}@{settings.host}:{settings.port}/?charset=utf8mb4"
