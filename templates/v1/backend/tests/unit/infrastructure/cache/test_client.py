"""RedisClient / CacheClients 单元测试。"""

from unittest import mock

import pytest

from backend.infrastructure.cache.clients import CacheClients
from backend.infrastructure.cache.redis.client import RedisClient
from backend.infrastructure.cache.redis.config import RedisSettings


@pytest.fixture
def redis_client() -> RedisClient:
    return RedisClient(RedisSettings())


def test_build_client_passes_settings(redis_client):
    with mock.patch(
        "backend.infrastructure.cache.redis.client.Redis"
    ) as redis_cls:
        client = redis_client._build_client()

    assert client is redis_cls.return_value
    _, kwargs = redis_cls.call_args
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 6382
    assert kwargs["db"] == 0
    assert kwargs["decode_responses"] is True
    assert kwargs["max_connections"] == 10
    assert kwargs["socket_timeout"] == 3.0
    assert kwargs["health_check_interval"] == 30


async def test_different_loops_get_different_clients(redis_client):
    first = mock.Mock()
    second = mock.Mock()
    builds = iter([first, second])
    loop1, loop2 = object(), object()
    loops = iter([loop1, loop1, loop2])  # loop1 两次触发复用

    def fake_get_running_loop():
        return next(loops)

    with mock.patch(
        "backend.infrastructure.cache.redis.client.asyncio.get_running_loop",
        side_effect=fake_get_running_loop,
    ), mock.patch.object(
        redis_client, "_build_client", side_effect=lambda: next(builds)
    ):
        assert await redis_client.get_client() is first
        assert await redis_client.get_client() is first  # 同 loop 复用
        assert await redis_client.get_client() is second


async def test_close_closes_all_clients(redis_client):
    first = mock.AsyncMock()
    second = mock.AsyncMock()
    redis_client._loop_clients = {object(): first, object(): second}

    await redis_client.close()

    first.aclose.assert_awaited_once()
    second.aclose.assert_awaited_once()
    assert redis_client._loop_clients == {}


def make_clients(required: bool) -> CacheClients:
    clients = CacheClients(RedisSettings(required=required))
    clients._redis = mock.Mock()
    clients._redis.open.side_effect = ConnectionError("down")
    return clients


async def test_open_all_degrades_when_not_required():
    await make_clients(required=False).open_all()  # 不抛出，降级


async def test_open_all_raises_when_required():
    with pytest.raises(ConnectionError):
        await make_clients(required=True).open_all()
