"""全局异常处理器。"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.errors.base import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """注册统一异常处理器。"""

    @app.exception_handler(AppError)
    async def app_error_handler(
            request: Request,
            exc: AppError,
    ) -> JSONResponse:
        metadata = (exc.metadata or {}).copy()
        headers: dict | None = metadata.pop("headers", None)
        metadata.pop("info", None)

        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "code": exc.code,
                "message": exc.message,
                "metadata": metadata or None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
            request: Request,
            exc: RequestValidationError,
    ) -> JSONResponse:
        errors: list[dict[str, Any]] = [
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]

        return JSONResponse(
            status_code=422,
            content={
                "code": 422000,
                "message": "Request validation failed",
                "metadata": {"errors": errors},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
            request: Request,
            exc: StarletteHTTPException,
    ) -> JSONResponse:
        message = (
            exc.detail
            if isinstance(exc.detail, str)
            else "HTTP error"
        )

        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "code": exc.status_code * 1000,
                "message": message,
                "metadata": None,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
            request: Request,
            exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception: %s %s",
            request.method,
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__),
        )

        return JSONResponse(
            status_code=500,
            content={
                "code": 500001,
                "message": "Internal Server Error",
                "metadata": None,
            },
        )
