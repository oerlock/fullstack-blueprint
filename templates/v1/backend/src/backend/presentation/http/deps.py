"""全局 HTTP 依赖。"""

from backend.infrastructure.cache.deps import DepCache, get_cache_dep

__all__ = [
    "DepCache",
    "get_cache_dep",
]
