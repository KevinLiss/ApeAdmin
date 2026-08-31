"""System settings routes: public read + admin CRUD."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, require_permission
from src.core.exceptions import success_response
from src.crud.setting import crud_setting
from src.db import get_db
from src.models import User
from src.schemas.setting import SettingsBatchUpdate

router = APIRouter(prefix="/settings", tags=["系统设置"])


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
