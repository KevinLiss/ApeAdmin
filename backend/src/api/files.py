"""System file and folder management API."""

import hashlib
import logging
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import AppException, NotFoundException, success_response
from src.db import get_db
from src.models import FileFolder, SystemFile, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["文件管理"])
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "pdf", "doc", "docx", "xls", "xlsx", "zip", "txt", "csv"}
ROOT_FOLDER_NAME = "全部文件"
bearer_scheme = HTTPBearer(auto_error=False)

# Module-level cache of the real root folder id (created lazily).
_root_folder_id: Optional[int] = None


class FolderInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    parent_id: int = Field(default=0, ge=0)


class FolderRename(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)


class MoveInput(BaseModel):
    folder_id: int = Field(..., ge=0)


def _clean_name(name: str) -> str:
    return re.sub(r"[\\/:*?\"<>|]", "_", name).strip() or "未命名文件"


def _folder_dict(folder: FileFolder) -> dict:
    return {"id": folder.id, "name": folder.name, "parent_id": folder.parent_id, "created_at": folder.created_at.isoformat() if folder.created_at else None}


def _file_dict(item: SystemFile) -> dict:
    return {"id": item.id, "folder_id": item.folder_id, "name": item.original_name, "extension": item.extension, "mime_type": item.mime_type, "size": item.size, "md5": item.md5, "uploaded_by": item.uploaded_by, "created_at": item.created_at.isoformat() if item.created_at else None}


async def _folder_exists(db: AsyncSession, folder_id: int) -> bool:
    if folder_id == 0:
        return True
    return await db.scalar(select(func.count()).select_from(FileFolder).where(FileFolder.id == folder_id, FileFolder.deleted_at.is_(None))) > 0


async def _ensure_root_folder(db: AsyncSession) -> int:
    """Return the real root folder id, creating it lazily on first use.

    ``folder_id=0`` means "root" in the UI, but ``sys_file.folder_id`` has a
    foreign key to ``sys_file_folder.id`` (no row with id=0), so on MySQL an
    insert with folder_id=0 raises a foreign-key error. We keep a single real
    "全部文件" row as root and map the virtual 0 onto it.
    """
    global _root_folder_id
    if _root_folder_id is not None:
        # Verify it still exists (e.g. DB reset between restarts).
        if await db.get(FileFolder, _root_folder_id) is not None:
            return _root_folder_id
        _root_folder_id = None
    existing = (await db.execute(
        select(FileFolder).where(FileFolder.name == ROOT_FOLDER_NAME, FileFolder.parent_id == 0, FileFolder.deleted_at.is_(None))
    )).scalar_one_or_none()
    if existing is not None:
        _root_folder_id = existing.id
        return existing.id
    root = FileFolder(name=ROOT_FOLDER_NAME, parent_id=0, created_by=1)
    db.add(root)
    await db.commit()
    await db.refresh(root)
    _root_folder_id = root.id
    return root.id


async def _normalize_folder_id(db: AsyncSession, folder_id: int) -> int:
    """Map ``0`` (UI root) to the real root folder id; validate others."""
    if folder_id == 0:
        return await _ensure_root_folder(db)
    if not await _folder_exists(db, folder_id):
        raise NotFoundException("目标文件夹不存在")
    return folder_id


