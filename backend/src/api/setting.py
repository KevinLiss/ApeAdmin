"""System settings routes: public read + admin CRUD."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import get_current_user, require_permission
from src.core.exceptions import AppException, success_response
from src.crud.setting import crud_setting
from src.db import get_db
from src.models import User
from src.schemas.setting import SettingsBatchUpdate

router = APIRouter(prefix="/settings", tags=["系统设置"])

# Brand images (logo / login background) uploaded from the settings page.
# Stored under uploads/brand and served publicly via /media/brand (mounted
# in create_app) so <img> tags can render them without auth headers.
BRAND_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "svg", "ico"}
MAX_BRAND_IMAGE_SIZE = 10 * 1024 * 1024


@router.get("/public")
async def get_public_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get public settings (no auth required).

    Used by login page, layout sidebar, etc. to render site_name, logo, colors.
    """
    settings = await crud_setting.get_all_public(db)
    return success_response(data=settings)


@router.get("")
async def list_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:setting:list"))],
):
    """Get all settings (admin only)."""
    settings = await crud_setting.get_all(db)
    from src.schemas.setting import SettingOut
    return success_response(data=[
        SettingOut.model_validate(s).model_dump() for s in settings
    ])


@router.put("")
async def update_settings(
    body: SettingsBatchUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:setting:edit"))],
):
    """Batch update settings by key. Only updates existing keys."""
    updated = []
    for key, value in body.items.items():
        existing = await crud_setting.get_by_key(db, key)
        if existing:
            existing.value = value
            updated.append(key)
        else:
            # Create new setting if it doesn't exist
            is_public = key in ("site_name", "logo_url", "primary_color", "footer_text", "theme_mode")
            await crud_setting.upsert(db, key, value, is_public=is_public, category="general", description="")
            updated.append(key)
    await db.commit()
    return success_response(msg=f"已更新 {len(updated)} 项设置", data={"updated": updated})


@router.put("/{key}")
async def update_single_setting(
    key: str,
    body: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:setting:edit"))],
):
    """Update a single setting by key."""
    value = body.get("value", "")
    existing = await crud_setting.get_by_key(db, key)
    if not existing:
        from src.core.exceptions import NotFoundException
        raise NotFoundException(f"设置项 '{key}' 不存在")
    existing.value = value
    await db.commit()
    return success_response(msg=f"设置 '{key}' 已更新")


@router.post("/brand-image")
async def upload_brand_image(
    file: UploadFile = File(...),
    user: User = Depends(require_permission("system:setting:edit")),
):
    """Upload a brand image (logo / login background) and return its public URL.

    Files are stored under ``uploads/brand/`` and served at
    ``/media/brand/<filename>`` (public static mount, no auth) so they can be
    referenced directly by <img> tags on the login page and sidebar.
    """
    original_name = (file.filename or "").strip() or "brand.png"
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in BRAND_IMAGE_EXTENSIONS:
        raise AppException(msg="仅支持图片格式：" + " / ".join(sorted(BRAND_IMAGE_EXTENSIONS)), code=400)
    content = await file.read(MAX_BRAND_IMAGE_SIZE + 1)
    if len(content) > MAX_BRAND_IMAGE_SIZE:
        raise AppException(msg="图片大小不能超过 10MB", code=400)

    import secrets

    brand_dir = Path(settings.FILE_STORAGE_DIR).parent / "brand"
    brand_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(6)}.{extension}"
    (brand_dir / filename).write_bytes(content)
    url = f"/media/brand/{filename}"
    return success_response(data={"url": url}, msg="上传成功")
