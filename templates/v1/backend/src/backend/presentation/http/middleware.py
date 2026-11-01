"""全局 HTTP 中间件注册。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import CorsSettings


def register_middlewares(app: FastAPI, cors_settings: CorsSettings) -> None:
    if not cors_settings.enabled:
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_origin_regex=cors_settings.allow_origin_regex,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers,
        allow_credentials=cors_settings.allow_credentials,
        expose_headers=cors_settings.expose_headers,
        max_age=cors_settings.max_age,
    )
