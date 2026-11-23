"""Protocol-agnostic MCP JSON-RPC dispatcher.

Shared by both transports (SSE and Streamable HTTP) so tool listing,
RBAC checks, audit logging and timeouts behave identically regardless
of how the client connects.

A dispatcher receives one JSON-RPC message and returns exactly one
JSON-RPC response dict. Sessionful transports (SSE) may pass a session
object to track ``initialize`` state; stateless transports pass ``None``.
"""

import asyncio
from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.manager import mcp_manager
from src.mcp.routes import _write_audit_log

PROTOCOL_VERSION = "2025-03-26"  # streamable HTTP spec revision
TOOL_CALL_TIMEOUT = 30  # seconds; guards against hung plugin handlers


class JsonRpcRequest(BaseModel):
    """Wire format for one JSON-RPC message (validated by FastAPI)."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = {}
    id: int | str | None = None


def _result(result: Any, rpc_id: int | str | None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": rpc_id}


def _error(code: int, message: str, rpc_id: int | str | None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": rpc_id}


async def dispatch_jsonrpc(
    method: str,
    params: dict[str, Any],
    rpc_id: int | str | None,
    user: Any = None,
    db: AsyncSession | None = None,
    session: Any = None,
) -> dict[str, Any]:
    """Handle one MCP JSON-RPC method and return the response dict.

    ``user`` is the authenticated User (None → empty permission set).
    ``session`` (optional) receives ``initialized`` / ``client_info`` on
    the ``initialize`` method for sessionful transports.
    """
    user_perms = set()
    if user is not None:
        from src.core.deps import get_user_permissions

        user_perms = get_user_permissions(user)

    try:
        # ---- initialize ----
        if method == "initialize":
            if session is not None:
                session.initialized = True
                session.client_info = params.get("clientInfo", {})
            return _result({
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"listChanged": True},
                    "prompts": {"listChanged": True},
                },
                "serverInfo": {
                    "name": "ApeAdmin MCP Server",
                    "version": "2.9.0",
                },
            }, rpc_id)

        # ---- tools/list ----
        if method == "tools/list":
            tools = mcp_manager.list_tools(user_perms)
            return _result({
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema,
                        "category": t.category,
                    }
                    for t in tools
                ]
            }, rpc_id)

        # ---- tools/call ----
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:
                return _error(-32602, "Missing 'name' in params", rpc_id)

            # RBAC check
            if "mcp:tools:call" not in user_perms and "*" not in user_perms:
                return _error(-32603, "Permission denied: mcp:tools:call", rpc_id)

            available = mcp_manager.list_tools(user_perms)
            if tool_name not in {t.name for t in available}:
                return _error(-32602, f"Tool not found: {tool_name}", rpc_id)

            try:
                result = await asyncio.wait_for(
                    mcp_manager.call_tool(tool_name, arguments),
                    timeout=TOOL_CALL_TIMEOUT,
                )
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, result)
                return _result({
                    "content": [{"type": "text", "text": str(result)}],
                }, rpc_id)
            except asyncio.TimeoutError:
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, status="failed")
                return _error(
                    -32603,
                    f"Tool execution timed out after {TOOL_CALL_TIMEOUT}s: {tool_name}",
                    rpc_id,
                )
            except Exception as exc:
                if user:
                    await _write_audit_log(db, "tool", tool_name, user, arguments, status="failed")
                return _error(-32603, f"Tool execution failed: {exc}", rpc_id)

        # ---- resources/list ----
        if method == "resources/list":
            resources = mcp_manager.list_resources()
            return _result({
                "resources": [
                    {
                        "uri": r.uri,
                        "name": r.name,
                        "description": r.description,
                        "mimeType": r.mime_type,
                    }
                    for r in resources
                ]
            }, rpc_id)

        # ---- resources/read ----
        if method == "resources/read":
            uri = params.get("uri")
            if not uri:
                return _error(-32602, "Missing 'uri' in params", rpc_id)
            try:
                content = await mcp_manager.read_resource(uri)
                if user:
                    await _write_audit_log(db, "resource", uri, user, result=content[:2000])
                return _result({
                    "contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]
                }, rpc_id)
            except ValueError as exc:
                return _error(-32602, str(exc), rpc_id)

        # ---- prompts/list ----
        if method == "prompts/list":
            prompts = mcp_manager.list_prompts()
            return _result({
                "prompts": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "arguments": [{"name": a} for a in p.arguments],
                    }
                    for p in prompts
                ]
            }, rpc_id)

        # ---- prompts/get (MCP standard) / prompts/render (legacy alias) ----
        if method in ("prompts/get", "prompts/render"):
            prompt_name = params.get("name")
            prompt_args = params.get("arguments", {})
            if not prompt_name:
                return _error(-32602, "Missing 'name' in params", rpc_id)
            try:
                rendered = mcp_manager.render_prompt(prompt_name, **prompt_args)
                if user:
                    await _write_audit_log(db, "prompt", prompt_name, user, prompt_args, rendered)
                return _result({
                    "content": [{"type": "text", "text": rendered}]
                }, rpc_id)
            except ValueError as exc:
                return _error(-32602, str(exc), rpc_id)

        # ---- ping ----
        if method == "ping":
            return _result({}, rpc_id)

        return _error(-32601, f"Method not found: {method}", rpc_id)

    except Exception as exc:
        logger.error(f"MCP dispatch error: {exc}")
        return _error(-32603, f"Internal error: {exc}", rpc_id)
