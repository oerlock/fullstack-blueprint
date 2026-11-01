"""缓存依赖注入。"""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from backend.config import settings
from backend.infrastructure.cache.clients import CacheClients


async def get_cache_dep() -> Redis:
    cache_clients: CacheClients = settings.cache_clients
    return await cache_clients.require_redis().get_client()


type DepCache = Annotated[Redis, Depends(get_cache_dep)]
