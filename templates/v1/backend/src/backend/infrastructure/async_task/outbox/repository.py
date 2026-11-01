"""任务投递箱数据访问。调用方负责事务边界。"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.async_task.outbox.dto import CreateTaskOutboxDTO
from backend.infrastructure.async_task.outbox.models import TaskOutbox


async def create_task_outbox(
    session: AsyncSession, dto: CreateTaskOutboxDTO, *, now: datetime
) -> TaskOutbox:
    row = TaskOutbox(
        task_name=dto.task_name,
        business_id=dto.business_id,
        user_id=dto.user_id,
        payload=dto.payload,
        available_at=dto.available_at or now,
        expires_at=dto.expires_at,
        max_publish_attempts=dto.max_publish_attempts,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return row


async def fetch_pending_for_update(
    session: AsyncSession, *, now: datetime, limit: int
) -> Sequence[TaskOutbox]:
    """`FOR UPDATE SKIP LOCKED` 领取一批待投递任务，多实例安全。"""

    stmt = (
        select(TaskOutbox)
        .where(
            TaskOutbox.published_at.is_(None),
            TaskOutbox.cancelled_at.is_(None),
            TaskOutbox.available_at <= now,
            TaskOutbox.publish_attempts < TaskOutbox.max_publish_attempts,
        )
        .order_by(TaskOutbox.available_at, TaskOutbox.id)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_task_outbox(session: AsyncSession, outbox_id: int) -> TaskOutbox | None:
    return await session.get(TaskOutbox, outbox_id)


async def increment_publish_attempts(
    session: AsyncSession, outbox_ids: Sequence[int]
) -> None:
    if not outbox_ids:
        return
    await session.execute(
        update(TaskOutbox)
        .where(TaskOutbox.id.in_(outbox_ids))
        .values(publish_attempts=TaskOutbox.publish_attempts + 1)
    )


async def mark_published(session: AsyncSession, outbox_id: int, *, now: datetime) -> None:
    await session.execute(
        update(TaskOutbox)
        .where(TaskOutbox.id == outbox_id, TaskOutbox.published_at.is_(None))
        .values(published_at=now)
    )


async def mark_cancelled(session: AsyncSession, outbox_id: int, *, now: datetime) -> None:
    await session.execute(
        update(TaskOutbox)
        .where(
            TaskOutbox.id == outbox_id,
            TaskOutbox.published_at.is_(None),
            TaskOutbox.cancelled_at.is_(None),
        )
        .values(cancelled_at=now)
    )


async def record_publish_failure(
    session: AsyncSession,
    outbox_id: int,
    *,
    failure: dict,
    next_available_at: datetime | None,
    cancel: bool,
    now: datetime,
) -> None:
    """记录投递失败：可重试则推迟 available_at，否则取消。"""

    values: dict = {"publish_failure": failure}
    if next_available_at is not None:
        values["available_at"] = next_available_at
    if cancel:
        values["cancelled_at"] = now
    await session.execute(
        update(TaskOutbox)
        .where(TaskOutbox.id == outbox_id, TaskOutbox.published_at.is_(None))
        .values(**values)
    )
