"""Outbox 投递服务：领取待投递任务并投递到 Taskiq Broker。"""

import random
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.outbox import repository as outbox_repo
from backend.infrastructure.async_task.outbox.models import TaskOutbox
from backend.infrastructure.async_task.schemas import OutboxRelaySettings
from backend.infrastructure.async_task.taskiq.publisher import TaskPublisher

logger = getLogger(__name__)


def _as_utc(value: datetime) -> datetime:
    """MySQL DATETIME 读回 naive（应用统一 UTC），比较前补时区。"""

    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def compute_backoff_delay(
    attempts: int,
    *,
    base_delay_seconds: float,
    max_delay_seconds: float,
    jitter: Callable[[float, float], float] | None = None,
) -> float:
    """指数退避：min(base * 2^(attempts-1), max)，叠加 [0, 0.5s) 抖动。"""

    raw = min(base_delay_seconds * 2 ** (max(attempts, 1) - 1), max_delay_seconds)
    jitter_fn = jitter or (lambda low, high: random.uniform(low, high))
    return raw + jitter_fn(0.0, min(0.5, raw))


class TaskRelayService:
    """单轮投递：分批领取（SKIP LOCKED）→ 递增尝试 → 投递 → 更新状态。

    领取与状态更新在短事务内完成，不在等待 Broker 响应期间持有行锁。
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        publisher: TaskPublisher,
        *,
        relay_settings: OutboxRelaySettings | None = None,
        now_fn: Callable[[], datetime] | None = None,
        jitter: Callable[[float, float], float] | None = None,
    ):
        self._session_factory = session_factory
        self._publisher = publisher
        self._settings = relay_settings or OutboxRelaySettings()
        self._now_fn = now_fn or utcnow
        self._jitter = jitter

    async def dispatch_tick(self) -> int:
        """执行一轮投递，返回本轮成功投递条数。"""

        published = 0
        for _ in range(self._settings.max_rounds_per_tick):
            claimed = await self._claim_batch()
            if not claimed:
                break
            for row in claimed:
                if await self._publish_one(row):
                    published += 1
        return published

    async def _claim_batch(self) -> list[TaskOutbox]:
        """短事务：领取并递增尝试次数；过期/耗尽的任务直接取消。"""

        now = self._now_fn()
        async with self._session_factory() as session:
            async with session.begin():
                rows = await outbox_repo.fetch_pending_for_update(
                    session, now=now, limit=self._settings.batch_size
                )
                claim_ids: list[int] = []
                for row in rows:
                    expires_at = _as_utc(row.expires_at) if row.expires_at is not None else None
                    expired = expires_at is not None and expires_at <= now
                    exhausted = row.publish_attempts + 1 > row.max_publish_attempts
                    if expired or exhausted:
                        await outbox_repo.mark_cancelled(session, row.id, now=now)
                    else:
                        claim_ids.append(row.id)
                await outbox_repo.increment_publish_attempts(session, claim_ids)
            return [row for row in rows if row.id in claim_ids]

    async def _publish_one(self, row: TaskOutbox) -> bool:
        try:
            await self._publisher.publish(row.task_name, row.payload, outbox_id=row.id)
        except BaseException as exc:
            logger.warning("任务投递失败 outbox_id=%s task_name=%s: %s", row.id, row.task_name, exc)
            now = self._now_fn()
            attempts = row.publish_attempts + 1
            cancel = attempts >= row.max_publish_attempts
            delay = compute_backoff_delay(
                attempts,
                base_delay_seconds=self._settings.retry_base_delay_seconds,
                max_delay_seconds=self._settings.retry_max_delay_seconds,
                jitter=self._jitter,
            )
            async with self._session_factory() as session, session.begin():
                await outbox_repo.record_publish_failure(
                    session,
                    row.id,
                    failure={"error_type": type(exc).__name__, "error_message": str(exc)},
                    next_available_at=None if cancel else now + timedelta(seconds=delay),
                    cancel=cancel,
                    now=now,
                )
            return False

        async with self._session_factory() as session, session.begin():
            await outbox_repo.mark_published(session, row.id, now=self._now_fn())
        return True
