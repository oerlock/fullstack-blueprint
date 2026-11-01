"""任务侧 Session 工厂：任务执行与投递自行管理 Session 生命周期。"""

from collections.abc import Callable
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.config.settings import settings
from backend.infrastructure.database.session import create_session_factory


@lru_cache
def get_task_session_factory() -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings.database_engine)


def session_factory_provider() -> Callable[[], async_sessionmaker[AsyncSession]]:
    """返回惰性解析的工厂获取函数，避免导入期依赖运行环境。"""

    return lambda: get_task_session_factory()
