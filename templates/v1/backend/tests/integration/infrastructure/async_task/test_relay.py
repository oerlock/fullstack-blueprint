"""投递服务与执行记录集成测试（--with-database）。"""

from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.execution.models import TaskExecution
from backend.infrastructure.async_task.execution.schemas import TaskExecutionStatus
from backend.infrastructure.async_task.outbox import repository as outbox_repo
from backend.infrastructure.async_task.outbox.dto import CreateTaskOutboxDTO
from backend.infrastructure.async_task.outbox.models import TaskOutbox
from backend.infrastructure.async_task.relay.service import TaskRelayService
from backend.infrastructure.async_task.schemas import OutboxRelaySettings
from backend.infrastructure.async_task.taskiq.execution import task_execution

pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_database,
    pytest.mark.asyncio(loop_scope="session"),
]


class FakePublisher:
    def __init__(self, fail_times: int = 0):
        self.fail_times = fail_times
        self.calls: list[tuple[str, dict, int]] = []

    async def publish(self, task_name: str, payload: dict, *, outbox_id: int) -> None:
        if self.fail_times > 0:
            self.fail_times -= 1
            raise ConnectionError("broker down")
        self.calls.append((task_name, payload, outbox_id))


@pytest.fixture
def relay_factory(db_session, database_test_engine):
    async def make(publisher, **settings_overrides):
        factory = async_sessionmaker(
            database_test_engine, class_=AsyncSession, expire_on_commit=False
        )
        relay = OutboxRelaySettings(**settings_overrides)
        return TaskRelayService(factory, publisher, relay_settings=relay, jitter=lambda low, high: 0.0)

    return make


async def _create(db_session: AsyncSession, **overrides) -> TaskOutbox:
    fields = {"task_name": "demo_task", "business_id": "b-1", "payload": {"x": 1}}
    fields.update(overrides)
    row = await outbox_repo.create_task_outbox(
        db_session, CreateTaskOutboxDTO(**fields), now=utcnow()
    )
    await db_session.commit()
    return row


async def _reload(db_session: AsyncSession, outbox_id: int) -> TaskOutbox:
    await db_session.rollback()
    # 丢弃 identity map 缓存，读取其他事务提交后的最新状态
    db_session.expire_all()
    return await db_session.get(TaskOutbox, outbox_id)


async def test_dispatch_publishes_and_marks(db_session, relay_factory):
    row = await _create(db_session)
    publisher = FakePublisher()
    service = await relay_factory(publisher)

    published = await service.dispatch_tick()

    assert published == 1
    assert publisher.calls == [("demo_task", {"x": 1}, row.id)]
    fresh = await _reload(db_session, row.id)
    assert fresh.published_at is not None
    assert fresh.publish_attempts == 1

    # 已投递任务不再被领取
    assert await service.dispatch_tick() == 0
    assert len(publisher.calls) == 1


async def test_dispatch_failure_reschedules_with_backoff(db_session, relay_factory):
    row = await _create(db_session, max_publish_attempts=5)
    publisher = FakePublisher(fail_times=1)
    service = await relay_factory(publisher, retry_base_delay_seconds=2.0)
    before = utcnow()

    assert await service.dispatch_tick() == 0
    fresh = await _reload(db_session, row.id)
    assert fresh.published_at is None
    assert fresh.publish_attempts == 1
    assert fresh.publish_failure["error_type"] == "ConnectionError"
    # MySQL DATETIME 读回为 naive，统一去掉时区比较
    assert fresh.available_at.replace(tzinfo=None) >= before.replace(tzinfo=None) + timedelta(seconds=2)

    # 退避未到，本轮不重复领取
    assert await service.dispatch_tick() == 0


