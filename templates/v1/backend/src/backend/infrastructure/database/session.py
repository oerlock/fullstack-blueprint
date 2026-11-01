"""Session 工厂与生命周期。"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from backend.infrastructure.database.config import DatabaseSettings
from backend.infrastructure.database.engine import create_database_engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_session_factory(settings: DatabaseSettings) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(create_database_engine(settings))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：按请求创建 Session，结束时回滚并关闭。

    事务提交由业务用例负责，此处不隐式 commit。
    """

    from backend.config.settings import settings

    factory = get_session_factory(settings.database)
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
