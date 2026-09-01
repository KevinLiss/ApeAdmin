"""System management routes: version info, deploy-package upload & update.

Provides:
- GET /system/version  — current app version + server info
- POST /system/update   — upload a .tar.gz deploy package, validate,
                           backup current code, extract-overwrite,
                           pip install deps, then restart the process
"""

import asyncio
import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from loguru import logger

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import ValidationException, success_response
from src.db import get_db
from src.models import User
from src.models.log import SysLog

router = APIRouter(prefix="/system", tags=["系统管理"])

# Max deploy package size: 200 MB (source + frontend_dist + deps)
_MAX_PKG_SIZE = 200 * 1024 * 1024

# Allowed extensions
_ALLOWED_EXTS = {".tar.gz", ".tgz"}


@router.get("/version")
async def get_version(
    user: Annotated[User, Depends(require_permission("system:version:view"))],
):
    """Return current app version and server-side info for the update dialog."""
    project_root = Path(__file__).resolve().parents[2]  # backend/ or deploy root
    # Check if .env exists (production)
    env_file = project_root / ".env"

    return success_response(data={
        "current_version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "python_version": sys.version.split()[0],
        "project_root": str(project_root),
        "has_env": env_file.exists(),
        "pid": os.getpid(),
    })


@router.post("/update")
async def upload_update(
    file: UploadFile = File(..., description="部署包 .tar.gz 文件"),
    user: Annotated[User, Depends(require_permission("system:version:update"))] = None,  # type: ignore
):
    """Upload a new deploy package and perform an in-place update.

    Flow:
    1. Validate file extension and size
    2. Save to temp dir
    3. Validate tar.gz structure (must contain a top-level dir with src/)
    4. Backup current code to backup_<timestamp>/
    5. Extract new package, overwrite src/ and frontend_dist/
    6. Install new requirements
    7. Spawn restart script, self-terminate

    The response is sent before the actual restart happens.
    """
    # ---- Validate super admin (only super admin can update) ----
    if user.username != settings.SUPER_ADMIN_USERNAME:
        raise ValidationException("仅超级管理员可执行版本更新")

    # ---- Validate file extension ----
    filename = file.filename or ""
    # Normalize: check both .tar.gz and .tgz
    lower_name = filename.lower()
    valid = False
    for ext in _ALLOWED_EXTS:
        if lower_name.endswith(ext):
            valid = True
            break
    if not valid:
        raise ValidationException("仅支持 .tar.gz 格式的部署包")

    # ---- Read content with size check ----
    content = await file.read()
    if len(content) > _MAX_PKG_SIZE:
        raise ValidationException(f"部署包大小不能超过 {_MAX_PKG_SIZE // (1024*1024)}MB")

    # ---- Save to temp file ----
    tmp_dir = Path(tempfile.gettempdir()) / "apeadmin_update"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_pkg = tmp_dir / f"update_{int(time.time())}.tar.gz"
    tmp_pkg.write_bytes(content)
    logger.info(f"Update package saved: {tmp_pkg} ({len(content)} bytes)")

    # ---- Validate tar.gz structure ----
    project_root = Path(__file__).resolve().parents[2]  # backend/ or deploy root
    extract_dir = tmp_dir / f"extract_{int(time.time())}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(tmp_pkg, "r:gz") as tar:
            # Security: prevent path traversal (no absolute paths or ..)
            for member in tar.getmembers():
                if member.name.startswith("/") or ".." in member.name:
                    raise ValidationException(f"非法路径: {member.name}")
            tar.extractall(str(extract_dir))
    except tarfile.ReadError:
        raise ValidationException("无法解压，请检查文件是否为有效的 .tar.gz 包")
    except ValidationException:
        raise
    except Exception as exc:
        raise ValidationException(f"解压失败: {exc}") from exc

    # Find the top-level directory inside the archive
    top_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if not top_dirs:
        raise ValidationException("部署包为空或结构不正确")
    pkg_root = top_dirs[0]  # e.g. apeadmin/

    # Must contain src/ directory
    if not (pkg_root / "src").is_dir():
        raise ValidationException("部署包结构不正确：缺少 src/ 目录")

    # ---- Backup current code ----
    backup_dir = project_root.parent / f"apeadmin_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Backing up current code to {backup_dir}")
    shutil.copytree(
        str(project_root),
        str(backup_dir),
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".git", "node_modules",
            "uploads", ".env", "apeadmin.db", "*.db",
        ),
    )

    # ---- Overwrite code ----
    # 1. Copy src/ (backend source)
    src_src = pkg_root / "src"
    src_dst = project_root / "src"
    if src_src.is_dir():
        logger.info("Overwriting src/ ...")
        # Remove old src contents (but keep plugins/builtin uploads if any)
        # Actually, full overwrite is cleaner for version updates
        if src_dst.exists():
            shutil.rmtree(str(src_dst))
        shutil.copytree(str(src_src), str(src_dst))

    # 2. Copy frontend_dist/ (built frontend)
    fe_src = pkg_root / "frontend_dist"
    fe_dst = project_root / "frontend_dist"
    if fe_src.is_dir():
        logger.info("Overwriting frontend_dist/ ...")
        if fe_dst.exists():
            shutil.rmtree(str(fe_dst))
        shutil.copytree(str(fe_src), str(fe_dst))

    # 3. Copy requirements.txt
    req_src = pkg_root / "requirements.txt"
    req_dst = project_root / "requirements.txt"
    if req_src.is_file():
        logger.info("Overwriting requirements.txt ...")
        shutil.copy2(str(req_src), str(req_dst))

    # 4. Copy scripts/ if present
    scripts_src = pkg_root / "scripts"
    scripts_dst = project_root / "scripts"
    if scripts_src.is_dir():
        logger.info("Overwriting scripts/ ...")
        if scripts_dst.exists():
            shutil.rmtree(str(scripts_dst))
        shutil.copytree(str(scripts_src), str(scripts_dst))

    # ---- Install new dependencies ----
    if req_dst.exists():
        logger.info("Installing new requirements...")
        pip_proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-r", str(req_dst),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await pip_proc.communicate()
        if pip_proc.returncode != 0:
            logger.error(f"pip install failed:\n{stderr.decode()}")
            raise ValidationException(
                f"依赖安装失败 (exit {pip_proc.returncode}): {stderr.decode()[:2000]}"
            )
        logger.info("Dependencies installed successfully")

    # ---- Write audit log ----
    try:
        from src.db import SessionLocal
        async with SessionLocal() as db:
            entry = SysLog(
                user_id=user.id,
                username=user.username,
                method="SYSTEM",
                path="/api/v1/system/update",
                params=json.dumps({
                    "filename": filename,
                    "size": len(content),
                    "backup_dir": str(backup_dir),
                }, ensure_ascii=False)[:10000],
                status_code=200,
                duration_ms=0,
            )
            db.add(entry)
            await db.commit()
    except Exception as exc:
        logger.warning(f"Failed to write update audit log: {exc}")

    # ---- Clean up temp files ----
    shutil.rmtree(str(extract_dir), ignore_errors=True)
    tmp_pkg.unlink(missing_ok=True)

    # ---- Spawn restart script ----
    import stat

    restart_script = Path(tempfile.gettempdir()) / "apeadmin_update_restart.sh"
    python_bin = sys.executable

    script_content = f"""#!/bin/bash
# ApeAdmin version update restart script
sleep 2

# Try systemd restart first (production)
if command -v systemctl &>/dev/null && systemctl list-unit-files | grep -q apeadmin; then
    systemctl restart apeadmin
    exit 0
fi

# Fallback: direct uvicorn restart
cd "{project_root}"
exec "{python_bin}" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 </dev/null >> /tmp/apeadmin_backend.log 2>&1
"""
    restart_script.write_text(script_content)
    restart_script.chmod(
        restart_script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    )

    proc = await asyncio.create_subprocess_exec(
        "bash", str(restart_script),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        start_new_session=True,
    )
    logger.info(f"Update restart script spawned (pid={proc.pid}), shutting down in 1s...")

    # Schedule self-termination
    async def _delayed_exit():
        await asyncio.sleep(1)
        logger.info("Backend restarting after update...")
        os._exit(0)

    asyncio.create_task(_delayed_exit())

    return success_response(
        data={
            "old_pid": os.getpid(),
            "backup_dir": str(backup_dir),
        },
        msg="版本更新完成，后端正在重启，请等待约 5 秒后刷新页面",
    )
