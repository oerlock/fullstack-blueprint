"""缓存客户端管理器。"""

import logging

from backend.infrastructure.cache.redis.client import RedisClient
from backend.infrastructure.cache.redis.config import RedisSettings

logger = logging.getLogger(__name__)


class CacheClients:
    """统一管理缓存客户端的构建、自检与释放。"""

    def __init__(self, redis_settings: RedisSettings) -> None:
        self._redis_settings = redis_settings
        self._redis: RedisClient | None = None

    @property
    def redis(self) -> RedisClient:
        if self._redis is None:
            self._redis = RedisClient(self._redis_settings)
        return self._redis

    def require_redis(self) -> RedisClient:
        return self.redis

    async def open_all(self) -> None:
        try:
            await self.redis.open()
        except Exception:
            if self._redis_settings.required:
                raise
            logger.exception(
                "Redis is unavailable; application will start in degraded mode"
            )

    async def close_all(self) -> None:
        if self._redis is not None:
            await self._redis.close()
