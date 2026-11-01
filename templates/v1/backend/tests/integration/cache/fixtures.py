"""真实 Redis 集成测试夹具（需 --with-redis，参考 slash_space）。"""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from backend.config.settings import settings
from backend.infrastructure.cache.keys import build_cache_key
from backend.infrastructure.cache.redis.client import RedisClient


@pytest.fixture(scope="session")
def redis_test_run_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def redis_test_key_prefix(redis_test_run_id: str) -> str:
    redis_settings = settings.redis
    return build_cache_key(
        redis_settings.key_prefix,
        "test",
        "test_run",
        redis_test_run_id,
    )


@pytest.fixture(scope="module")
def _redis_wrapper() -> RedisClient:
    # 连接测试专用 DB（REDIS__TEST_DATABASE，经 test_app.env 配置），与本地开发数据隔离
    test_settings = settings.redis.model_copy(
        update={"database": settings.redis.test_database}
    )
    return RedisClient(test_settings)


@pytest_asyncio.fixture
async def real_redis(_redis_wrapper: RedisClient, redis_test_key_prefix: str) -> AsyncGenerator[Redis, None]:
    client = await _redis_wrapper.get_client()
    await client.ping()
    try:
        yield client
    finally:
        keys: list[str] = []
        async for key in client.scan_iter(match=f"{redis_test_key_prefix}:*", count=100):
            keys.append(key)
            if len(keys) >= 100:
                await client.unlink(*keys)
                keys.clear()
        if keys:
            await client.unlink(*keys)
        await _redis_wrapper.close()
