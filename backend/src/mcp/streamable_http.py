"""MCP Streamable HTTP transport (MCP spec revision 2025-03-26).

Modern single-endpoint transport: the client POSTs JSON-RPC messages to
``/mcp`` and receives either a plain JSON response (this server always
answers synchronously — tool calls have their own 30s timeout) or
``202 Accepted`` for notifications. ``GET /mcp`` opens an optional
server-push SSE stream (keepalive pings; ``listChanged`` notifications
are a future extension), and ``DELETE /mcp`` terminates a session.

Auth notes:
- ``Authorization: Bearer <JWT>`` is the standard header path — nothing
  sensitive rides in URL query strings, and unauthenticated requests are
  rejected by the shared auth dependency (HTTP 401).
- Session: ``initialize`` assigns an ``Mcp-Session-Id`` response header.
  State is minimal (initialized flag + client info); all protocol state
  lives in the shared dispatcher, so stateless clients that skip
  session headers work identically.
"""

import asyncio
import json
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from src.core.deps import get_current_user
from src.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.dispatch import JsonRpcRequest, dispatch_jsonrpc
from src.models import User

router = APIRouter(prefix="/mcp", tags=["MCP Streamable HTTP"])

# Mcp-Session-Id -> {"initialized": bool, "client_info": {...}}
_sessions: dict[str, dict[str, Any]] = {}

# Sessions terminated by DELETE (short-lived tombstones so a racing client
# gets a clean error instead of silent re-initialization)
_closed: set[str] = set()


class _SseCompatSession:
    """Adapter so the shared dispatcher can track initialize state."""

    initialized = False
    client_info: dict[str, Any] = {}

    def __init__(self, state: dict[str, Any]):
        self._state = state

    def _sync(self) -> None:
        self._state["initialized"] = self.initialized
        self._state["client_info"] = self.client_info


async def _resolve_user(auth_user: User | None) -> User | None:
    """The auth dependency has already validated the JWT; pass through."""
    return auth_user


@router.post("")
async def mcp_streamable_http(
    body: JsonRpcRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_user: Annotated[User | None, Depends(get_current_user)] = None,
):
    """Single JSON-RPC endpoint per the 2025-03-26 Streamable HTTP spec."""
    session_id = request.headers.get("Mcp-Session-Id", "")
    if session_id and session_id in _closed:
        return JSONResponse(
            status_code=404,
            content={"jsonrpc": "2.0", "error": {"code": -32000, "message": "Session terminated"}, "id": body.id},
        )

    user = auth_user

    # Notifications (no id) expect no response body — 202 per spec.
    is_notification = body.id is None
    state = _sessions.setdefault(session_id, {"initialized": False, "client_info": {}}) if session_id else {}
    compat = _SseCompatSession(state) if state else None

    response = await dispatch_jsonrpc(
        body.method,
        body.params,
        None if is_notification else body.id,
        user=user,
        db=db,
        session=compat,
    )
    if compat is not None:
        compat._sync()

    headers: dict[str, str] = {}
    if body.method == "initialize":
        session_id = uuid.uuid4().hex
        _sessions[session_id] = {"initialized": True, "client_info": body.params.get("clientInfo", {})}
        headers["Mcp-Session-Id"] = session_id

    if is_notification:
        return Response(status_code=202)

    return JSONResponse(content=response, headers=headers)


@router.get("")
async def mcp_streamable_http_stream(request: Request):
    """Optional server-push SSE stream for a session.

    The current server has no asynchronous notifications to push, so the
    stream only carries keepalive comments; clients that do not need it
    can simply never call GET (per spec this is allowed).
    """
    session_id = request.headers.get("Mcp-Session-Id", "")
    if session_id and session_id in _closed:
        return JSONResponse(status_code=404, content={"message": "Session terminated"})

    async def event_generator():
        try:
            while True:
                await asyncio.sleep(15)
                yield ": ping\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("")
async def mcp_streamable_http_delete(request: Request):
    """Terminate a session (client-driven shutdown per spec)."""
    session_id = request.headers.get("Mcp-Session-Id", "")
    if session_id:
        _sessions.pop(session_id, None)
        _closed.add(session_id)
        if len(_closed) > 4096:  # bound tombstone growth
            for stale in list(_closed)[:2048]:
                _closed.discard(stale)
        logger.info(f"MCP streamable session terminated: {session_id[:8]}…")
    return Response(status_code=204)


def register_streamable_routes(app) -> None:
    """Mount the MCP Streamable HTTP routes on the app."""
    from src.core.config import settings

    app.include_router(router, prefix=settings.API_PREFIX)