async def _download_auth(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Auth dependency for downloads: accepts Bearer header OR ?token= query.

    Keeps the same JWT + permission model, but tolerates query-string tokens
    so the frontend can use plain <a href> direct-download links.
    """
    from src.core.deps import get_current_user
    from src.core.exceptions import AuthException

    if credentials is not None:
        return await get_current_user(request, credentials, db)
    token = request.query_params.get("token")
    if not token:
        raise AuthException("Missing authentication token")
    from src.core.security import decode_token

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise AuthException("Invalid or expired token")
    from src.crud import crud_user

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException("Invalid token payload")
    user = await crud_user.get(db, int(user_id))
    if not user:
        raise AuthException("User not found")
    if user.status != 1:
        raise AuthException("Account disabled")
    request.state.user = user
    # Permission check (same as require_permission, kept local to avoid
    # re-injecting the header-only dependency).
    from src.core.config import settings as _settings
    from src.core.exceptions import PermissionException

    if user.username != _settings.SUPER_ADMIN_USERNAME:
        user_permissions: set[str] = set()
        for role in user.roles:
            for menu in role.menus:
                if menu.permission:
                    user_permissions.add(menu.permission)
        if "system:file:download" not in user_permissions:
            raise PermissionException("无下载权限")
    return user


@router.get("/folders/tree")
async def folder_tree(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:list"))]):
    root_id = await _ensure_root_folder(db)
    folders = (await db.execute(select(FileFolder).where(FileFolder.deleted_at.is_(None)).order_by(FileFolder.parent_id, FileFolder.name))).scalars().all()
    nodes = {root_id: {"id": root_id, "name": ROOT_FOLDER_NAME, "parent_id": 0, "children": []}}
    for folder in folders:
        nodes[folder.id] = _folder_dict(folder) | {"children": []}
    for folder in folders:
        if folder.parent_id in nodes:
            nodes[folder.parent_id]["children"].append(nodes[folder.id])
    return success_response(data=[nodes[root_id]])


@router.post("/folders")
async def create_folder(body: FolderInput, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:create-folder"))]):
    parent_id = await _normalize_folder_id(db, body.parent_id)
    folder = FileFolder(name=_clean_name(body.name), parent_id=parent_id, created_by=user.id)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return success_response(data=_folder_dict(folder), msg="文件夹创建成功")


@router.put("/folders/{folder_id}")
async def rename_folder(folder_id: int, body: FolderRename, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:rename"))]):
    folder = await db.get(FileFolder, folder_id)
    if not folder or folder.deleted_at:
        raise NotFoundException("文件夹不存在")
    folder.name = _clean_name(body.name)
    await db.commit()
    return success_response(msg="文件夹已重命名")


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:delete"))]):
    """Delete a folder cascading to its whole subtree (folders + files).

    All files under the subtree are soft-deleted (deleted_at) and their
    physical blobs removed best-effort. The response carries the affected
    counts so the frontend can show them to the user beforehand.
    """
    folder = await db.get(FileFolder, folder_id)
    if not folder or folder.deleted_at:
        raise NotFoundException("文件夹不存在")
    root_id = await _ensure_root_folder(db)
    if folder_id == root_id:
        raise AppException(msg="根文件夹不可删除", code=400)
    # Collect the whole subtree of folder ids (BFS over parent_id).
    all_folders = (await db.execute(
        select(FileFolder).where(FileFolder.deleted_at.is_(None))
    )).scalars().all()
    children_map: dict[int, list[int]] = {}
    for f in all_folders:
        children_map.setdefault(f.parent_id, []).append(f.id)
    to_delete: list[int] = []
    queue = [folder_id]
    while queue:
        cur = queue.pop(0)
        to_delete.append(cur)
        queue.extend(children_map.get(cur, []))
    folder_count = len(to_delete)
    # All files living in any of these folders.
    files = (await db.execute(
        select(SystemFile).where(SystemFile.folder_id.in_(to_delete), SystemFile.deleted_at.is_(None))
    )).scalars().all()
    file_count = len(files)
    now = datetime.now(timezone.utc)
    for fid in to_delete:
        f = await db.get(FileFolder, fid)
        if f:
            f.deleted_at = now
    for item in files:
        item.deleted_at = now
    await db.commit()
    # Best-effort physical removal of the file blobs.
    storage_root = Path(settings.FILE_STORAGE_DIR).resolve()
    for item in files:
        try:
            path = (storage_root / item.storage_key).resolve()
            if path.is_file() and (storage_root == path.parent or storage_root in path.parents):
                path.unlink()
                parent = path.parent
                for _ in range(2):
                    if parent == storage_root:
                        break
                    try:
                        parent.rmdir()
                    except OSError:
                        break
                    parent = parent.parent
        except OSError as exc:
            logger.warning("级联删除物理文件失败 file_id=%s storage_key=%s: %s", item.id, item.storage_key, exc)
    return success_response(data={"folder_count": folder_count, "file_count": file_count}, msg=f"已删除文件夹及其下 {file_count} 个文件")


@router.get("")
async def list_files(folder_id: int = Query(0, ge=0), keyword: str = Query("", max_length=100), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("system:file:list"))):
    folder_id = await _normalize_folder_id(db, folder_id)
    query = select(SystemFile).where(SystemFile.deleted_at.is_(None), SystemFile.folder_id == folder_id)
    if keyword:
        query = query.where(SystemFile.original_name.contains(keyword))
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (await db.execute(query.order_by(SystemFile.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": [_file_dict(item) for item in items]})


@router.post("/upload")
async def upload_file(folder_id: int = Query(0, ge=0), file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("system:file:upload"))):
    folder_id = await _normalize_folder_id(db, folder_id)
    original_name = _clean_name(file.filename or "未命名文件")
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise AppException(msg="不支持的文件类型", code=400)
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise AppException(msg="文件大小不能超过 50MB", code=400)
    digest = hashlib.md5(content).hexdigest()
    stored_name = f"{secrets.token_hex(16)}.{extension}" if extension else secrets.token_hex(16)
    relative = Path(datetime.now(timezone.utc).strftime("%Y/%m")) / stored_name
    root = Path(settings.FILE_STORAGE_DIR)
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    item = SystemFile(folder_id=folder_id, original_name=original_name, stored_name=stored_name, storage_key=str(relative), extension=extension, mime_type=file.content_type or "application/octet-stream", size=len(content), md5=digest, uploaded_by=user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return success_response(data=_file_dict(item), msg="文件上传成功")


# ---------------------------------------------------------------------------
# Asset storage browsing (read/delete over physical upload directories)
# ---------------------------------------------------------------------------

ASSET_GROUPS: dict[str, dict] = {
    "brand": {
        "name": "品牌图片",
        "root": lambda: Path(settings.FILE_STORAGE_DIR).parent / "brand",
        "risk": "low",
        "note": "登录页 Logo / 背景，删除后需重新上传",
    },
    "site-assets": {
        "name": "官网站点素材",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web" / "site-assets",
        "risk": "low",
        "note": "官网内容引用的图片，删除后对应位置显示破图",
    },
    "plugin-media": {
        "name": "插件媒体",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web" / "plugin-media",
        "risk": "low",
        "note": "插件市场图标 / 截图 / 二维码",
    },
    "plugins": {
        "name": "插件安装包",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web" / "plugins",
        "risk": "high",
        "note": "插件市场安装包，删除后插件无法下载，请谨慎操作",
        "hidden": True,  # 业务文件，由插件管理页专门维护，不在文件管理侧边栏展示
    },
    "release-packages": {
        "name": "版本发布包",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web" / "release-packages",
        "risk": "high",
        "note": "官网安装下载页的安装包，删除后版本无法下载，请谨慎操作",
        "hidden": True,  # 业务文件，由版本发布页专门维护，不在文件管理侧边栏展示
    },
    "system-plugins": {
        "name": "底座插件包",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR),
        "risk": "medium",
        "note": "底座插件上传的临时包，正常情况下安装后可清理",
    },
}


def _asset_root(group: str) -> Path:
    """Resolve a group's root directory, raising 404 for unknown groups."""
    if group not in ASSET_GROUPS:
        raise NotFoundException("素材分组不存在")
    return ASSET_GROUPS[group]["root"]()


def _safe_asset_path(group: str, relative: str) -> Path:
    """Join a relative path onto the group root with traversal protection."""
    root = _asset_root(group).resolve()
    candidate = (root / relative).resolve()
    if root != candidate and root not in candidate.parents:
        raise NotFoundException("非法路径")
    return candidate


def _asset_file_dict(path: Path, root: Path) -> dict:
    stat = path.stat()
    rel = path.relative_to(root).as_posix()
    return {
        "path": rel,
        "name": path.name,
        "extension": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def _asset_dir_dict(path: Path, root: Path) -> dict:
    rel = path.relative_to(root).as_posix()
    return {"path": rel, "name": path.name}


@router.get("/assets/groups")
async def asset_groups(user: User = Depends(require_permission("system:file:list"))):
    """List asset storage groups (physical upload directories)."""
    data = []
    for key, conf in ASSET_GROUPS.items():
        if conf.get("hidden"):
            continue
        root = conf["root"]()
        file_count = 0
        total_size = 0
        if root.is_dir():
            for p in root.rglob("*"):
                if p.is_file():
                    file_count += 1
                    try:
                        total_size += p.stat().st_size
                    except OSError:
                        pass
        data.append({
            "key": key,
            "name": conf["name"],
            "risk": conf["risk"],
            "note": conf["note"],
            "exists": root.is_dir(),
            "file_count": file_count,
            "total_size": total_size,
        })
    return success_response(data=data)


@router.get("/assets/list")
async def list_assets(
    group: str = Query(..., max_length=40),
    path: str = Query("", max_length=300),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("system:file:list")),
):
    """List sub-directories and files under an asset directory."""
    root = _asset_root(group)
    if not root.is_dir():
        return success_response(data={"dirs": [], "files": []})
    target = _safe_asset_path(group, path)
    if not target.is_dir():
        raise NotFoundException("目录不存在")
    dirs, files = [], []
    for entry in sorted(target.iterdir(), key=lambda p: p.name):
        if entry.is_dir():
            dirs.append(_asset_dir_dict(entry, root))
        elif entry.is_file():
            files.append(_asset_file_dict(entry, root))
    files.sort(key=lambda f: f["name"])
    return success_response(data={"dirs": dirs, "files": files})


@router.get("/assets/download")
async def download_asset(
    user: Annotated[User, Depends(_download_auth)],
    group: str = Query(..., max_length=40),
    path: str = Query(..., max_length=300),
    preview: int = Query(0, ge=0, le=1),
):
    """Download an asset file (preview=1 returns inline for direct rendering)."""
    target = _safe_asset_path(group, path)
    if not target.is_file():
        raise NotFoundException("文件不存在")
    media_type = "application/octet-stream"
    suffix = target.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}:
        media_type = f"image/{suffix.lstrip('.')}".replace("jpg", "jpeg")
    elif suffix == ".pdf":
        media_type = "application/pdf"
    elif suffix in {".txt", ".md", ".csv", ".json", ".log", ".xml", ".yml", ".yaml"}:
        media_type = "text/plain; charset=utf-8"
    return FileResponse(target, media_type=media_type, filename=target.name, content_disposition_type="inline" if preview else "attachment")


