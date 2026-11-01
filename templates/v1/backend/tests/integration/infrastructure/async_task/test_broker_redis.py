"""RedisStreamBroker 真实收发集成测试（--with-redis）。

每次运行使用唯一的 queue / consumer group，结束后清理，避免污染本地数据。
"""


import pytest
from redis.asyncio import Redis

from backend.config.settings import settings
from backend.infrastructure.async_task.schemas import TasksSettings
from backend.infrastructure.async_task.taskiq.broker import build_broker, build_redis_url
from backend.infrastructure.async_task.taskiq.publisher import TaskiqPublisher

pytestmark = [pytest.mark.integration, pytest.mark.requires_redis]


@pytest.fixture
def stream_broker(redis_test_run_id: str):
    tasks = TasksSettings(
        queue_name=f"test_async_task:{redis_test_run_id}",
        consumer_group=f"test_group:{redis_test_run_id}",
    )
    redis_settings = settings.redis.model_copy(update={"database": settings.redis.test_database})
    return build_broker(tasks, redis_settings)


async def test_publish_writes_to_stream(stream_broker):
    await stream_broker.startup()
    try:
        publisher = TaskiqPublisher(stream_broker)
        await publisher.publish("some_task", {"x": 1}, outbox_id=42)
        await publisher.publish("some_task", {"x": 2}, outbox_id=43)
    finally:
        await stream_broker.shutdown()

    client = Redis.from_url(
        build_redis_url(
            settings.redis.model_copy(update={"database": settings.redis.test_database})
        )
    )
    try:
        assert await client.xlen(stream_broker.queue_name) == 2
    finally:
        await client.delete(stream_broker.queue_name)
        await client.aclose()
