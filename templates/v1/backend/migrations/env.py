"""Alembic 迁移环境（async 模板）。"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from backend.infrastructure.database import models  # noqa: F401  统一注册业务模型
from backend.infrastructure.database.engine import build_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 数据库 URL 优先取 alembic -x url=... 或 set_main_option 注入，否则由 Settings 组装
url = context.get_x_argument(as_dictionary=True).get("url")
if url is None and not config.get_main_option("sqlalchemy.url"):
    from backend.config.settings import get_settings

    config.set_main_option("sqlalchemy.url", build_database_url(get_settings().database))

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
