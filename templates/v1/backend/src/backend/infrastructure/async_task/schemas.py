"""异步任务总配置，环境变量前缀 TASKS__。"""

from pydantic import BaseModel, Field

from backend.infrastructure.cache.redis.config import RedisSettings


class OutboxRelaySettings(BaseModel):
    """Outbox 投递轮询参数。"""

    poll_interval_seconds: int = Field(5, ge=1)
    batch_size: int = Field(50, ge=1)
    max_rounds_per_tick: int = Field(10, ge=1)
    retry_base_delay_seconds: float = Field(1.0, gt=0)
    retry_max_delay_seconds: float = Field(60.0, gt=0)


class TasksSettings(BaseModel):
    """异步任务配置，环境变量前缀 TASKS__。"""

    # Broker 使用的 Redis 连接；未配置时回退到 cache 的 REDIS__* 配置（同一实例）
    redis: RedisSettings | None = None
    queue_name: str = "async_task"
    consumer_group: str = "async_task_group"
    max_retry_count: int = Field(3, ge=0)
    relay: OutboxRelaySettings = Field(default_factory=OutboxRelaySettings)

    def resolve_redis(self, fallback: RedisSettings) -> RedisSettings:
        return self.redis if self.redis is not None else fallback
