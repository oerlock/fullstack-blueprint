"""Broker 构建。必须通过 get_broker 共享进程级单例：任务注册只作用于装饰时的实例。"""

from taskiq import AsyncBroker
from taskiq.middlewares import SimpleRetryMiddleware
from taskiq_redis import RedisStreamBroker

from backend.config.settings import settings
from backend.infrastructure.async_task.schemas import TasksSettings
from backend.infrastructure.cache.redis.config import RedisSettings


def build_redis_url(redis: RedisSettings) -> str:
    auth = f":{redis.password.get_secret_value()}@" if redis.password else ""
    scheme = "rediss" if redis.ssl else "redis"
    return f"{scheme}://{auth}{redis.host}:{redis.port}/{redis.database}"


def build_broker(tasks: TasksSettings, redis: RedisSettings) -> AsyncBroker:
    broker = RedisStreamBroker(
        url=build_redis_url(redis),
        queue_name=tasks.queue_name,
        consumer_group_name=tasks.consumer_group,
        max_connection_pool_size=redis.max_connections,
        socket_connect_timeout=redis.socket_connect_timeout,
        socket_timeout=redis.socket_timeout,
    ).with_middlewares(
        SimpleRetryMiddleware(default_retry_count=tasks.max_retry_count),
    )
    return broker


_broker: AsyncBroker | None = None


def get_broker() -> AsyncBroker:
    global _broker
    if _broker is None:
        _broker = build_broker(settings.tasks, settings.tasks.resolve_redis(settings.redis))
    return _broker


def reset_broker() -> None:
    """仅供测试：重置进程级单例。"""

    global _broker
    _broker = None
