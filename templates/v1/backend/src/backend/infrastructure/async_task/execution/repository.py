"""任务执行记录数据访问。调用方负责事务边界。"""

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.async_task.execution.models import TaskExecution
from backend.infrastructure.async_task.execution.schemas import TaskExecutionStatus


def build_failure_result(exc: BaseException) -> dict:
    return {"error_type": type(exc).__name__, "error_message": str(exc)}


def build_success_result(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {"value": value}


async def next_attempt(session: AsyncSession, outbox_id: int) -> int:
    stmt = select(func.max(TaskExecution.attempt)).where(TaskExecution.outbox_id == outbox_id)
    current = (await session.execute(stmt)).scalar_one_or_none()
    return (current or 0) + 1


async def create_running(
    session: AsyncSession, outbox_id: int, attempt: int, *, now: datetime
) -> TaskExecution:
    row = TaskExecution(
        outbox_id=outbox_id,
        attempt=attempt,
        status=TaskExecutionStatus.RUNNING.value,
        started_at=now,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return row


async def finish(
    session: AsyncSession,
    execution_id: int,
    *,
    status: TaskExecutionStatus,
    result: dict | None,
    now: datetime,
) -> None:
    await session.execute(
        update(TaskExecution)
        .where(TaskExecution.id == execution_id, TaskExecution.status == TaskExecutionStatus.RUNNING.value)
        .values(
            status=status.value,
            result=result,
            completed_at=now,
        )
    )