async def test_dispatch_retry_after_backoff_succeeds(db_session, relay_factory):
    row = await _create(db_session)
    publisher = FakePublisher(fail_times=1)
    service = await relay_factory(publisher)

    assert await service.dispatch_tick() == 0
    # 将 available_at 拨回当下，模拟退避时间已过
    async with db_session.begin():
        await db_session.execute(
            TaskOutbox.__table__.update()
            .where(TaskOutbox.id == row.id)
            .values(available_at=utcnow() - timedelta(seconds=1))
        )
    assert await service.dispatch_tick() == 1
    fresh = await _reload(db_session, row.id)
    assert fresh.published_at is not None
    assert fresh.publish_attempts == 2


async def test_dispatch_exhausted_cancels(db_session, relay_factory):
    row = await _create(db_session, max_publish_attempts=1)
    publisher = FakePublisher(fail_times=5)
    service = await relay_factory(publisher)

    assert await service.dispatch_tick() == 0
    fresh = await _reload(db_session, row.id)
    assert fresh.cancelled_at is not None
    assert fresh.publish_attempts == 1


async def test_dispatch_expired_cancels_without_publish(db_session, relay_factory):
    now = utcnow()
    row = await _create(
        db_session, available_at=now - timedelta(minutes=10), expires_at=now - timedelta(minutes=1)
    )
    publisher = FakePublisher()
    service = await relay_factory(publisher)

    assert await service.dispatch_tick() == 0
    assert publisher.calls == []
    fresh = await _reload(db_session, row.id)
    assert fresh.cancelled_at is not None
    assert fresh.publish_attempts == 0


async def test_execution_decorator_records_attempts(db_session, database_test_engine):
    row = await _create(db_session)
    factory = async_sessionmaker(database_test_engine, class_=AsyncSession, expire_on_commit=False)
    calls = {"n": 0}

    @task_execution(session_factory=factory)
    async def demo_task(*, payload: dict):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("first fails")
        return {"ok": True}

    with pytest.raises(RuntimeError):
        await demo_task(payload={"x": 1}, outbox_id=row.id)
    assert await demo_task(payload={"x": 1}, outbox_id=row.id) == {"ok": True}

    await db_session.rollback()
    rows = (
        (
            await db_session.execute(
                TaskExecution.__table__.select().where(TaskExecution.outbox_id == row.id)
            )
        )
        .mappings()
        .all()
    )
    assert [(r["attempt"], r["status"]) for r in rows] == [
        (1, TaskExecutionStatus.FAILED.value),
        (2, TaskExecutionStatus.COMPLETED.value),
    ]
    assert rows[0]["result"]["error_type"] == "RuntimeError"
    assert rows[1]["result"] == {"ok": True}


async def test_pipeline_with_inmemory_broker(db_session, database_test_engine):
    """全链路：outbox → relay → InMemoryBroker（同步执行）→ execution 记录。"""

    from taskiq.brokers.inmemory_broker import InMemoryBroker

    from backend.infrastructure.async_task.taskiq.publisher import TaskiqPublisher

    broker = InMemoryBroker(await_inplace=True)
    executed: list[dict] = []

    @broker.task(task_name="pipeline_demo")
    @task_execution(
        session_factory=async_sessionmaker(
            database_test_engine, class_=AsyncSession, expire_on_commit=False
        )
    )
    async def pipeline_demo(*, payload: dict):
        executed.append(payload)
        return {"echo": payload}

    row = await _create(db_session, task_name="pipeline_demo")
    relay = TaskRelayService(
        async_sessionmaker(database_test_engine, class_=AsyncSession, expire_on_commit=False),
        TaskiqPublisher(broker),
    )
    published = await relay.dispatch_tick()

    assert published == 1
    assert executed == [{"x": 1}]
    fresh = await _reload(db_session, row.id)
    assert fresh.published_at is not None
    records = (
        (
            await db_session.execute(
                TaskExecution.__table__.select().where(TaskExecution.outbox_id == row.id)
            )
        )
        .mappings()
        .all()
    )
    assert len(records) == 1
    assert records[0]["status"] == TaskExecutionStatus.COMPLETED.value
    assert records[0]["result"] == {"echo": {"x": 1}}
