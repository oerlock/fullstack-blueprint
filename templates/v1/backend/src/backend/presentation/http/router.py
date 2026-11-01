"""HTTP 路由统一装配：业务路由注册、前缀与版本、健康检查。"""

import asyncio

from fastapi import APIRouter, Response

from backend.config import settings

API_PREFIX = "/api/v1"

READINESS_TIMEOUT_SECONDS = 3


async def _check_cache() -> bool:
    try:
        return await asyncio.wait_for(
            settings.cache_clients.require_redis().ping(),
            timeout=READINESS_TIMEOUT_SECONDS,
        )
    except Exception:
        return False


def create_health_router() -> APIRouter:
    health_router = APIRouter(tags=["health"])

    @health_router.get("/ping")
    async def health_check():
        return {"message": "pong"}

    @health_router.get("/ready")
    async def readiness_check(response: Response):
        dependencies: dict[str, str] = {}
        dependencies["cache"] = "ok" if await _check_cache() else "unavailable"
        overall_status = "ok"
        if "unavailable" in dependencies.values():
            response.status_code = 503
            overall_status = "unavailable" if response.status_code == 503 else "degraded"
        return {"status": overall_status, "dependencies": dependencies}

    return health_router


def create_api_router() -> APIRouter:
    """注册业务路由，业务路由由各自 app 的 routes.py 维护。"""

    api_router = APIRouter()
    # from backend.apps.<app>.routes import router as <app>_router
    # api_router.include_router(<app>_router)
    return api_router
