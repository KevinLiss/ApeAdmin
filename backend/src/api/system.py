"""System management routes: version info, deploy-package upload & update.

Provides:
- GET /system/version  — current app version + server info
- POST /system/update   — upload a deploy package (.tar.gz or .zip), validate,
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
import zipfile
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

# Allowed extensions: tar.gz (traditional) and zip (ApeHub release format)
_ALLOWED_EXTS = {".tar.gz", ".tgz", ".zip"}

# Archive-bomb guards: total uncompressed size / member count.
_MAX_TOTAL_UNCOMPRESSED = 1024 * 1024 * 1024  # 1 GB
_MAX_MEMBERS = 50_000

# Paths the update overwrites (and therefore restores on rollback).
_REPLACED_PATHS = ("src", "frontend_dist", "requirements.txt", "scripts")


def _project_root() -> Path:
    """Deploy root (contains src/, .env, ...) — overridable in tests."""
    return Path(__file__).resolve().parents[2]


def _validate_tar_members(tar: tarfile.TarFile, locale: str) -> None:
    """Security checks on a tar archive before extraction (sync, worker thread)."""
    members = tar.getmembers()
    total = 0
    for member in members:
        if member.name.startswith("/") or ".." in member.name:
            raise ValidationException(t("system.invalid_path", locale, path=member.name))
        # A deployment package never needs links; a symlink could point the
        # extract step at arbitrary host paths (e.g. overwrite /etc/...).
        if member.issym() or member.islnk():
            raise ValidationException(t("system.no_links", locale, path=member.name))
        total += member.size
    if total > _MAX_TOTAL_UNCOMPRESSED or len(members) > _MAX_MEMBERS:
        raise ValidationException(t("system.suspicious_package", locale))


def _validate_zip_members(zf: zipfile.ZipFile, locale: str) -> None:
    """Security checks on a zip archive before extraction (sync, worker thread)."""
    infos = zf.infolist()
    total = 0
    for info in infos:
        name = info.filename
        # Reject absolute paths, traversal, Windows drive letters and
        # backslash separators (zip spec uses "/"; backslashes are either
        # malformed or an attempt to smuggle a path on Windows hosts).
        if (
            name.startswith("/")
            or ".." in name
            or ":" in name.split("/", 1)[0]
            or "\\" in name
        ):
            raise ValidationException(t("system.invalid_path", locale, path=name))
        total += info.file_size
    if total > _MAX_TOTAL_UNCOMPRESSED or len(infos) > _MAX_MEMBERS:
        raise ValidationException(t("system.suspicious_package", locale))


def _extract_update_package(tmp_pkg: Path, extract_dir: Path, locale: str) -> None:
    """Validate + extract a pre-saved package (called in a worker thread).

    Supports both .tar.gz (traditional) and .zip (ApeHub release format).
    """
    if tmp_pkg.name.lower().endswith(".zip"):
        with zipfile.ZipFile(tmp_pkg, "r") as zf:
            _validate_zip_members(zf, locale)
            zf.extractall(str(extract_dir))
    else:
        with tarfile.open(tmp_pkg, "r:gz") as tar:
            _validate_tar_members(tar, locale)
            tar.extractall(str(extract_dir))


def _locate_pkg_root(extract_dir: Path) -> Path:
    """Find the deploy-package root inside the extraction directory.

    Handles both layouts: a single top-level dir (apeadmin/...) and a
    flat archive whose members sit directly at the root (src/...).
    """
    if (extract_dir / "src").is_dir():
        return extract_dir
    candidates = [d for d in extract_dir.iterdir() if d.is_dir()]
    with_src = [d for d in candidates if (d / "src").is_dir()]
    if len(with_src) == 1:
        return with_src[0]
    if not candidates:
        raise ValidationException(t("system.empty_package", locale=locale))
    if len(candidates) == 1:
        return candidates[0]
    raise ValidationException(t("system.missing_src", locale=locale))


def _replace_directory(src: Path, dst: Path) -> None:
    """Atomically replace ``dst`` with ``src`` (called in a worker thread)."""
    if dst.exists():
        shutil.rmtree(str(dst))
    shutil.copytree(str(src), str(dst))


def _restore_install_only_plugins(backup_src: Path, new_src: Path) -> list[str]:
    """Bring back built-in plugins that exist on this install only.

    The deploy package ships the open-source baseline; plugins imported
    afterwards (e.g. ``apehub_web`` with its site data) live only on the
    install. After the full src/ replace, copy any plugin directory from
    the pre-update backup that the package does not contain, so a
    version update never destroys installed plugins.
    """
    restored: list[str] = []
    backup_builtin = backup_src / "plugins" / "builtin"
    new_builtin = new_src / "plugins" / "builtin"
    if not backup_builtin.is_dir():
        return restored
    new_builtin.mkdir(parents=True, exist_ok=True)
    for child in backup_builtin.iterdir():
        if child.is_dir() and not (new_builtin / child.name).exists():
            shutil.copytree(str(child), str(new_builtin / child.name))
            restored.append(child.name)
    return restored


@router.get("/version")
async def get_version(
    user: Annotated[User, Depends(require_permission("system:version:view"))],
):
    """Return current app version and server-side info for the update dialog."""
    project_root = _project_root()
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


def _rollback_backup(backup_dir: Path, project_root: Path, replaced: list[str]) -> None:
    """Restore the pre-update state of ``replaced`` paths from the backup."""
    for name in replaced:
        saved = backup_dir / name
        dst = project_root / name
        if not saved.exists():
            continue
        if saved.is_dir():
            _replace_directory(saved, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(saved), str(dst))
    logger.info(f"Rolled back {replaced} from {backup_dir}")


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
    # Preserve the original extension: the extractor dispatches on it.
    tmp_suffix = ".zip" if lower_name.endswith(".zip") else ".tar.gz"
    tmp_pkg = tmp_dir / f"update_{int(time.time())}{tmp_suffix}"
    # A 200MB sync write would block the event loop for seconds.
    await run_in_threadpool(tmp_pkg.write_bytes, content)
    logger.info(f"Update package saved: {tmp_pkg} ({len(content)} bytes)")

    # ---- Validate tar.gz structure ----
    project_root = _project_root()
    extract_dir = tmp_dir / f"extract_{int(time.time())}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    # ---- Validate + extract (security checks live in the helpers) ----
    try:
        if lower_name.endswith(".zip"):
            from src.core.pkgdetect import detect_zip_upgrade_kind, mismatch_message

            pkg_kind = detect_zip_upgrade_kind(tmp_pkg)
            if pkg_kind in {"plugin", "go-binary"}:
                hint = mismatch_message(pkg_kind, "system-update")
                if hint:
                    raise ValidationException(hint)
            await run_in_threadpool(_extract_update_package, tmp_pkg, extract_dir, locale)
        else:
            from src.core.pkgdetect import detect_tar_gz_kind, mismatch_message

            pkg_kind = detect_tar_gz_kind(tmp_pkg)
            if pkg_kind in {"plugin", "go-binary"}:
                hint = mismatch_message(pkg_kind, "system-update")
                if hint:
                    raise ValidationException(hint)
            await run_in_threadpool(_extract_update_package, tmp_pkg, extract_dir, locale)
    except tarfile.ReadError:
        raise ValidationException(t("system.extract_failed", locale))
    except zipfile.BadZipFile:
        raise ValidationException(t("system.extract_failed_zip", locale))
    except ValidationException:
        raise
    except Exception as exc:
        raise ValidationException(t("system.extract_error", locale, error=str(exc))) from exc

    # Find the deploy-package root (top-level dir or flat archive)
    pkg_root = _locate_pkg_root(extract_dir)

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

    # ---- Overwrite code (track what was replaced for rollback) ----
    replaced: list[str] = []

    # 1. Copy src/ (backend source)
    src_src = pkg_root / "src"
    src_dst = project_root / "src"
    if src_src.is_dir():
        logger.info("Overwriting src/ ...")
        await run_in_threadpool(_replace_directory, src_src, src_dst)
        replaced.append("src")
        # Deploy packages built from the open-source repo do NOT carry
        # installed plugins (apehub_web, third-party L1 plugins, ...).
        # A full src/ replace would wipe them and take down any site
        # served by those plugins on restart. Restore install-only
        # built-in plugins from the fresh backup.
        restored = await run_in_threadpool(
            _restore_install_only_plugins, backup_dir / "src", src_dst
        )
        if restored:
            logger.info(f"Restored install-only plugins: {restored}")

    # 2. Copy frontend_dist/ (built frontend)
    fe_src = pkg_root / "frontend_dist"
    fe_dst = project_root / "frontend_dist"
    if fe_src.is_dir():
        logger.info("Overwriting frontend_dist/ ...")
        await run_in_threadpool(_replace_directory, fe_src, fe_dst)
        replaced.append("frontend_dist")

    # 3. Copy requirements.txt
    req_src = pkg_root / "requirements.txt"
    req_dst = project_root / "requirements.txt"
    if req_src.is_file():
        logger.info("Overwriting requirements.txt ...")
        shutil.copy2(str(req_src), str(req_dst))
        replaced.append("requirements.txt")

    # 4. Copy scripts/ if present
    scripts_src = pkg_root / "scripts"
    scripts_dst = project_root / "scripts"
    if scripts_src.is_dir():
        logger.info("Overwriting scripts/ ...")
        await run_in_threadpool(_replace_directory, scripts_src, scripts_dst)
        replaced.append("scripts")

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
            # Roll back the replaced files: the old process is still running
            # with the old code in memory, but a restart would load the new
            # code against missing dependencies and crash-loop. Restoring
            # the backup keeps the on-disk state consistent with the
            # running process so a manual restart stays safe.
            await run_in_threadpool(_rollback_backup, backup_dir, project_root, replaced)
            raise ValidationException(
                t("system.update_rolled_back", locale, error=stderr.decode()[:2000])
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
            # The axios interceptor unwraps the envelope to data only, so the
            # human-readable message must also live inside data for the UI.
            "message": t("system.update_complete", locale),
        },
        msg=t("system.update_complete", locale),
    )