@router.delete("/assets")
async def delete_asset(
    group: str = Query(..., max_length=40),
    path: str = Query(..., max_length=300),
    user: User = Depends(require_permission("system:file:delete")),
):
    """Delete an asset file (single file only, directories rejected)."""
    target = _safe_asset_path(group, path)
    if not target.is_file():
        raise NotFoundException("文件不存在")
    try:
        target.unlink()
        # 清理空的父目录（最多向上清 2 层，保留分组根目录）
        parent = target.parent
        root = ASSET_GROUPS[group]["root"]().resolve()
        for _ in range(2):
            if parent == root or root not in parent.parents:
                break
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    except OSError as exc:
        raise AppException(msg=f"删除失败：{exc}", code=500)
    return success_response(msg="文件已删除")


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(_download_auth)],
    preview: int = Query(0, ge=0, le=1),
):
    item = await db.get(SystemFile, file_id)
    if not item or item.deleted_at:
        raise NotFoundException("文件不存在")
    path = (Path(settings.FILE_STORAGE_DIR) / item.storage_key).resolve()
    if not path.is_file() or Path(settings.FILE_STORAGE_DIR).resolve() not in path.parents:
        raise NotFoundException("文件内容不存在")
    media_type = item.mime_type or "application/octet-stream"
    # preview=1 → Content-Disposition: inline,浏览器直接渲染图片/PDF/文本
    return FileResponse(path, media_type=media_type, filename=item.original_name, content_disposition_type="inline" if preview else "attachment")


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: User = Depends(require_permission("system:file:delete"))):
    item = await db.get(SystemFile, file_id)
    if not item or item.deleted_at:
        raise NotFoundException("文件不存在")
    item.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    # Physically remove the stored blob when possible (non-blocking on failure).
    try:
        path = (Path(settings.FILE_STORAGE_DIR) / item.storage_key).resolve()
        root = Path(settings.FILE_STORAGE_DIR).resolve()
        if path.is_file() and (root == path.parent or root in path.parents):
            path.unlink()
            # Clean up now-empty year/month parent dirs (best effort).
            for _ in range(2):
                if path.parent == root:
                    break
                try:
                    path.parent.rmdir()
                except OSError:
                    break
                path = path.parent
    except OSError as exc:
        logger.warning("物理删除文件失败 file_id=%s storage_key=%s: %s", file_id, item.storage_key, exc)
    return success_response(msg="文件已删除")


