"""outbox 数据访问集成测试（--with-database）。"""

import asyncio
from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.outbox import repository
from backend.infrastructure.async_task.outbox.dto import CreateTaskOutboxDTO
from backend.infrastructure.async_task.outbox.models import TaskOutbox

pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_database,
    pytest.mark.asyncio(loop_scope="session"),
]


async def _create(session: AsyncSession, **overrides) -> TaskOutbox:
    dto_fields = {"task_name": "demo_task", "business_id": "b-1", "payload": {"x": 1}}
    dto_fields.update(overrides)
    dto = CreateTaskOutboxDTO(**dto_fields)
    return await repository.create_task_outbox(session, dto, now=utcnow())


async def test_create_and_fetch_pending(db_session: AsyncSession):
    row = await _create(db_session)
    await db_session.commit()

    pending = await repository.fetch_pending_for_update(db_session, now=utcnow(), limit=10)
    assert [r.id for r in pending] == [row.id]


async def test_pending_filters(db_session: AsyncSession):
    now = utcnow()
    visible = await _create(db_session)
    delayed = await _create(db_session, available_at=now + timedelta(minutes=5))
    expired = await _create(
        db_session, available_at=now - timedelta(minutes=10), expires_at=now - timedelta(minutes=1)
    )
    published = await _create(db_session)
    await db_session.commit()
    async with db_session.begin():
        await repository.mark_published(db_session, published.id, now=now)

    pending = await repository.fetch_pending_for_update(db_session, now=utcnow(), limit=10)
    ids = {r.id for r in pending}
    assert visible.id in ids
    assert delayed.id not in ids
    # 已过期任务仍会被领取（由 relay 负责取消），已投递任务不再领取
    assert expired.id in ids
    assert published.id not in ids


async def test_cancel_guards(db_session: AsyncSession):
    now = utcnow()
    row = await _create(db_session)
    await db_session.commit()

    async with db_session.begin():
        await repository.mark_cancelled(session=db_session, outbox_id=row.id, now=now)
    pending = await repository.fetch_pending_for_update(db_session, now=utcnow(), limit=10)
    assert row.id not in {r.id for r in pending}


async def test_publish_failure_reschedules_then_cancels(db_session: AsyncSession):
    now = utcnow()
    row = await _create(db_session, max_publish_attempts=2)
    await db_session.commit()

    await repository.increment_publish_attempts(db_session, [row.id])
    await repository.record_publish_failure(
        db_session,
        row.id,
        failure={"error_type": "Error", "error_message": "x"},
        next_available_at=now + timedelta(seconds=10),
        cancel=False,
        now=now,
    )
    await db_session.commit()
    await db_session.refresh(row)
    assert row.publish_attempts == 1
    assert row.publish_failure["error_type"] == "Error"
    # MySQL DATETIME 读回为 naive，统一去掉时区比较
    assert row.available_at.replace(tzinfo=None) > now.replace(tzinfo=None) + timedelta(seconds=9)

    await repository.increment_publish_attempts(db_session, [row.id])
    await repository.record_publish_failure(
        db_session,
        row.id,
        failure={"error_type": "Error", "error_message": "x"},
        next_available_at=None,
        cancel=True,
        now=now,
    )
    await db_session.commit()
    await db_session.refresh(row)
    assert row.publish_attempts == 2
    assert row.cancelled_at is not None


async def test_concurrent_claim_no_overlap(db_session, database_test_engine):
    """两个并发事务领取同一批任务：SKIP LOCKED 保证不重叠、总量守恒。"""

    for i in range(6):
        await _create(db_session, business_id=f"b-{i}")
    await db_session.commit()

    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        database_test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def claim() -> list[int]:
        # 模拟 relay 真实领取：同事务内更新，锁随事务提交释放
        async with factory() as session, session.begin():
            rows = await repository.fetch_pending_for_update(session, now=utcnow(), limit=6)
            ids = [r.id for r in rows]
            if ids:
                await session.execute(
                    TaskOutbox.__table__.update()
                    .where(TaskOutbox.id.in_(ids))
                    .values(available_at=utcnow() + timedelta(hours=1))
                )
            return ids

    first, second = await asyncio.gather(claim(), claim())
    assert not (set(first) & set(second))
    assert len(first) + len(second) == 6

    total = (await db_session.execute(select(TaskOutbox.id))).scalars().all()
    assert set(first) | set(second) == set(total)
