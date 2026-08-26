"""Plugin management routes: list, toggle, config, upload, restart, delete."""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import AppException, NotFoundException, success_response, ValidationException
from src.crud.plugin import crud_plugin
from src.db import get_db
from src.models import User
from src.models.log import SysLog
from src.schemas.plugin import PluginConfigUpdate, PluginToggle

router = APIRouter(prefix="/plugins", tags=["插件管理"])


async def _write_plugin_audit(
    db: AsyncSession,
    user: User,
    action: str,
    plugin_name: str,
    started: float,
    result: dict | None = None,
    error: str | None = None,
) -> None:
    """Write a dedicated plugin lifecycle audit entry without masking the operation result."""
    try:
        entry = SysLog(
            user_id=user.id,
            username=user.username,
            method="PLUGIN",
            path=f"/api/v1/plugins/{plugin_name}/{action}",
            params=json.dumps(result or {}, ensure_ascii=False)[:10000],
            status_code=200 if error is None else 409,
            duration_ms=int((time.perf_counter() - started) * 1000),
            error=error,
        )
        db.add(entry)
        await db.commit()
    except Exception as exc:
        await db.rollback()
        __import__("loguru").logger.warning(f"Failed to write plugin audit log: {exc}")


def _plugin_to_dict(p) -> dict:
    """Convert Plugin ORM to dict with parsed config."""
    try:
        config = json.loads(p.config) if p.config else None
    except (json.JSONDecodeError, TypeError):
        config = None
    from src.plugins.manager import plugin_manager
    runtime = plugin_manager.get_plugin(p.name)
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
        "runtime_state": runtime.runtime_state if runtime else ("active" if p.enabled else "inactive"),
        "last_error": runtime.last_error if runtime else None,
        "dependencies": runtime.dependencies if runtime else [],
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
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:toggle"))],
):
    """Enable or disable a plugin in the current process."""
    plugin = await crud_plugin.get(db, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")

    from src.plugins.manager import plugin_manager

    started = time.perf_counter()
    try:
        if body.enabled:
            result = await plugin_manager.enable_plugin(plugin.name, request.app, db=db)
        else:
            result = await plugin_manager.disable_plugin(plugin.name, request.app, db=db)
    except Exception as exc:
        await _write_plugin_audit(db, user, "enable" if body.enabled else "disable", plugin.name, started, error=str(exc))
        raise AppException(
            msg=f"热拔插失败：{exc}，建议重启后端",
            code=409,
            data={"fallback": "/api/v1/plugins/restart", "name": plugin.name},
        ) from exc

    state = "启用" if body.enabled else "禁用"
    await _write_plugin_audit(db, user, "enable" if body.enabled else "disable", plugin.name, started, result=result)
    return success_response(data=result | {"refresh": True}, msg=f"插件已{state}，运行时生效")


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
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:upload"))],
    file: UploadFile = File(..., description="插件包 .zip 文件"),
):
    """Upload and install a plugin .zip package.

    The zip is validated, extracted into the builtin plugins directory,
    and the plugin metadata is upserted into the database.
    The plugin is installed and activated without restarting the backend.
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

    # Import, install and register the plugin package in the current process.
    from src.plugins.manager import plugin_manager

    started = time.perf_counter()
    try:
        result = await plugin_manager.install_plugin_from_zip(tmp_path, request.app)
    except (ValueError, OSError) as exc:
        # Clean up temp file on failure
        tmp_path.unlink(missing_ok=True)
        await _write_plugin_audit(db, user, "install", filename, started, error=str(exc))
        raise ValidationException(str(exc))

    # Upsert metadata only after runtime installation succeeds.
    plugin_name = result["name"]
    record = await crud_plugin.upsert(db, plugin_name, {
        "display_name": result.get("display_name", plugin_name),
        "description": result.get("description", ""),
        "version": result.get("version", "1.0.0"),
        "author": result.get("author", ""),
        "module_path": f"src.plugins.builtin.{plugin_name}",
    })
    record.enabled = True
    await db.commit()
    await db.refresh(record)
    await _write_plugin_audit(db, user, "install", plugin_name, started, result=result)

    return success_response(data={
        "id": record.id,
        "name": record.name,
        "display_name": record.display_name,
        "version": record.version,
        "enabled": record.enabled,
        **{k: v for k, v in result.items() if k not in {"name", "display_name", "version"}},
        "refresh": True,
    }, msg="插件安装成功，运行时生效")


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
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:plugin:delete"))],
    keep_data: bool = Query(True, description="是否保留插件业务数据"),
):
    """Uninstall a plugin at runtime and optionally remove its data."""
    plugin = await crud_plugin.get(db, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")

    plugin_name = plugin.name

    from src.plugins.manager import plugin_manager
    started = time.perf_counter()
    try:
        result = await plugin_manager.uninstall_plugin(
            plugin_name,
            request.app,
            keep_data=keep_data,
            db=db,
        )
    except Exception as exc:
        await _write_plugin_audit(db, user, "uninstall", plugin_name, started, error=str(exc))
        raise AppException(
            msg=f"插件卸载失败：{exc}，建议重启后端",
            code=409,
            data={"fallback": "/api/v1/plugins/restart", "name": plugin_name},
        ) from exc

    await _write_plugin_audit(db, user, "uninstall", plugin_name, started, result=result)
    return success_response(data={**result, "refresh": True}, msg=f"插件 '{plugin_name}' 已卸载，运行时生效")
