"""System file and folder management API."""

import hashlib
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import require_permission
from src.core.exceptions import AppException, NotFoundException, success_response
from src.db import get_db
from src.models import FileFolder, SystemFile, User

router = APIRouter(prefix="/files", tags=["文件管理"])
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "pdf", "doc", "docx", "xls", "xlsx", "zip", "txt", "csv"}


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


@router.get("/folders/tree")
async def folder_tree(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:list"))]):
    folders = (await db.execute(select(FileFolder).where(FileFolder.deleted_at.is_(None)).order_by(FileFolder.parent_id, FileFolder.name))).scalars().all()
    nodes = {0: {"id": 0, "name": "全部文件", "parent_id": 0, "children": []}}
    for folder in folders:
        nodes[folder.id] = _folder_dict(folder) | {"children": []}
    for folder in folders:
        nodes.setdefault(folder.parent_id, nodes[0])["children"].append(nodes[folder.id])
    return success_response(data=[nodes[0]])


@router.post("/folders")
async def create_folder(body: FolderInput, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:create-folder"))]):
    if not await _folder_exists(db, body.parent_id):
        raise NotFoundException("父文件夹不存在")
    folder = FileFolder(name=_clean_name(body.name), parent_id=body.parent_id, created_by=user.id)
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
    folder = await db.get(FileFolder, folder_id)
    if not folder or folder.deleted_at:
        raise NotFoundException("文件夹不存在")
    has_children = await db.scalar(select(func.count()).select_from(FileFolder).where(FileFolder.parent_id == folder_id, FileFolder.deleted_at.is_(None)))
    has_files = await db.scalar(select(func.count()).select_from(SystemFile).where(SystemFile.folder_id == folder_id, SystemFile.deleted_at.is_(None)))
    if has_children or has_files:
        raise AppException(msg="文件夹不为空，请先移除其中内容", code=409)
    folder.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return success_response(msg="文件夹已删除")


@router.get("")
async def list_files(folder_id: int = Query(0, ge=0), keyword: str = Query("", max_length=100), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("system:file:list"))):
    query = select(SystemFile).where(SystemFile.deleted_at.is_(None), SystemFile.folder_id == folder_id)
    if keyword:
        query = query.where(SystemFile.original_name.contains(keyword))
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (await db.execute(query.order_by(SystemFile.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": [_file_dict(item) for item in items]})


@router.post("/upload")
async def upload_file(folder_id: int = Query(0, ge=0), file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("system:file:upload"))):
    if not await _folder_exists(db, folder_id):
        raise NotFoundException("目标文件夹不存在")
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
    },
    "release-packages": {
        "name": "版本发布包",
        "root": lambda: Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web" / "release-packages",
        "risk": "high",
        "note": "官网安装下载页的安装包，删除后版本无法下载，请谨慎操作",
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
    group: str = Query(..., max_length=40),
    path: str = Query(..., max_length=300),
    user: User = Depends(require_permission("system:file:download")),
):
    """Download an asset file."""
    target = _safe_asset_path(group, path)
    if not target.is_file():
        raise NotFoundException("文件不存在")
    media_type = "application/octet-stream"
    if target.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        media_type = f"image/{target.suffix.lower().lstrip('.')}".replace("jpg", "jpeg")
    return FileResponse(target, media_type=media_type, filename=target.name)


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
async def download_file(file_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(require_permission("system:file:download"))]):
    item = await db.get(SystemFile, file_id)
    if not item or item.deleted_at:
        raise NotFoundException("文件不存在")
    path = (Path(settings.FILE_STORAGE_DIR) / item.storage_key).resolve()
    if not path.is_file() or Path(settings.FILE_STORAGE_DIR).resolve() not in path.parents:
        raise NotFoundException("文件内容不存在")
    return FileResponse(path, media_type=item.mime_type, filename=item.original_name)


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: User = Depends(require_permission("system:file:delete"))):
    item = await db.get(SystemFile, file_id)
    if not item or item.deleted_at:
        raise NotFoundException("文件不存在")
    item.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return success_response(msg="文件已删除")
