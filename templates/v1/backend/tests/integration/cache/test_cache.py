"""缓存基础设施集成测试（需要本地 docker Redis，127.0.0.1:6382，--with-redis 门控）。"""

import pytest

from backend.infrastructure.cache.redis.client import RedisClient
from backend.infrastructure.cache.redis.config import RedisSettings

pytestmark = pytest.mark.requires_redis


async def test_set_get_ping(real_redis, redis_test_key_prefix: str):
    key = f"{redis_test_key_prefix}:set_get"
    assert await real_redis.set(key, "1", ex=60) is True
    assert await real_redis.get(key) == "1"
    assert await real_redis.delete(key) == 1
    assert await real_redis.get(key) is None


async def test_open_close():
    client = RedisClient(RedisSettings())
    await client.open()
    await client.close()
    assert client._loop_clients == {}
