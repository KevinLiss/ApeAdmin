"""ApeHub official website API routes.

Two surfaces are provided:
- Public website (免登录): site config/content, docs, plugin marketplace, register/login
- Admin management (需登录 + 超级管理员/权限): content/config/doc/plugin review/payment/user

Auth reuses ApeAdmin's sys_user + JWT. Public endpoints are deliberately
independent of `get_current_user` so the /site/* pages work without a token.
"""

import asyncio
import os
import secrets
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import get_current_user
from src.core.exceptions import (
    AuthException,
    ConflictException,
    NotFoundException,
    PermissionException,
    ValidationException,
    success_response,
)
from src.core.security import create_access_token, hash_password
from src.crud import crud_user
from src.db import get_db
from src.models import User
from src.plugins.builtin.apehub_web import services
from src.plugins.builtin.apehub_web.models import (
    ApehubWebDoc,
    ApehubWebDocCategory,
    ApehubWebEmailVerification,
    ApehubWebIncome,
    ApehubWebOrder,
    ApehubWebPlugin,
    ApehubWebPluginDemo,
    ApehubWebPluginFile,
    ApehubWebProfile,
    ApehubWebSiteConfig,
    ApehubWebSiteContent,
    ApehubWebWithdrawal,
    DemoType,
    OrderStatus,
    PluginStatus,
    WithdrawalStatus,
)
from src.plugins.builtin.apehub_web.schemas import (
    DocCategoryIn,
    DocIn,
    PluginReviewIn,
    PluginSubmitIn,
    ProfileUpdateIn,
    PurchaseIn,
    SiteConfigIn,
    SiteContentIn,
    WithdrawIn,
)

router = APIRouter(prefix="/apehub-web", tags=["Apehub_web"])

