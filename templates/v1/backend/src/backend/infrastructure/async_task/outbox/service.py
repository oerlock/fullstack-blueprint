"""任务投递箱服务：在业务事务内创建任务。"""

from collections.abc import Callable
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.outbox import repository
from backend.infrastructure.async_task.outbox.dto import CreateTaskOutboxDTO
from backend.infrastructure.async_task.outbox.models import TaskOutbox, TaskOutboxEntity


class TaskOutboxService:
    """在调用方的业务事务（AsyncSession）内写入 task_outbox，随业务一起提交。"""

    def __init__(self, session: AsyncSession, *, now_fn: Callable[[], datetime] | None = None):
        self._session = session
        self._now_fn = now_fn or utcnow

    async def create(self, dto: CreateTaskOutboxDTO) -> TaskOutboxEntity:
        return await repository.create_task_outbox(
            self._session, dto, now=self._now_fn()
        )


__all__ = ["TaskOutbox", "TaskOutboxService"]
