"""MCP HTTP endpoint: exposes the MCP server over SSE transport.

Mounts at the configured MCP_PREFIX and provides:
- GET  /mcp/tools    — list available tools (filtered by user permissions)
- POST /mcp/tools/call — call a tool by name
- GET  /mcp/resources — list resources
- GET  /mcp/resources/read?uri=... — read a resource
- GET  /mcp/prompts   — list prompts
- POST /mcp/prompts/render — render a prompt
- GET  /mcp/audit-logs — list audit logs (admin)
"""

import json
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Query
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, get_user_permissions
from src.core.exceptions import success_response, AppException
from src.db import get_db
from src.mcp.manager import mcp_manager
from src.models import McpAuditLog, User

router = APIRouter(prefix="/mcp", tags=["MCP 协议"])


class CallToolRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


class RenderPromptRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


def register_mcp_routes(app: FastAPI) -> None:
    """Mount the MCP API routes on the app."""
    from src.core.config import settings

    app.include_router(router, prefix=settings.API_PREFIX)


# ---- Audit helpers ----

async def _write_audit_log(
    db: AsyncSession,
    action_type: str,
    target_name: str,
    user: User | None,
    arguments: dict[str, Any] | None = None,
    result: Any = None,
    status: str = "success",
) -> None:
    """Persist an MCP audit log row."""
    try:
        import json as _json

        arg_text = _json.dumps(arguments, ensure_ascii=False, default=str)[:2000] if arguments else None
        result_text = _json.dumps(result, ensure_ascii=False, default=str)[:2000] if result is not None else None
        log = McpAuditLog(
            action_type=action_type,
            target_name=target_name,
            arguments=arg_text,
            result_preview=result_text,
            status=status,
            user_id=user.id if user else None,
            username=user.username if user else None,
        )
        db.add(log)
        await db.commit()
    except Exception as exc:
        logger.warning(f"Failed to write MCP audit log: {exc}")


# ---- Tools ----

@router.get("/tools")
async def list_tools(
    user: Annotated[User, Depends(get_current_user)],
):
    """List all MCP tools available to the current user (RBAC-filtered)."""
    permissions = get_user_permissions(user)
    tools = mcp_manager.list_tools(permissions)
    return success_response(
        data=[
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "category": t.category,
                "plugin_name": t.plugin_name,
                "required_permissions": t.required_permissions,
            }
            for t in tools
        ]
    )


@router.get("/tools/categories")
async def list_tool_categories(
    user: Annotated[User, Depends(get_current_user)],
):
    """List all MCP tool categories with counts."""
    categories = mcp_manager.list_categories()
    return success_response(data=categories)


@router.post("/tools/call")
async def call_tool(
    body: CallToolRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Call an MCP tool by name with the given arguments."""
    permissions = get_user_permissions(user)
    available_tools = mcp_manager.list_tools(permissions)
    tool_names = {t.name for t in available_tools}

    if body.name not in tool_names:
        raise AppException(f"Tool '{body.name}' not found or not permitted", code=403)

    # Button-level permission: mcp:tools:call
    # Super admin gets "*" so this passes automatically.
    if "mcp:tools:call" not in permissions and "*" not in permissions:
        raise AppException("Missing permission: mcp:tools:call", code=403)

    try:
        result = await mcp_manager.call_tool(body.name, body.arguments)
    except Exception as exc:
        await _write_audit_log(db, "tool", body.name, user, body.arguments, status="failed")
        raise AppException(f"Tool execution failed: {exc}")

    await _write_audit_log(db, "tool", body.name, user, body.arguments, result)
    return success_response(data={"result": result})


# ---- Resources ----

@router.get("/resources")
async def list_resources(
    user: Annotated[User, Depends(get_current_user)],
):
    """List all registered MCP resources."""
    resources = mcp_manager.list_resources()
    return success_response(
        data=[
            {
                "uri": r.uri,
                "name": r.name,
                "description": r.description,
                "mime_type": r.mime_type,
            }
            for r in resources
        ]
    )


@router.get("/resources/read")
async def read_resource(
    uri: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Read the content of an MCP resource by URI."""
    try:
        content = await mcp_manager.read_resource(uri)
    except ValueError as exc:
        await _write_audit_log(db, "resource", uri, user, status="failed")
        raise AppException(str(exc), code=404)
    await _write_audit_log(db, "resource", uri, user, result=content[:2000])
    return success_response(data={"uri": uri, "content": content})


# ---- Prompts ----

@router.get("/prompts")
async def list_prompts(
    user: Annotated[User, Depends(get_current_user)],
):
    """List all registered MCP prompt templates."""
    prompts = mcp_manager.list_prompts()
    return success_response(
        data=[
            {
                "name": p.name,
                "description": p.description,
                "arguments": p.arguments,
            }
            for p in prompts
        ]
    )


@router.post("/prompts/render")
async def render_prompt(
    body: RenderPromptRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Render a prompt template with the given arguments."""
    try:
        rendered = mcp_manager.render_prompt(body.name, **body.arguments)
    except ValueError as exc:
        await _write_audit_log(db, "prompt", body.name, user, body.arguments, status="failed")
        raise AppException(str(exc), code=404)
    await _write_audit_log(db, "prompt", body.name, user, body.arguments, result=rendered)
    return success_response(data={"rendered": rendered})


# ---- Audit logs ----

@router.get("/audit-logs")
async def list_audit_logs(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action_type: str | None = Query(None),
    keyword: str | None = Query(None),
):
    """List MCP audit logs (paginated, optional filters)."""
    stmt = select(McpAuditLog)
    count_stmt = select(func.count()).select_from(McpAuditLog)

    if action_type:
        stmt = stmt.where(McpAuditLog.action_type == action_type)
        count_stmt = count_stmt.where(McpAuditLog.action_type == action_type)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(McpAuditLog.target_name.ilike(kw) | McpAuditLog.username.ilike(kw))
        count_stmt = count_stmt.where(McpAuditLog.target_name.ilike(kw) | McpAuditLog.username.ilike(kw))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.order_by(McpAuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": l.id,
                    "action_type": l.action_type,
                    "target_name": l.target_name,
                    "arguments": l.arguments,
                    "result_preview": l.result_preview,
                    "status": l.status,
                    "user_id": l.user_id,
                    "username": l.username,
                    "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else None,
                }
                for l in logs
            ],
        }
    )