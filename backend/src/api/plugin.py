"""Plugin management routes: list, toggle enable/disable, get/set config."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import require_permission
from src.core.exceptions import NotFoundException, success_response
from src.crud.plugin import crud_plugin
from src.db import get_db
from src.models import User
from src.schemas.plugin import PluginConfigUpdate, PluginToggle

router = APIRouter(prefix="/plugins", tags=["插件管理"])


def _plugin_to_dict(p) -> dict:
    """Convert Plugin ORM to dict with parsed config."""
    try:
        config = json.loads(p.config) if p.config else None
    except (json.JSONDecodeError, TypeError):
        config = None
    return {
        "id": p.id,
        "name": p.name,
        "display_name": p.display_name,
        "description": p.description,
        "version": p.version,
        "author": p.author,
        "module_path": p.module_path,
        "enabled": p.enabled,
        "config": config,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


@router.get("")
async def list_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:list"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all registered plugins (paginated)."""
    items, total = await crud_plugin.get_multi(db, page=page, page_size=page_size)
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_plugin_to_dict(p) for p in items],
    })


@router.put("/{plugin_id}/toggle")
async def toggle_plugin(
    plugin_id: int,
    body: PluginToggle,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:toggle"))],
):
    """Enable or disable a plugin (requires restart to take effect)."""
    plugin = await crud_plugin.get(db, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")

    await crud_plugin.update(db, plugin_id, {"enabled": body.enabled})
    state = "启用" if body.enabled else "禁用"
    return success_response(msg=f"插件已{state}，重启后生效")


@router.get("/{plugin_id}/config")
async def get_plugin_config(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:config"))],
):
    """Get plugin configuration."""
    plugin = await crud_plugin.get(db, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")

    try:
        config = json.loads(plugin.config) if plugin.config else {}
    except (json.JSONDecodeError, TypeError):
        config = {}

    return success_response(data={"config": config})


@router.put("/{plugin_id}/config")
async def update_plugin_config(
    plugin_id: int,
    body: PluginConfigUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:config"))],
):
    """Update plugin configuration."""
    plugin = await crud_plugin.set_config(db, plugin_id, body.config)
    if not plugin:
        raise NotFoundException("插件不存在")

    return success_response(msg="配置已保存")
