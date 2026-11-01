"""`@task_execution` 装饰器：记录每次执行尝试，重试由 Taskiq 负责。"""

import asyncio
import functools
from collections.abc import Callable
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.execution import repository
from backend.infrastructure.async_task.execution.schemas import TaskExecutionStatus
from backend.infrastructure.async_task.session import get_task_session_factory


def task_execution(
    func: Callable | None = None,
    *,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
    now_fn: Callable[[], datetime] | None = None,
):
    """剥离保留参数 outbox_id；每次尝试建一条 execution（attempt 递增）。

    - 正常返回 → completed，保存返回值
    - 异常 → failed，保存异常信息后继续抛出，由 Taskiq 处理重试
    - 取消 → cancelled
    """

    def decorate(f: Callable) -> Callable:
        @functools.wraps(f)
        async def wrapper(*, payload: dict, **kwargs):
            outbox_id = kwargs.pop("outbox_id", None)
            if outbox_id is None:
                raise ValueError("缺少保留参数 outbox_id")
            factory = session_factory or get_task_session_factory()
            clock = now_fn or utcnow

            async with factory() as session:
                attempt = await repository.next_attempt(session, outbox_id)
                execution = await repository.create_running(
                    session, outbox_id, attempt, now=clock()
                )
                await session.commit()

                try:
                    result = await f(payload=payload)
                except asyncio.CancelledError:
                    await repository.finish(
                        session,
                        execution.id,
                        status=TaskExecutionStatus.CANCELLED,
                        result=None,
                        now=clock(),
                    )
                    await session.commit()
                    raise
                except BaseException as exc:
                    await repository.finish(
                        session,
                        execution.id,
                        status=TaskExecutionStatus.FAILED,
                        result=repository.build_failure_result(exc),
                        now=clock(),
                    )
                    await session.commit()
                    raise

                await repository.finish(
                    session,
                    execution.id,
                    status=TaskExecutionStatus.COMPLETED,
                    result=repository.build_success_result(result),
                    now=clock(),
                )
                await session.commit()
                return result

        return wrapper

    return decorate(func) if func is not None else decorate
