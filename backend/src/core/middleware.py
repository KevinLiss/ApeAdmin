"""Middleware chain configuration."""

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import settings
from src.core.security import decode_token
from src.db import SessionLocal
from src.models.log import SysLog


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


class OperationLogMiddleware(BaseHTTPMiddleware):
    """Record API operations to sys_log table.

    Skips /logs endpoints and non-API paths to avoid noise and infinite loops.
    """

    SKIP_PREFIXES = ("/api/v1/logs",)

    async def dispatch(self, request: Request, call_next):
        # Skip log endpoints and non-API requests
        path = request.url.path
        if not path.startswith("/api/v1/") or any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # Extract user info from Bearer token (lightweight, no DB lookup)
        user_id: int | None = None
        username: str | None = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = int(payload.get("sub", 0)) or None
                username = payload.get("username")

        # Capture query params (skip body to avoid streaming complexity)
        params = None
        if request.query_params:
            params = str(request.query_params)[:2000]

        # Get client IP
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "")[:500]

        # Write log entry (fire-and-forget with error suppression)
        try:
            async with SessionLocal() as db:
                log_entry = SysLog(
                    user_id=user_id,
                    username=username,
                    method=request.method,
                    path=path,
                    params=params,
                    status_code=response.status_code,
                    duration_ms=elapsed_ms,
                    ip=client_ip,
                    user_agent=user_agent,
                    error=None if response.status_code < 500 else f"HTTP {response.status_code}",
                )
                db.add(log_entry)
                await db.commit()
        except Exception as exc:
            logger.warning(f"Failed to write operation log: {exc}")

        return response


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
    # Operation log
    app.add_middleware(OperationLogMiddleware)
    # Request context
    app.add_middleware(RequestContextMiddleware)
