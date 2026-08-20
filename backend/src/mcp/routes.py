"""MCP HTTP endpoint: exposes the MCP server over SSE transport.

Mounts at the configured MCP_PREFIX and provides:
- GET  /mcp/tools    — list available tools (filtered by user permissions)
- POST /mcp/tools/call — call a tool by name
- GET  /mcp/resources — list resources
- GET  /mcp/resources/read?uri=... — read a resource
- GET  /mcp/prompts   — list prompts
- POST /mcp/prompts/render — render a prompt
"""

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, get_user_permissions
from src.core.exceptions import success_response, AppException
from src.db import get_db
from src.mcp.manager import mcp_manager
from src.models import User

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
            }
            for t in tools
        ]
    )


@router.post("/tools/call")
async def call_tool(
    body: CallToolRequest,
    user: Annotated[User, Depends(get_current_user)],
):
    """Call an MCP tool by name with the given arguments."""
    permissions = get_user_permissions(user)
    available_tools = mcp_manager.list_tools(permissions)
    tool_names = {t.name for t in available_tools}

    if body.name not in tool_names:
        raise AppException(f"Tool '{body.name}' not found or not permitted", code=403)

    try:
        result = await mcp_manager.call_tool(body.name, body.arguments)
    except Exception as exc:
        raise AppException(f"Tool execution failed: {exc}")

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
):
    """Read the content of an MCP resource by URI."""
    try:
        content = await mcp_manager.read_resource(uri)
    except ValueError as exc:
        raise AppException(str(exc), code=404)
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
):
    """Render a prompt template with the given arguments."""
    try:
        rendered = mcp_manager.render_prompt(body.name, **body.arguments)
    except ValueError as exc:
        raise AppException(str(exc), code=404)
    return success_response(data={"rendered": rendered})