@router.post("/{file_id}/move")
async def move_file(file_id: int, body: MoveInput, db: Annotated[AsyncSession, Depends(get_db)], user: User = Depends(require_permission("system:file:move"))):
    """Move a file into another folder."""
    item = await db.get(SystemFile, file_id)
    if not item or item.deleted_at:
        raise NotFoundException("文件不存在")
    target_id = await _normalize_folder_id(db, body.folder_id)
    if target_id == item.folder_id:
        return success_response(msg="文件已在目标文件夹")
    item.folder_id = target_id
    await db.commit()
    return success_response(msg="文件已移动")


@router.post("/folders/{folder_id}/move")
async def move_folder(folder_id: int, body: MoveInput, db: Annotated[AsyncSession, Depends(get_db)], user: User = Depends(require_permission("system:file:move"))):
    """Move a folder (and its subtree) under another folder (or root)."""
    folder = await db.get(FileFolder, folder_id)
    if not folder or folder.deleted_at:
        raise NotFoundException("文件夹不存在")
    if folder_id == (await _ensure_root_folder(db)):
        raise AppException(msg="根文件夹不可移动", code=400)
    target_id = await _normalize_folder_id(db, body.folder_id)
    if target_id == folder_id:
        raise AppException(msg="不能移动到自身", code=400)
    # Prevent moving into its own subtree (would create a cycle).
    ancestor = target_id
    while ancestor:
        if ancestor == folder_id:
            raise AppException(msg="不能移动到自身子文件夹中", code=400)
        if ancestor == 0:
            break
        parent = await db.get(FileFolder, ancestor)
        if not parent or parent.deleted_at:
            break
        ancestor = parent.parent_id
    folder.parent_id = target_id
    await db.commit()
    return success_response(msg="文件夹已移动")
