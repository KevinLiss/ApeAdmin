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

from src.core.deps import get_current_user, get_user_permissions
from src.core.exceptions import success_response, AppException
from src.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.manager import mcp_manager
from src.mcp.routes import _write_audit_log
from src.models import User

router = APIRouter(prefix="/mcp/sse", tags=["MCP SSE 传输"])

# ---------------------------------------------------------------------------
# Short-lived ticket auth (avoids JWT in URL / access logs)
# ---------------------------------------------------------------------------

TICKET_TTL_SECONDS = 30
TOOL_CALL_TIMEOUT = 30  # seconds; guards against hung plugin handlers

# ticket -> {"user_id": int, "expires_at": float}
_tickets: dict[str, dict[str, Any]] = {}


def _create_ticket(user: User) -> str:
    ticket = secrets.token_urlsafe(24)
    # Prune expired tickets opportunistically
    now = time.time()
    for k in [k for k, v in _tickets.items() if v["expires_at"] < now]:
        _tickets.pop(k, None)
    _tickets[ticket] = {"user_id": user.id, "expires_at": now + TICKET_TTL_SECONDS}
    return ticket


def _consume_ticket(ticket: str) -> int | None:
    """Validate and remove a ticket; return user_id if valid."""
    entry = _tickets.pop(ticket, None)
    if not entry or entry["expires_at"] < time.time():
        return None
    return entry["user_id"]


@router.post("/ticket")
async def create_sse_ticket(
    user: Annotated[User, Depends(get_current_user)],
):
    """Exchange a valid JWT for a one-time, 30s SSE connection ticket.

    Clients use the ticket in the SSE URL instead of the raw JWT so the
    long-lived token never appears in access logs.
    """
    return success_response(data={"ticket": _create_ticket(user), "expires_in": TICKET_TTL_SECONDS})


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
        user_id = _consume_ticket(ticket)
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
    user_perms = get_user_permissions(user) if user else set()

    async def send_result(result: Any, rpc_id: int | str | None = body.id) -> None:
        await session.send({
            "jsonrpc": "2.0",
            "result": result,
            "id": rpc_id,
        })

    async def send_error(code: int, message: str, rpc_id: int | str | None = body.id) -> None:
        await session.send({
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": rpc_id,
        })

    method = body.method

    try:
        # ---- initialize ----
        if method == "initialize":
            session.initialized = True
            session.client_info = body.params.get("clientInfo", {})
            await send_result({
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"listChanged": True},
                    "prompts": {"listChanged": True},
                },
                "serverInfo": {
                    "name": "ApeAdmin MCP Server",
                    "version": "0.1.0",
                },
            })

        # ---- tools/list ----
        elif method == "tools/list":
            tools = mcp_manager.list_tools(user_perms)
            await send_result({
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema,
                        "category": t.category,
                    }
                    for t in tools
                ]
            })

        # ---- tools/call ----
        elif method == "tools/call":
            tool_name = body.params.get("name")
            arguments = body.params.get("arguments", {})

            if not tool_name:
                await send_error(-32602, "Missing 'name' in params")
                return {"status": "ok"}

            # RBAC check
            if "mcp:tools:call" not in user_perms and "*" not in user_perms:
                await send_error(-32603, "Permission denied: mcp:tools:call")
                return {"status": "ok"}

            available = mcp_manager.list_tools(user_perms)
            if tool_name not in {t.name for t in available}:
                await send_error(-32602, f"Tool not found: {tool_name}")
                return {"status": "ok"}

            try:
                result = await asyncio.wait_for(
                    mcp_manager.call_tool(tool_name, arguments),
                    timeout=TOOL_CALL_TIMEOUT,
                )
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, result)
                await send_result({
                    "content": [{"type": "text", "text": str(result)}],
                })
            except asyncio.TimeoutError:
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, status="failed")
                await send_error(-32603, f"Tool execution timed out after {TOOL_CALL_TIMEOUT}s: {tool_name}")
            except Exception as exc:
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, status="failed")
                await send_error(-32603, f"Tool execution failed: {exc}")

        # ---- resources/list ----
        elif method == "resources/list":
            resources = mcp_manager.list_resources()
            await send_result({
                "resources": [
                    {
                        "uri": r.uri,
                        "name": r.name,
                        "description": r.description,
                        "mimeType": r.mime_type,
                    }
                    for r in resources
                ]
            })

        # ---- resources/read ----
        elif method == "resources/read":
            uri = body.params.get("uri")
            if not uri:
                await send_error(-32602, "Missing 'uri' in params")
                return {"status": "ok"}

            try:
                content = await mcp_manager.read_resource(uri)
                if user:
                    await _write_audit_log(db, "resource", uri, user, result=content[:2000])
                await send_result({
                    "contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]
                })
            except ValueError as exc:
                await send_error(-32602, str(exc))

        # ---- prompts/list ----
        elif method == "prompts/list":
            prompts = mcp_manager.list_prompts()
            await send_result({
                "prompts": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "arguments": [{"name": a} for a in p.arguments],
                    }
                    for p in prompts
                ]
            })

        # ---- prompts/get (MCP standard) / prompts/render (legacy alias) ----
        elif method in ("prompts/get", "prompts/render"):
            prompt_name = body.params.get("name")
            prompt_args = body.params.get("arguments", {})
            if not prompt_name:
                await send_error(-32602, "Missing 'name' in params")
                return {"status": "ok"}

            try:
                rendered = mcp_manager.render_prompt(prompt_name, **prompt_args)
                if user:
                    await _write_audit_log(db, "prompt", prompt_name, user, prompt_args, rendered)
                await send_result({
                    "content": [{"type": "text", "text": rendered}]
                })
            except ValueError as exc:
                await send_error(-32602, str(exc))

        # ---- ping ----
        elif method == "ping":
            await send_result({})

        else:
            await send_error(-32601, f"Method not found: {method}")

    except Exception as exc:
        logger.error(f"MCP SSE error: {exc}")
        await send_error(-32603, f"Internal error: {exc}")

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------

def register_sse_routes(app: FastAPI) -> None:
    """Mount the MCP SSE routes on the app."""
    from src.core.config import settings

    app.include_router(router, prefix=settings.API_PREFIX)
