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

from fastapi import APIRouter, Depends, File, Request, UploadFile
from loguru import logger
from starlette.concurrency import run_in_threadpool

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import ValidationException, success_response
from src.core.i18n import get_locale, t
from src.db import get_db
from src.models import User
from src.models.log import SysLog

router = APIRouter(prefix="/system", tags=["系统管理"])

# Max deploy package size: 200 MB (source + frontend_dist + deps)
_MAX_PKG_SIZE = 200 * 1024 * 1024

# Allowed extensions
_ALLOWED_EXTS = {".tar.gz", ".tgz"}


def _extract_update_package(tmp_pkg: Path, extract_dir: Path) -> None:
    """Extract a pre-validated tar.gz package (called in a worker thread)."""
    with tarfile.open(tmp_pkg, "r:gz") as tar:
        tar.extractall(str(extract_dir))


def _replace_directory(src: Path, dst: Path) -> None:
    """Atomically replace ``dst`` with ``src`` (called in a worker thread)."""
    if dst.exists():
        shutil.rmtree(str(dst))
    shutil.copytree(str(src), str(dst))


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
        # Base-stack identity: "python" (FastAPI) — the Go base
        # (ApeAdmin-Gin) reports "go". The frontend uses it to warn when a
        # package built for the other stack is uploaded.
        "runtime": "python",
    })


@router.post("/update")
async def upload_update(
    file: UploadFile = File(..., description="部署包 .tar.gz 文件"),
    request: Request = None,  # type: ignore
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
    locale = get_locale(request)
    if user.username != settings.SUPER_ADMIN_USERNAME:
        raise ValidationException(t("system.super_admin_only", locale))

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
        raise ValidationException(t("system.tar_gz_only", locale))

    # ---- Read content with size check ----
    content = await file.read()
    if len(content) > _MAX_PKG_SIZE:
        raise ValidationException(t("system.package_too_large", locale))

    # ---- Save to temp file ----
    tmp_dir = Path(tempfile.gettempdir()) / "apeadmin_update"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_pkg = tmp_dir / f"update_{int(time.time())}.tar.gz"
    # A 200MB sync write would block the event loop for seconds.
    await run_in_threadpool(tmp_pkg.write_bytes, content)
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
                    raise ValidationException(t("system.invalid_path", locale, path=member.name))
            # Security: reject archive bombs (zip of highly compressible data).
            # Limit total uncompressed size to 1 GB, single files to 500 MB,
            # and member count to 50k entries.
            total_uncompressed = sum(m.size for m in tar.getmembers())
            if total_uncompressed > 1024 * 1024 * 1024 or len(tar.getmembers()) > 50_000:
                raise ValidationException(t("system.suspicious_package", locale))

        # Cross-stack guard: users occasionally upload a plugin package
        # (or a Go-stack archive) where a deploy package is expected.
        # Fail early with an actionable message instead of a generic
        # "缺少 src/ 目录" error.  The plain "unknown" case keeps the
        # original explicit structural error below.
        from src.core.pkgdetect import detect_tar_gz_kind, mismatch_message

        pkg_kind = detect_tar_gz_kind(tmp_pkg)
        if pkg_kind in {"plugin", "go-binary"}:
            hint = mismatch_message(pkg_kind, "system-update")
            if hint:
                raise ValidationException(hint)

        await run_in_threadpool(_extract_update_package, tmp_pkg, extract_dir)
    except tarfile.ReadError:
        raise ValidationException(t("system.extract_failed", locale))
    except ValidationException:
        raise
    except Exception as exc:
        raise ValidationException(t("system.extract_error", locale, error=str(exc))) from exc

    # Find the top-level directory inside the archive
    top_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if not top_dirs:
        raise ValidationException(t("system.empty_package", locale))
    pkg_root = top_dirs[0]  # e.g. apeadmin/

    # Must contain src/ directory
    if not (pkg_root / "src").is_dir():
        raise ValidationException(t("system.missing_src", locale))

    # ---- Backup current code ----
    backup_dir = project_root.parent / f"apeadmin_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Backing up current code to {backup_dir}")
    # A full-tree copy is heavy disk IO; run it in a worker thread.
    await run_in_threadpool(
        shutil.copytree,
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
        await run_in_threadpool(_replace_directory, src_src, src_dst)

    # 2. Copy frontend_dist/ (built frontend)
    fe_src = pkg_root / "frontend_dist"
    fe_dst = project_root / "frontend_dist"
    if fe_src.is_dir():
        logger.info("Overwriting frontend_dist/ ...")
        await run_in_threadpool(_replace_directory, fe_src, fe_dst)

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
        await run_in_threadpool(_replace_directory, scripts_src, scripts_dst)

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

    # ---- Spawn restart script (cross-platform, see src/core/runtime.py) ----
    from src.core.runtime import spawn_restart

    python_bin = sys.executable
    restart_info = await spawn_restart(project_root, python_bin)
    logger.info(
        f"Update restart script spawned (mode={restart_info['mode']}, "
        f"pid={restart_info['spawner_pid']}), shutting down in 1s..."
    )

    # Schedule self-termination. Keep a strong reference on request.app.state:
    # the event loop only holds a weak reference to tasks, so an unreferenced
    # task may be garbage-collected and the scheduled exit would never run.
    async def _delayed_exit():
        await asyncio.sleep(1)
        logger.info("Backend restarting after update...")
        os._exit(0)

    request.app.state.update_restart_task = asyncio.create_task(_delayed_exit())

    return success_response(
        data={
            "old_pid": os.getpid(),
            "backup_dir": str(backup_dir),
            "restart_mode": restart_info["mode"],
            "restart_log": restart_info.get("log"),
        },
        msg=t("system.update_complete", locale),
    )
