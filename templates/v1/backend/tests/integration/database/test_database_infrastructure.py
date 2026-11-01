"""数据库基础设施最小集成测试（需 --with-database）。"""

import pytest
from sqlalchemy import text

pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_database,
    pytest.mark.asyncio(loop_scope="session"),
]


async def test_test_database_connectable(db_session) -> None:
    result = await db_session.execute(text("SELECT DATABASE()"))
    database_name = result.scalar_one()
    assert database_name == "app_test"


async def test_migrations_applied(database_test_engine) -> None:
    async with database_test_engine.connect() as conn:
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        assert result.scalar_one() is not None