# Keep plugin uploads beside ApeAdmin's existing plugin upload directory.
UPLOAD_ROOT = str(Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health")
async def health_check():
    """Lightweight route used to confirm the plugin router is registered."""
    return success_response(data={"plugin": "apehub_web", "status": "ok"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _is_admin(user: User) -> bool:
    if user.username == settings.SUPER_ADMIN_USERNAME:
        return True
    return any(r.code == "admin" for r in user.roles)


async def _require_permission(user: User, permission: str) -> None:
    """Require the same plugin permission that is declared in the menu tree."""
    if user.username == settings.SUPER_ADMIN_USERNAME:
        return
    permissions = {
        menu.permission
        for role in user.roles
        if role.status == 1
        for menu in role.menus
        if menu.status == 1 and menu.permission
    }
    if permission not in permissions:
        raise PermissionException(f"缺少权限：{permission}")


async def _get_site_config(db: AsyncSession) -> ApehubWebSiteConfig:
    """Get (or lazily create) the singleton site config row."""
    result = await db.execute(select(ApehubWebSiteConfig).limit(1))
    cfg = result.scalar_one_or_none()
    if cfg is None:
        cfg = ApehubWebSiteConfig()
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    return cfg


async def _get_or_create_profile(db: AsyncSession, user: User) -> ApehubWebProfile:
    result = await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == user.id))
    prof = result.scalar_one_or_none()
    if prof is None:
        prof = ApehubWebProfile(user_id=user.id, nickname=user.nickname or user.username)
        db.add(prof)
        await db.commit()
        await db.refresh(prof)
    return prof


def _plugin_summary(p: ApehubWebPlugin, with_demos: bool = False) -> dict[str, Any]:
    """Serialize a plugin row for list/detail responses."""
    data: dict[str, Any] = {
        "id": p.id,
        "developer_id": p.developer_id,
        "name": p.name,
        "display_name": p.display_name,
        "slug": p.slug,
        "description": p.description,
        "category": p.category,
        "version": p.version,
        "tags": p.tags,
        "icon": p.icon,
        "price": p.price,
        "service_fee_rate": p.service_fee_rate,
        "status": p.status.value,
        "download_count": p.download_count,
        "rating_avg": p.rating_avg,
        "rating_count": p.rating_count,
        "reject_reason": p.reject_reason,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    if with_demos:
        data["demos"] = [
            {
                "id": d.id,
                "demo_type": d.demo_type.value,
                "title": d.title,
                "url": d.url,
                "qr_image": d.qr_image,
            }
            for d in p.demos
        ]
    return data


# ---------------------------------------------------------------------------
# Public website (公开访问)
# ---------------------------------------------------------------------------

@router.get("/site/public/config")
async def public_site_config(db: Annotated[AsyncSession, Depends(get_db)]):
    """Public site config (no secrets: no mail_code / lempay_key)."""
    cfg = await _get_site_config(db)
    return success_response(data={
        "site_name": cfg.site_name,
        "site_logo": cfg.site_logo,
        "site_domain": cfg.site_domain,
        "site_prefix": cfg.site_prefix,
        "seo_title": cfg.seo_title,
        "seo_description": cfg.seo_description,
        "seo_keywords": cfg.seo_keywords,
        "service_fee_rate": cfg.service_fee_rate,
    })


@router.get("/site/public/content")
async def public_site_content(db: Annotated[AsyncSession, Depends(get_db)]):
    """All enabled site content blocks grouped by block_key."""
    result = await db.execute(
        select(ApehubWebSiteContent).where(ApehubWebSiteContent.enabled.is_(True)).order_by(ApehubWebSiteContent.sort)
    )
    blocks: dict[str, list[dict]] = {}
    for c in result.scalars().all():
        blocks.setdefault(c.block_key, []).append({
            "id": c.id,
            "block_key": c.block_key,
            "title": c.title,
            "subtitle": c.subtitle,
            "body": c.body,
            "image": c.image,
            "sort": c.sort,
            "extra": c.extra or {},
        })
    return success_response(data=blocks)


# --- Docs (public) ---

@router.get("/site/public/docs/categories")
async def public_doc_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(ApehubWebDocCategory).order_by(ApehubWebDocCategory.sort.asc(), ApehubWebDocCategory.id.asc())
    )
    return success_response(data=[
        {"id": c.id, "name": c.name, "description": c.description, "sort": c.sort}
        for c in result.scalars().all()
    ])


@router.get("/site/public/docs")
async def public_docs(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(ApehubWebDoc).where(ApehubWebDoc.published.is_(True))
    if category_id:
        stmt = stmt.where(ApehubWebDoc.category_id == category_id)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ApehubWebDoc.title.like(like), ApehubWebDoc.summary.like(like), ApehubWebDoc.body.like(like)))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebDoc.sort.asc(), ApehubWebDoc.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = [
        {
            "id": d.id,
            "category_id": d.category_id,
            "category_name": d.category.name if d.category else None,
            "title": d.title,
            "slug": d.slug,
            "summary": d.summary,
            "version": d.version,
            "view_count": d.view_count,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in result.scalars().all()
    ]
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/site/public/docs/{doc_id}")
async def public_doc_detail(doc_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(ApehubWebDoc).where(ApehubWebDoc.id == doc_id, ApehubWebDoc.published.is_(True)))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundException("文档不存在")
    await db.execute(update(ApehubWebDoc).where(ApehubWebDoc.id == doc.id).values(view_count=ApehubWebDoc.view_count + 1))
    await db.commit()
    return success_response(data={
        "id": doc.id,
        "category_id": doc.category_id,
        "category_name": doc.category.name if doc.category else None,
        "title": doc.title,
        "slug": doc.slug,
        "summary": doc.summary,
        "body": doc.body,
        "version": doc.version,
        "author": doc.author,
        "view_count": doc.view_count + 1,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    })


# ---------------------------------------------------------------------------
# Site config / content admin
# ---------------------------------------------------------------------------

@router.get("/admin/config")
async def get_site_config(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:list")
    cfg = await _get_site_config(db)
    return success_response(data={
        "id": cfg.id,
        "site_name": cfg.site_name,
        "site_logo": cfg.site_logo,
        "site_domain": cfg.site_domain,
        "site_prefix": cfg.site_prefix,
        "seo_title": cfg.seo_title,
        "seo_description": cfg.seo_description,
        "seo_keywords": cfg.seo_keywords,
        "mail_user": cfg.mail_user,
        "mail_host": cfg.mail_host,
        "mail_port": cfg.mail_port,
        "lempay_pid": cfg.lempay_pid,
        "lempay_api_url": cfg.lempay_api_url,
        "lempay_submit_url": cfg.lempay_submit_url,
        "lempay_notify_url": cfg.lempay_notify_url,
        "lempay_return_url": cfg.lempay_return_url,
        "service_fee_rate": cfg.service_fee_rate,
    })


@router.put("/admin/config")
async def update_site_config(
    body: SiteConfigIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:edit")
    cfg = await _get_site_config(db)
    payload = body.model_dump(exclude_unset=True, exclude_none=True)
    for secret in ("mail_code", "lempay_key"):
        if payload.get(secret) == "":
            payload.pop(secret)
    # Normalize site_prefix: must start with "/" and not end with "/"
    if "site_prefix" in payload:
        prefix = payload["site_prefix"].strip() or "/site"
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        payload["site_prefix"] = prefix.rstrip("/")
    for k, v in payload.items():
        setattr(cfg, k, v)
    await db.commit()
    await db.refresh(cfg)
    return success_response(data={"id": cfg.id}, msg="配置已保存")


@router.get("/admin/content")
async def list_site_content(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:content:list")
    result = await db.execute(select(ApehubWebSiteContent).order_by(ApehubWebSiteContent.block_key.asc(), ApehubWebSiteContent.sort.asc()))
    return success_response(data=[
        {
            "id": c.id, "block_key": c.block_key, "title": c.title,
            "subtitle": c.subtitle, "body": c.body, "image": c.image,
            "sort": c.sort, "enabled": c.enabled, "extra": c.extra or {},
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in result.scalars().all()
    ])


@router.post("/admin/content")
async def create_site_content(
    body: SiteContentIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:content:edit")
    content = ApehubWebSiteContent(**body.model_dump())
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return success_response(data={"id": content.id}, msg="内容已创建")


@router.put("/admin/content/{content_id}")
async def update_site_content(
    content_id: int,
    body: SiteContentIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:content:edit")
    content = await db.get(ApehubWebSiteContent, content_id)
    if not content:
        raise NotFoundException("内容不存在")
    payload = body.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(content, k, v)
    await db.commit()
    return success_response(msg="内容已更新")


@router.delete("/admin/content/{content_id}")
async def delete_site_content(
    content_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:content:edit")
    content = await db.get(ApehubWebSiteContent, content_id)
    if not content:
        raise NotFoundException("内容不存在")
    await db.delete(content)
    await db.commit()
    return success_response(msg="内容已删除")


# ---------------------------------------------------------------------------
# Docs admin (分类 + 文档 CRUD)
# ---------------------------------------------------------------------------

@router.get("/admin/doc-categories")
async def list_doc_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:list")
    result = await db.execute(select(ApehubWebDocCategory).order_by(ApehubWebDocCategory.sort.asc()))
    return success_response(data=[
        {"id": c.id, "name": c.name, "description": c.description, "sort": c.sort}
        for c in result.scalars().all()
    ])


@router.post("/admin/doc-categories")
async def create_doc_category(
    body: DocCategoryIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:edit")
    cat = ApehubWebDocCategory(**body.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return success_response(data={"id": cat.id}, msg="分类已创建")


@router.put("/admin/doc-categories/{cat_id}")
async def update_doc_category(
    cat_id: int,
    body: DocCategoryIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:edit")
    cat = await db.get(ApehubWebDocCategory, cat_id)
    if not cat:
        raise NotFoundException("分类不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    await db.commit()
    return success_response(msg="分类已更新")


@router.delete("/admin/doc-categories/{cat_id}")
async def delete_doc_category(
    cat_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:edit")
    cat = await db.get(ApehubWebDocCategory, cat_id)
    if not cat:
        raise NotFoundException("分类不存在")
    docs = await db.execute(select(func.count()).select_from(ApehubWebDoc).where(ApehubWebDoc.category_id == cat_id))
    if (docs.scalar() or 0) > 0:
        raise ConflictException("分类下存在文档，请先移动或删除")
    await db.delete(cat)
    await db.commit()
    return success_response(msg="分类已删除")


@router.get("/admin/docs")
async def list_docs(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    await _require_permission(user, "apehub_web:docs:list")
    stmt = select(ApehubWebDoc)
    if category_id:
        stmt = stmt.where(ApehubWebDoc.category_id == category_id)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ApehubWebDoc.title.like(like), ApehubWebDoc.summary.like(like)))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebDoc.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = [
        {
            "id": d.id, "category_id": d.category_id,
            "category_name": d.category.name if d.category else None,
            "title": d.title, "slug": d.slug, "summary": d.summary,
            "version": d.version, "published": d.published, "sort": d.sort,
            "view_count": d.view_count,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in result.scalars().all()
    ]
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.post("/admin/docs")
async def create_doc(
    body: DocIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:edit")
    if not body.slug.strip():
        body.slug = services.gen_slug(body.title)
    existing = await db.execute(select(ApehubWebDoc).where(ApehubWebDoc.slug == body.slug))
    if existing.scalar_one_or_none():
        raise ConflictException("slug 已存在")
    doc = ApehubWebDoc(**body.model_dump(), author=user.username)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return success_response(data={"id": doc.id}, msg="文档已创建")


@router.get("/admin/docs/{doc_id}")
async def get_doc(doc_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    await _require_permission(user, "apehub_web:docs:list")
    doc = await db.get(ApehubWebDoc, doc_id)
    if not doc:
        raise NotFoundException("文档不存在")
    return success_response(data={
        "id": doc.id, "category_id": doc.category_id, "title": doc.title,
        "slug": doc.slug, "summary": doc.summary, "body": doc.body,
        "version": doc.version, "author": doc.author, "published": doc.published,
        "sort": doc.sort, "view_count": doc.view_count,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    })


@router.put("/admin/docs/{doc_id}")
async def update_doc(
    doc_id: int,
    body: DocIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:docs:edit")
    doc = await db.get(ApehubWebDoc, doc_id)
    if not doc:
        raise NotFoundException("文档不存在")
    payload = body.model_dump(exclude_unset=True)
    if "slug" in payload and payload["slug"] != doc.slug:
        existing = await db.execute(select(ApehubWebDoc).where(ApehubWebDoc.slug == payload["slug"], ApehubWebDoc.id != doc_id))
        if existing.scalar_one_or_none():
            raise ConflictException("slug 已存在")
    for k, v in payload.items():
        setattr(doc, k, v)
    await db.commit()
    return success_response(msg="文档已更新")


@router.delete("/admin/docs/{doc_id}")
async def delete_doc(doc_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    await _require_permission(user, "apehub_web:docs:edit")
    doc = await db.get(ApehubWebDoc, doc_id)
    if not doc:
        raise NotFoundException("文档不存在")
    await db.delete(doc)
    await db.commit()
    return success_response(msg="文档已删除")


# ---------------------------------------------------------------------------
# Marketplace (public browse + developer submit + admin review)
# ---------------------------------------------------------------------------

@router.get("/site/public/plugins")
async def public_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(ApehubWebPlugin).where(ApehubWebPlugin.status == PluginStatus.APPROVED)
    if category:
        stmt = stmt.where(ApehubWebPlugin.category == category)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(ApehubWebPlugin.display_name.like(like), ApehubWebPlugin.description.like(like), ApehubWebPlugin.tags.like(like)))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebPlugin.download_count.desc(), ApehubWebPlugin.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = [_plugin_summary(p) for p in result.scalars().all()]
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/site/public/plugins/categories")
async def public_plugin_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(ApehubWebPlugin.category, func.count())
        .where(ApehubWebPlugin.status == PluginStatus.APPROVED)
        .group_by(ApehubWebPlugin.category)
    )
    return success_response(data=[{"name": name, "count": cnt} for name, cnt in result.all()])


@router.get("/site/public/plugins/{plugin_id}")
async def public_plugin_detail(plugin_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin or plugin.status != PluginStatus.APPROVED:
        raise NotFoundException("插件不存在或未上架")
    data = _plugin_summary(plugin, with_demos=True)
    # File metadata (no download path leak for paid plugins)
    data["files"] = [
        {"id": f.id, "file_type": f.file_type, "filename": f.filename, "size": f.size}
        for f in plugin.files
    ]
    return success_response(data=data)


# Developer submit
@router.post("/developer/plugins")
async def submit_plugin(
    body: PluginSubmitIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    prof = await _get_or_create_profile(db, user)
    prof.is_developer = True
    slug = services.gen_slug(body.name)
    existing = await db.execute(select(ApehubWebPlugin).where(ApehubWebPlugin.slug == slug))
    if existing.scalar_one_or_none():
        raise ConflictException("插件名称已存在，请更换")
    cfg = await _get_site_config(db)
    default_rate = cfg.service_fee_rate if cfg else 30.0
    plugin = ApehubWebPlugin(
        developer_id=user.id,
        name=body.name,
        display_name=body.display_name,
        slug=slug,
        description=body.description,
        category=body.category,
        version=body.version,
        tags=body.tags,
        price=body.price,
        service_fee_rate=body.service_fee_rate if body.service_fee_rate is not None else default_rate,
    )
    db.add(plugin)
    await db.flush()
    for demo in body.demos or []:
        db.add(ApehubWebPluginDemo(plugin_id=plugin.id, demo_type=demo.demo_type, title=demo.title, url=demo.url, qr_image=demo.qr_image))
    await db.commit()
    await db.refresh(plugin)
    return success_response(data={"id": plugin.id, "slug": plugin.slug}, msg="插件已提交，等待审核")


@router.get("/developer/plugins")
async def my_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(ApehubWebPlugin).where(ApehubWebPlugin.developer_id == user.id).order_by(ApehubWebPlugin.id.desc())
    )
    return success_response(data=[_plugin_summary(p) for p in result.scalars().all()])


@router.get("/developer/plugins/{plugin_id}")
async def my_plugin_detail(plugin_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin or plugin.developer_id != user.id:
        raise NotFoundException("插件不存在")
    data = _plugin_summary(plugin, with_demos=True)
    data["files"] = [
        {"id": f.id, "file_type": f.file_type, "filename": f.filename, "size": f.size, "stored_path": f.stored_path}
        for f in plugin.files
    ]
    return success_response(data=data)


@router.put("/developer/plugins/{plugin_id}")
async def update_my_plugin(
    plugin_id: int,
    body: PluginSubmitIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin or plugin.developer_id != user.id:
        raise NotFoundException("插件不存在")
    if plugin.status == PluginStatus.APPROVED:
        raise ValidationException("已上架插件请先联系管理员下架后再编辑")
    payload = body.model_dump(exclude_unset=True)
    if "slug" in payload:
        payload.pop("slug", None)
    for k, v in payload.items():
        if k in ("name",):
            v = services.gen_slug(v)
            plugin.slug = v
        setattr(plugin, k, v)
    # replace demos
    await db.execute(update(ApehubWebPluginDemo).where(ApehubWebPluginDemo.plugin_id == plugin_id).values())
    # simple: delete + recreate
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(ApehubWebPluginDemo).where(ApehubWebPluginDemo.plugin_id == plugin_id))
    for demo in body.demos or []:
        db.add(ApehubWebPluginDemo(plugin_id=plugin_id, demo_type=demo.demo_type, title=demo.title, url=demo.url, qr_image=demo.qr_image))
    await db.commit()
    return success_response(msg="插件已更新")


@router.post("/developer/plugins/{plugin_id}/files")
async def upload_plugin_file(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(...)],
    file_type: str = Query("package", pattern="^(package|doc|screenshot)$"),
):
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin or plugin.developer_id != user.id:
        raise NotFoundException("插件不存在")
    _ensure_dir(os.path.join(UPLOAD_ROOT, "plugins"))
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    stored = f"plugins/{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_ROOT, stored)
    size = 0
    with open(dest, "wb") as fh:
        while chunk := await file.read(1024 * 1024):
            fh.write(chunk)
            size += len(chunk)
    import hashlib
    md5 = ""
    try:
        with open(dest, "rb") as fh:
            md5 = hashlib.md5(fh.read()).hexdigest()
    except OSError:
        pass
    row = ApehubWebPluginFile(
        plugin_id=plugin_id, file_type=file_type,
        filename=file.filename or stored, stored_path=stored, size=size, md5=md5,
    )
    db.add(row)
    await db.commit()
    return success_response(data={"id": row.id, "filename": row.filename, "size": size}, msg="文件上传成功")


@router.delete("/developer/plugins/{plugin_id}/files/{file_id}")
async def delete_plugin_file(
    plugin_id: int, file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin or plugin.developer_id != user.id:
        raise NotFoundException("插件不存在")
    f = await db.get(ApehubWebPluginFile, file_id)
    if not f or f.plugin_id != plugin_id:
        raise NotFoundException("文件不存在")
    path = os.path.join(UPLOAD_ROOT, f.stored_path)
    if os.path.exists(path):
        os.remove(path)
    await db.delete(f)
    await db.commit()
    return success_response(msg="文件已删除")


# ---------------------------------------------------------------------------
# Admin review / marketplace management
# ---------------------------------------------------------------------------

@router.get("/admin/plugins")
async def admin_list_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    await _require_permission(user, "apehub_web:plugins:review")
    stmt = select(ApehubWebPlugin)
    if status:
        try:
            stmt = stmt.where(ApehubWebPlugin.status == PluginStatus(status))
        except ValueError:
            raise ValidationException("无效的筛选状态")
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebPlugin.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = []
    for p in result.scalars().all():
        d = _plugin_summary(p, with_demos=True)
        d["developer"] = None
        dev = await db.get(User, p.developer_id)
        if dev:
            d["developer"] = {"id": dev.id, "username": dev.username, "nickname": dev.nickname}
        items.append(d)
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.post("/admin/plugins/{plugin_id}/review")
async def review_plugin(
    plugin_id: int,
    body: PluginReviewIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")
    if plugin.status != PluginStatus.PENDING:
        raise ConflictException("仅待审核插件可操作")
    if body.action == "approve":
        plugin.status = PluginStatus.APPROVED
        plugin.reject_reason = ""
    elif body.action == "reject":
        plugin.status = PluginStatus.REJECTED
        plugin.reject_reason = body.reason or "未通过审核"
    else:
        raise ValidationException("action 必须为 approve 或 reject")
    await db.commit()
    return success_response(msg="审核完成")


@router.post("/admin/plugins/{plugin_id}/offline")
async def offline_plugin(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")
    plugin.status = PluginStatus.OFFLINE
    await db.commit()
    return success_response(msg="插件已下架")


@router.post("/admin/plugins/{plugin_id}/online")
async def online_plugin(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")
    plugin.status = PluginStatus.APPROVED
    await db.commit()
    return success_response(msg="插件已重新上架")


# ---------------------------------------------------------------------------
# Purchase / payment (LemPay)
# ---------------------------------------------------------------------------

@router.post("/orders/create")
async def create_order(
    body: PurchaseIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await db.get(ApehubWebPlugin, body.plugin_id)
    if not plugin or plugin.status != PluginStatus.APPROVED:
        raise NotFoundException("插件不存在或未上架")
    if plugin.price <= 0:
        raise ValidationException("免费插件无需购买")

    # 防止重复购买
    dup = await db.execute(select(ApehubWebOrder).where(
        ApehubWebOrder.user_id == user.id, ApehubWebOrder.plugin_id == plugin.id, ApehubWebOrder.status == OrderStatus.PAID,
    ))
    if dup.scalar_one_or_none():
        raise ConflictException("您已购买该插件")

    dev_income, fee = services.calc_split(plugin.price, plugin.service_fee_rate)
    order = ApehubWebOrder(
        order_no=services.gen_order_no(),
        user_id=user.id,
        plugin_id=plugin.id,
        amount=plugin.price,
        service_fee=fee,
        developer_income=dev_income,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    cfg = await _get_site_config(db)
    submit_url = services.build_lepay_submit_url(
        cfg.__dict__,
        {
            "type": "alipay",
            "name": f"ApeHub-{plugin.display_name}",
            "money": f"{plugin.price:.2f}",
            "out_trade_no": order.order_no,
            "notify_url": cfg.lempay_notify_url or "",
            "return_url": cfg.lempay_return_url or "",
        },
    )
    return success_response(data={
        "order": {"id": order.id, "order_no": order.order_no, "amount": order.amount, "status": order.status.value},
        "pay_url": submit_url,
    }, msg="订单已创建")


@router.post("/notify")
async def lepay_notify(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """LemPay 异步通知：验签 → 更新订单 → 分成入账。"""
    try:
        params = dict(await request.form())
    except Exception:
        params = dict(request.query_params)
    params = {k: str(v) for k, v in params.items()}
    cfg = await _get_site_config(db)
    if not services.lepay_verify_notify(params, cfg.lempay_key or ""):
        raise ValidationException("签名校验失败")

    out_trade_no = params.get("out_trade_no", "")
    trade_status = params.get("trade_status", "")
    trade_no = params.get("trade_no", "")
    order = (await db.execute(select(ApehubWebOrder).where(ApehubWebOrder.order_no == out_trade_no))).scalar_one_or_none()
    if not order:
        raise NotFoundException("订单不存在")
    if order.status == OrderStatus.PAID:
        return success_response(msg="订单已处理")

    if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED", "SUCCESS"):
        order.status = OrderStatus.PAID
        order.lepay_trade_no = trade_no
        order.paid_at = datetime.utcnow()
        plugin = await db.get(ApehubWebPlugin, order.plugin_id)
        if plugin:
            plugin.download_count += 1
            income = ApehubWebIncome(
                order_id=order.id, user_id=plugin.developer_id, plugin_id=plugin.id,
                amount=order.developer_income, rate=plugin.service_fee_rate,
            )
            db.add(income)
            # 开发者余额入账
            prof_result = await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == plugin.developer_id))
            prof = prof_result.scalar_one_or_none()
            if prof:
                prof.balance = prof.balance + order.developer_income
                prof.total_income = prof.total_income + order.developer_income
            else:
                db.add(ApehubWebProfile(user_id=plugin.developer_id, nickname="", balance=order.developer_income, total_income=order.developer_income))
        await db.commit()
        return {"code": 200, "msg": "success"}

    if trade_status in ("TRADE_CLOSED", "TRADE_CANCELLED", "CLOSED"):
        order.status = OrderStatus.CANCELLED
        await db.commit()
    return {"code": 200, "msg": "success"}


@router.get("/orders/my")
async def my_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(ApehubWebOrder).where(ApehubWebOrder.user_id == user.id).order_by(ApehubWebOrder.id.desc()).limit(100)
    )
    items = []
    for o in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, o.plugin_id)
        items.append({
            "id": o.id, "order_no": o.order_no, "plugin_id": o.plugin_id,
            "plugin_name": plugin.display_name if plugin else "",
            "amount": o.amount, "status": o.status.value, "created_at": o.created_at.isoformat() if o.created_at else None,
        })
    return success_response(data=items)


@router.get("/orders/my/paid")
async def my_paid_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """用户已购付费插件列表（含下载地址）。"""
    result = await db.execute(
        select(ApehubWebOrder).where(ApehubWebOrder.user_id == user.id, ApehubWebOrder.status == OrderStatus.PAID)
    )
    items = []
    for o in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, o.plugin_id)
        if not plugin:
            continue
        data = _plugin_summary(plugin)
        data["files"] = [
            {"id": f.id, "file_type": f.file_type, "filename": f.filename, "size": f.size}
            for f in plugin.files
        ]
        items.append(data)
    return success_response(data=items)


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """下载插件文件。付费插件需已购买，免费插件登录即可。"""
    f = await db.get(ApehubWebPluginFile, file_id)
    if not f:
        raise NotFoundException("文件不存在")
    plugin = await db.get(ApehubWebPlugin, f.plugin_id)
    if not plugin:
        raise NotFoundException("插件不存在")
    if plugin.price > 0:
        paid = await db.execute(select(ApehubWebOrder).where(
            ApehubWebOrder.user_id == user.id, ApehubWebOrder.plugin_id == plugin.id, ApehubWebOrder.status == OrderStatus.PAID,
        ))
        if not paid.scalar_one_or_none():
            raise PermissionException("请先购买该插件")
    path = os.path.join(UPLOAD_ROOT, f.stored_path)
    if not os.path.exists(path):
        raise NotFoundException("文件不存在")
    from fastapi.responses import FileResponse
    return FileResponse(path, filename=f.filename)


# ---------------------------------------------------------------------------
# User profile / withdrawal
# ---------------------------------------------------------------------------

class SiteRegisterIn(BaseModel):
    """官网注册（复用 sys_user + 返回 JWT）。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)
    email: str = Field(max_length=100)
    verification_code: str = Field(pattern=r"^\d{6}$")
    nickname: str | None = Field(default=None, max_length=50)


class SendEmailCodeIn(BaseModel):
    email: str = Field(max_length=100)


async def _consume_registration_code(
    db: AsyncSession, email: str, code: str
) -> None:
    """Validate and consume a one-time registration code."""
    record = (
        await db.execute(
            select(ApehubWebEmailVerification).where(
                ApehubWebEmailVerification.email == email.lower(),
                ApehubWebEmailVerification.purpose == "register",
            )
        )
    ).scalar_one_or_none()
    now = datetime.utcnow()
    if record is None or record.consumed_at is not None or record.expires_at <= now:
        raise ValidationException("验证码已过期，请重新获取")
    if record.attempts >= services.MAX_CODE_ATTEMPTS:
        raise ValidationException("验证码尝试次数过多，请重新获取")
    if not services.verification_code_matches(email, code, record.code_hash):
        record.attempts += 1
        await db.commit()
        raise ValidationException("验证码错误")
    record.consumed_at = now
    await db.commit()


@router.post("/site/auth/register/code")
async def send_registration_code(
    body: SendEmailCodeIn,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Issue and deliver a QQ SMTP-backed code for account registration."""
    email = body.email.strip().lower()
    if not services.is_valid_email(email):
        raise ValidationException("请输入有效的邮箱")

    now = datetime.utcnow()
    client_ip = request.client.host if request.client else "unknown"
    recent_ip_requests = (
        await db.execute(
            select(func.count()).select_from(ApehubWebEmailVerification).where(
                ApehubWebEmailVerification.request_ip == client_ip,
                ApehubWebEmailVerification.sent_at >= now - timedelta(minutes=10),
            )
        )
    ).scalar() or 0
    if recent_ip_requests >= 10:
        raise ValidationException("请求过于频繁，请 10 分钟后再试")

    record = (
        await db.execute(
            select(ApehubWebEmailVerification).where(
                ApehubWebEmailVerification.email == email,
                ApehubWebEmailVerification.purpose == "register",
            )
        )
    ).scalar_one_or_none()
    if record and (now - record.sent_at).total_seconds() < services.RESEND_INTERVAL:
        raise ValidationException("验证码已发送，请稍后再试")

    code = services.generate_code()
    if record is None:
        record = ApehubWebEmailVerification(email=email, purpose="register", code_hash="")
        db.add(record)
    record.code_hash = services.hash_verification_code(email, code)
    record.request_ip = client_ip
    record.sent_at = now
    record.expires_at = now + timedelta(seconds=services.CODE_TTL)
    record.consumed_at = None
    record.attempts = 0

    config = await _get_site_config(db)
    smtp_config = {
        "mail_user": config.mail_user,
        "mail_code": config.mail_code,
        "mail_host": config.mail_host,
        "mail_port": config.mail_port,
    }
    try:
        await asyncio.to_thread(services.send_registration_code, smtp_config, email, code)
    except Exception as exc:
        await db.rollback()
        raise ValidationException("验证码发送失败，请确认邮件服务配置后重试") from exc
    await db.commit()
    return success_response(data={"expires_in": services.CODE_TTL, "resend_in": services.RESEND_INTERVAL}, msg="验证码已发送")


@router.post("/site/auth/register")
async def site_register(
    body: SiteRegisterIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not services.is_valid_email(body.email or ""):
        raise ValidationException("请输入有效的邮箱")
    existing = await crud_user.get_by_username(db, body.username)
    if existing:
        raise ConflictException("用户名已存在")
    email_exists = (
        await db.execute(select(User.id).where(User.email == body.email.strip().lower()))
    ).scalar_one_or_none()
    if email_exists:
        raise ConflictException("邮箱已注册")
    await _consume_registration_code(db, body.email.strip().lower(), body.verification_code)
    user = await crud_user.create(db, {
        "username": body.username,
        "nickname": body.nickname or body.username,
        "email": body.email.strip().lower(),
        "password": body.password,
    })
    await _get_or_create_profile(db, user)
    token = create_access_token(user.id, extra={"username": user.username})
    return success_response(data={
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "nickname": user.nickname, "email": user.email},
    }, msg="注册成功")


@router.get("/profile")
async def my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    prof = await _get_or_create_profile(db, user)
    return success_response(data={
        "id": prof.id, "user_id": prof.user_id, "username": user.username,
        "nickname": prof.nickname, "avatar": prof.avatar, "bio": prof.bio,
        "is_developer": prof.is_developer,
        "balance": prof.balance, "frozen_balance": prof.frozen_balance,
        "total_income": prof.total_income, "total_withdrawn": prof.total_withdrawn,
        "created_at": prof.created_at.isoformat() if prof.created_at else None,
    })


@router.put("/profile")
async def update_profile(
    body: ProfileUpdateIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    prof = await _get_or_create_profile(db, user)
    for k, v in body.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(prof, k, v)
    await db.commit()
    return success_response(msg="资料已更新")


@router.post("/withdrawals")
async def create_withdrawal(
    body: WithdrawIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    prof = await _get_or_create_profile(db, user)
    if body.amount > prof.balance:
        raise ValidationException("余额不足")
    prof.balance = round(prof.balance - body.amount, 2)
    prof.frozen_balance = round(prof.frozen_balance + body.amount, 2)
    wd = ApehubWebWithdrawal(user_id=user.id, amount=body.amount, method=body.method, account=body.account)
    db.add(wd)
    await db.commit()
    await db.refresh(wd)
    return success_response(data={"id": wd.id, "status": wd.status.value}, msg="提现申请已提交")


@router.get("/withdrawals")
async def my_withdrawals(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(ApehubWebWithdrawal).where(ApehubWebWithdrawal.user_id == user.id).order_by(ApehubWebWithdrawal.id.desc()).limit(100)
    )
    return success_response(data=[
        {
            "id": w.id, "amount": w.amount, "method": w.method, "account": w.account,
            "status": w.status.value, "remark": w.remark,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in result.scalars().all()
    ])


@router.get("/incomes")
async def my_incomes(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(ApehubWebIncome).where(ApehubWebIncome.user_id == user.id).order_by(ApehubWebIncome.id.desc()).limit(100)
    )
    items = []
    for inc in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, inc.plugin_id)
        items.append({
            "id": inc.id, "order_id": inc.order_id, "plugin_id": inc.plugin_id,
            "plugin_name": plugin.display_name if plugin else "",
            "amount": inc.amount, "rate": inc.rate,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
        })
    return success_response(data=items)


# ---------------------------------------------------------------------------
# Admin: withdrawals & users & incomes
# ---------------------------------------------------------------------------

@router.get("/admin/withdrawals")
async def admin_withdrawals(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    await _require_permission(user, "apehub_web:withdrawals:review")
    stmt = select(ApehubWebWithdrawal)
    if status:
        stmt = stmt.where(ApehubWebWithdrawal.status == WithdrawalStatus(status))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebWithdrawal.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = []
    for w in result.scalars().all():
        u = await db.get(User, w.user_id)
        items.append({
            "id": w.id, "user_id": w.user_id,
            "username": u.username if u else "",
            "amount": w.amount, "method": w.method, "account": w.account,
            "status": w.status.value, "remark": w.remark,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        })
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.post("/admin/withdrawals/{wd_id}/handle")
async def handle_withdrawal(
    wd_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    action: str = Query(..., pattern="^(approve|reject|done)$"),
    remark: str = Query(""),
):
    await _require_permission(user, "apehub_web:withdrawals:review")
    wd = await db.get(ApehubWebWithdrawal, wd_id)
    if not wd:
        raise NotFoundException("提现申请不存在")
    if wd.status != WithdrawalStatus.PENDING:
        raise ValidationException("仅待处理申请可操作")
    prof = (await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == wd.user_id))).scalar_one_or_none()
    if action == "approve":
        wd.status = WithdrawalStatus.APPROVED
        wd.remark = remark or "已通过"
    elif action == "reject":
        wd.status = WithdrawalStatus.REJECTED
        if prof:
            prof.frozen_balance = round(max(prof.frozen_balance - wd.amount, 0), 2)
            prof.balance = round(prof.balance + wd.amount, 2)
        wd.remark = remark or "已驳回"
    else:  # done
        wd.status = WithdrawalStatus.DONE
        if prof:
            prof.frozen_balance = round(max(prof.frozen_balance - wd.amount, 0), 2)
            prof.total_withdrawn = round(prof.total_withdrawn + wd.amount, 2)
        wd.remark = remark or "已打款"
    await db.commit()
    return success_response(msg="处理完成")


@router.get("/admin/users")
async def admin_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
):
    await _require_permission(user, "apehub_web:users:list")
    stmt = select(User)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(User.username.like(like), User.nickname.like(like), User.email.like(like)))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = []
    for u in result.scalars().all():
        prof = (await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == u.id))).scalar_one_or_none()
        items.append({
            "id": u.id, "username": u.username, "nickname": u.nickname,
            "email": u.email, "status": u.status,
            "is_developer": bool(prof and prof.is_developer),
            "balance": prof.balance if prof else 0.0,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/admin/incomes")
async def admin_incomes(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    await _require_permission(user, "apehub_web:orders:list")
    stmt = select(ApehubWebIncome)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebIncome.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = []
    for inc in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, inc.plugin_id)
        u = await db.get(User, inc.user_id)
        items.append({
            "id": inc.id, "order_id": inc.order_id, "plugin_id": inc.plugin_id,
            "plugin_name": plugin.name if plugin else "",
            "developer": u.username if u else "",
            "amount": inc.amount, "rate": inc.rate,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
        })
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/admin/orders")
async def admin_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List marketplace orders for the management console."""
    await _require_permission(user, "apehub_web:orders:list")
    stmt = select(ApehubWebOrder)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    result = await db.execute(
        stmt.order_by(ApehubWebOrder.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = []
    for order in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, order.plugin_id)
        purchaser = await db.get(User, order.user_id)
        items.append(
            {
                "id": order.id,
                "order_no": order.order_no,
                "user_id": order.user_id,
                "username": purchaser.username if purchaser else "",
                "plugin_id": order.plugin_id,
                "plugin_name": plugin.display_name if plugin else "",
                "amount": order.amount,
                "service_fee": order.service_fee,
                "developer_income": order.developer_income,
                "status": order.status.value,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            }
        )
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})
