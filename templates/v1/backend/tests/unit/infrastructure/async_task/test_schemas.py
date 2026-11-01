"""TasksSettings 单元测试。"""

from backend.infrastructure.async_task.schemas import OutboxRelaySettings, TasksSettings
from backend.infrastructure.cache.redis.config import RedisSettings


def test_default_values():
    tasks = TasksSettings()
    assert tasks.redis is None
    assert tasks.queue_name == "async_task"
    assert tasks.consumer_group == "async_task_group"
    assert tasks.max_retry_count == 3
    assert tasks.relay == OutboxRelaySettings()


def test_resolve_redis_fallback_to_cache():
    fallback = RedisSettings()
    tasks = TasksSettings()
    assert tasks.resolve_redis(fallback) is fallback


def test_resolve_redis_explicit_config_wins():
    explicit = RedisSettings(host="10.0.0.1")
    tasks = TasksSettings(redis=explicit)
    assert tasks.resolve_redis(RedisSettings()) is explicit
