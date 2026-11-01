"""真实数据库集成测试夹具（需 --with-database）。

结构：会话级一次——DROP 重建测试库并执行 alembic upgrade head（含触发器等迁移对象）。
数据：每测试函数后 TRUNCATE 全部业务表（跳过 alembic_version）并重灌基础数据。
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.config.settings import get_settings, settings
from backend.infrastructure.database.engine import (
    build_database_url,
    build_server_url,
    create_test_engine,
)
from backend.infrastructure.database.seed import run_seeds
from backend.infrastructure.database.session import create_session_factory

pytestmark = [pytest.mark.integration, pytest.mark.requires_database]

_ALEMBIC_INI = get_settings().project_root / "alembic.ini"


async def _recreate_test_database(engine: AsyncEngine, test_database: str) -> None:
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS `{test_database}`"))
        await conn.execute(text(f"CREATE DATABASE `{test_database}` CHARACTER SET utf8mb4"))
        await conn.commit()


def _upgrade_head(test_database: str) -> None:
    config = AlembicConfig(str(_ALEMBIC_INI))
    test_url = build_database_url(settings.database.model_copy(update={"database": test_database}))
    config.set_main_option("sqlalchemy.url", test_url)
    command.upgrade(config, "head")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def database_test_engine() -> AsyncGenerator[AsyncEngine, None]:
    database_settings = settings.database

    server_engine = create_async_engine(build_server_url(database_settings))
    try:
        await _recreate_test_database(server_engine, database_settings.test_database)
    finally:
        await server_engine.dispose()
    # env.py 内部使用 asyncio.run，需在独立线程中执行，避免与当前事件循环冲突
    await asyncio.to_thread(_upgrade_head, database_settings.test_database)

    engine = create_test_engine(database_settings)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(autouse=True)
def _clear_settings_cache(request) -> AsyncGenerator[None, None]:
    if request.node.get_closest_marker("requires_database") is None:
        yield
        return
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(
    database_test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """带数据清理的测试 Session：测试后 TRUNCATE 全部业务表并重灌基础数据。"""

    factory: async_sessionmaker[AsyncSession] = create_session_factory(database_test_engine)
    async with factory() as session:
        yield session
        await session.rollback()

    async with database_test_engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_name != 'alembic_version'"
            ),
            {"schema": settings.database.test_database},
        )
        tables = [row[0] for row in result]
        if tables:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            # MySQL 不支持一条 TRUNCATE 多张表，逐表清理
            for table in tables:
                await conn.execute(text(f"TRUNCATE TABLE `{table}`"))
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        await conn.commit()

    async with factory() as session:
        await run_seeds(session)
        await session.commit()
