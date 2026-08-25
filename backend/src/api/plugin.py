"""Plugin management routes: list, toggle, config, upload, restart, delete."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import NotFoundException, success_response, ValidationException
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


# ---------------------------------------------------------------------------
# Plugin upload / restart / delete
# ---------------------------------------------------------------------------

# Allowed file extensions
_ALLOWED_EXTENSIONS = {".zip"}

# Max upload size: 50 MB
_MAX_UPLOAD_SIZE = 50 * 1024 * 1024


@router.post("/upload")
async def upload_plugin(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:upload"))],
    file: UploadFile = File(..., description="插件包 .zip 文件"),
):
    """Upload and install a plugin .zip package.

    The zip is validated, extracted into the builtin plugins directory,
    and the plugin metadata is upserted into the database.
    A restart is required for the plugin to be loaded.
    """
    # Validate file extension
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValidationException("仅支持 .zip 格式的插件包")

    # Read file content with size check
    content = await file.read()
    if len(content) > _MAX_UPLOAD_SIZE:
        raise ValidationException("插件包大小不能超过 50MB")

    # Save to temp file
    upload_dir = Path(settings.PLUGINS_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    tmp_path = upload_dir / f"upload_{filename}"
    tmp_path.write_bytes(content)

    # Import the plugin package
    from src.plugins.manager import plugin_manager

    try:
        manifest = plugin_manager.import_plugin(tmp_path)
    except ValueError as exc:
        # Clean up temp file on failure
        tmp_path.unlink(missing_ok=True)
        raise ValidationException(str(exc))

    # Upsert into DB
    plugin_name = manifest["name"]
    record = await crud_plugin.upsert(db, plugin_name, {
        "display_name": manifest.get("display_name", plugin_name),
        "description": manifest.get("description", ""),
        "version": manifest.get("version", "1.0.0"),
        "author": manifest.get("author", ""),
        "module_path": f"src.plugins.builtin.{plugin_name}",
    })

    return success_response(data={
        "id": record.id,
        "name": record.name,
        "display_name": record.display_name,
        "version": record.version,
        "enabled": record.enabled,
    }, msg="插件导入成功，需要重启后端生效")


@router.post("/restart")
async def restart_server(
    user: Annotated[User, Depends(require_permission("system:plugin:restart"))],
):
    """Restart the backend server process.

    Spawns a detached restart script that waits for the current process
    to exit, then relaunches uvicorn. The response is sent before the
    actual restart happens.
    """
    import asyncio
    import stat

    # Write the restart helper script to a temp location
    restart_script = Path(tempfile.gettempdir()) / "apeadmin_restart.sh"
    python_bin = sys.executable
    project_root = Path(__file__).resolve().parent.parent.parent.parent  # backend/

    script_content = f"""#!/bin/bash
# ApeAdmin auto-restart script
# Waits for the old process to exit, then relaunches uvicorn

# Wait a moment for the old process to shut down gracefully
sleep 2

# Relaunch uvicorn
cd "{project_root}"
exec {python_bin} -m uvicorn src.main:app --host 127.0.0.1 --port 8000 >> /tmp/apeadmin_backend.log 2>&1
"""
    restart_script.write_text(script_content)
    restart_script.chmod(restart_script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    # Spawn the restart script as a detached process
    proc = await asyncio.create_subprocess_exec(
        "bash", str(restart_script),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        start_new_session=True,  # Detach from parent process group
    )
    logger = __import__("loguru").logger
    logger.info(f"Restart script spawned (pid={proc.pid}), shutting down in 1s...")

    # Schedule self-termination after a short delay (let the response go out)
    async def _delayed_exit():
        await asyncio.sleep(1)
        logger.info("Backend restarting now...")
        os._exit(0)

    asyncio.create_task(_delayed_exit())

    return success_response(msg="后端正在重启，请等待约 5 秒后刷新页面")


@router.delete("/{plugin_id}")
async def delete_plugin(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:delete"))],
):
    """Delete a plugin: remove its files and database record."""
    plugin = await crud_plugin.get(db, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")

    plugin_name = plugin.name

    # Remove plugin files from disk
    from src.plugins.manager import plugin_manager
    plugin_manager.remove_plugin_files(plugin_name)

    # Delete DB record
    await crud_plugin.delete_by_id(db, plugin_id)

    return success_response(msg=f"插件 '{plugin_name}' 已删除，重启后生效")
