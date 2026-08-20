"""Middleware chain configuration."""

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID and log request duration."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000

        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} "
            f"[{elapsed:.1f}ms] req={request_id}"
        )
        return response


class ExceptionFilterMiddleware(BaseHTTPMiddleware):
    """Catch unexpected errors in ASGI middleware layer and convert to JSON."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(f"ASGI-level error: {exc}")
            return Response(
                content='{"code":500,"msg":"Internal Server Error","data":null}',
                media_type="application/json",
                status_code=500,
            )


def register_middleware(app: FastAPI) -> None:
    """Register all middleware on the app."""
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Exception filter (outermost)
    app.add_middleware(ExceptionFilterMiddleware)
    # Request context
    app.add_middleware(RequestContextMiddleware)
