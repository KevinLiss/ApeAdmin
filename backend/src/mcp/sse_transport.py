"""MCP SSE transport: implements the MCP protocol over Server-Sent Events.

This module provides a standard MCP-compatible SSE endpoint that can be
connected to by any MCP client (e.g., Claude Desktop, Cursor, etc.).

Protocol flow:
1. Client obtains a short-lived ticket: POST /mcp/sse/ticket (JWT auth)
2. Client connects to GET /mcp/sse?ticket=xxx → server returns SSE stream
3. Client sends JSON-RPC messages via POST /mcp/sse/messages?session_id=xxx
4. Server processes: initialize → tools/list → tools/call
5. Responses are pushed back via the SSE stream

Auth notes:
- Tickets are one-time, expire in 30s, and avoid leaking JWTs into
  Nginx access logs via URL query strings.
- JWT ``sub`` carries the **user id** (not username).
"""

import asyncio
import json
import secrets
import time
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, Query, Request
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from src.core.deps import get_current_user
from src.core.exceptions import success_response
from src.core.redis_client import kv_delete, kv_get, kv_set
from src.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.dispatch import dispatch_jsonrpc
from src.models import User

router = APIRouter(prefix="/mcp/sse", tags=["MCP SSE 传输"])

# ---------------------------------------------------------------------------
# Short-lived ticket auth (avoids JWT in URL / access logs)
# ---------------------------------------------------------------------------

TICKET_TTL_SECONDS = 30
TOOL_CALL_TIMEOUT = 30  # seconds; guards against hung plugin handlers

# Tickets live in Redis (namespace "mcpticket", TTL 30s) when available so
# multi-worker deployments can verify tickets issued by another worker.
# The in-memory fallback (inside redis_client) mirrors the historical dict.
_SPACE = "mcpticket"


@router.post("/ticket")
async def create_sse_ticket(
    user: Annotated[User, Depends(get_current_user)],
):
    """Exchange a valid JWT for a one-time, 30s SSE connection ticket.

    Clients use the ticket in the SSE URL instead of the raw JWT so the
    long-lived token never appears in access logs.
    """
    ticket = secrets.token_urlsafe(24)
    await kv_set(_SPACE, ticket, str(user.id), ttl=TICKET_TTL_SECONDS)
    return success_response(data={"ticket": ticket, "expires_in": TICKET_TTL_SECONDS})


async def consume_ticket(ticket: str) -> int | None:
    """Validate and remove a ticket; return user_id if valid."""
    raw = await kv_get(_SPACE, ticket)
    if raw is None:
        return None
    await kv_delete(_SPACE, ticket)  # one-time use
    try:
        return int(raw)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

class SseSession:
    """An SSE session with a message queue for the connected client."""

    def __init__(self, session_id: str, user: User | None = None):
        self.session_id = session_id
        self.user = user
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.initialized = False
        self.client_info: dict[str, Any] = {}

    async def send(self, data: dict[str, Any]) -> None:
        await self.queue.put(json.dumps(data, ensure_ascii=False))

    async def close(self) -> None:
        await self.queue.put("__close__")


# In-memory session store (single-process mode)
_sessions: dict[str, SseSession] = {}


def _get_or_create_session(session_id: str | None = None, user: User | None = None) -> SseSession:
    sid = session_id or str(uuid.uuid4())
    if sid not in _sessions:
        _sessions[sid] = SseSession(sid, user)
    return _sessions[sid]


# ---------------------------------------------------------------------------
# SSE endpoint (GET /mcp/sse)
# ---------------------------------------------------------------------------

@router.get("")
async def mcp_sse_endpoint(
    request: Request,
    ticket: str | None = Query(None, description="One-time ticket from POST /mcp/sse/ticket (preferred)"),
    token: str | None = Query(None, description="JWT token (legacy fallback, discouraged)"),
):
    """Establish an SSE connection for MCP JSON-RPC communication.

    The client connects here and receives a session ID. Messages are
    exchanged via POST /mcp/sse/messages?session_id=xxx.
    """
    # Resolve user_id from ticket (preferred) or JWT fallback
    user_id: int | None = None
    if ticket:
        user_id = await consume_ticket(ticket)
        if user_id is None:
            return StreamingResponse(
                iter(["event: error\ndata: {\"message\": \"invalid or expired ticket\"}\n\n"]),
                media_type="text/event-stream",
                status_code=401,
            )
    elif token:
        try:
            from src.core.security import decode_token

            payload = decode_token(token)
            if payload and payload.get("sub"):
                # JWT ``sub`` stores the user **id** (see auth router)
                user_id = int(payload["sub"])
        except Exception:
            user_id = None

    user = None
    if user_id is not None:
        try:
            from src.crud import crud_user
            from src.db import SessionLocal

            async with SessionLocal() as db:
                user = await crud_user.get(db, user_id)
        except Exception:
            user = None

    session_id = str(uuid.uuid4())
    session = _get_or_create_session(session_id, user)

    async def event_generator():
        try:
            # Send endpoint info
            yield f"event: endpoint\ndata: /mcp/sse/messages?session_id={session_id}\n\n"
            logger.info(f"MCP SSE session started: {session_id}")

            while True:
                try:
                    msg = await asyncio.wait_for(session.queue.get(), timeout=30.0)
                    if msg == "__close__":
                        break
                    yield f"event: message\ndata: {msg}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield f": ping\n\n"
        except asyncio.CancelledError:
            logger.info(f"MCP SSE session cancelled: {session_id}")
        finally:
            _sessions.pop(session_id, None)
            logger.info(f"MCP SSE session closed: {session_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ---------------------------------------------------------------------------
# Message endpoint (POST /mcp/sse/messages)
# ---------------------------------------------------------------------------

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = {}
    id: int | str | None = None


@router.post("/messages")
async def mcp_sse_message(
    body: JsonRpcRequest,
    session_id: str = Query(...),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Handle a JSON-RPC message from the MCP client.

    Supported methods:
    - initialize: handshake
    - tools/list: list available tools
    - tools/call: call a tool
    - resources/list: list resources
    - resources/read: read a resource
    - prompts/list: list prompts
    - prompts/get: get a prompt (MCP standard; prompts/render kept as alias)
    """
    session = _sessions.get(session_id)
    if not session:
        return {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Invalid session"}, "id": body.id}

    user = session.user

    # Shared JSON-RPC dispatcher (identical logic to Streamable HTTP):
    # RBAC checks, audit logging and tool timeout live in one place.
    response = await dispatch_jsonrpc(
        body.method,
        body.params,
        body.id,
        user=user,
        db=db,
        session=session,
    )
    await session.send(response)

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------

def register_sse_routes(app: FastAPI) -> None:
    """Mount the MCP SSE routes on the app."""
    from src.core.config import settings

    app.include_router(router, prefix=settings.API_PREFIX)
