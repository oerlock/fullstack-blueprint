"""按事件循环隔离的 Redis 客户端包装。"""

import asyncio

from redis.asyncio import Redis

from backend.infrastructure.cache.redis.config import RedisSettings


class RedisClient:
    """包装 redis.asyncio.Redis，每个事件循环持有独立客户端。

    测试中不同用例可能运行在不同事件循环，跨循环复用连接会报错，
    因此按 loop 隔离客户端实例。
    """

    def __init__(self, settings: RedisSettings) -> None:
        self.settings = settings
        self._loop_clients: dict[asyncio.AbstractEventLoop, Redis] = {}

    def _build_client(self) -> Redis:
        password = (
            self.settings.password.get_secret_value()
            if self.settings.password
            else None
        )
        return Redis(
            host=self.settings.host,
            port=self.settings.port,
            db=self.settings.database,
            username=self.settings.username,
            password=password,
            ssl=self.settings.ssl,
            decode_responses=True,
            max_connections=self.settings.max_connections,
            socket_connect_timeout=self.settings.socket_connect_timeout,
            socket_timeout=self.settings.socket_timeout,
            health_check_interval=self.settings.health_check_interval,
        )

    async def get_client(self) -> Redis:
        loop = asyncio.get_running_loop()
        if loop not in self._loop_clients:
            self._loop_clients[loop] = self._build_client()
        return self._loop_clients[loop]

    async def open(self) -> None:
        client = await self.get_client()
        await client.ping()

    async def ping(self) -> bool:
        client = await self.get_client()
        return bool(await client.ping())

    async def close(self) -> None:
        for loop in list(self._loop_clients):
            client = self._loop_clients.pop(loop, None)
            if client is not None:
                await client.aclose()
