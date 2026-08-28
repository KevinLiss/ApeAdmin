"""ApeHub official website API routes.

Two surfaces are provided:
- Public website (免登录): site config/content, docs, plugin marketplace, register/login
- Admin management (需登录 + 超级管理员/权限): content/config/doc/plugin review/payment/user

Auth reuses ApeAdmin's sys_user + JWT. Public endpoints are deliberately
independent of `get_current_user` so the /site/* pages work without a token.
"""

import asyncio
import hashlib
import os
import secrets
import uuid
import zipfile
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, Request, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.crypto import decrypt_api_key, encrypt_api_key
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
from src.db import SessionLocal, get_db
from src.models import User
from src.plugins.builtin.apehub_web import services
from src.plugins.builtin.apehub_web.analysis import (
    MAX_PACKAGE_SIZE,
    PackageValidationError,
    generate_documentation,
    inspect_package,
)
from src.plugins.builtin.apehub_web.models import (
    AnalysisStatus,
    ApehubWebAnalysisJob,
    ApehubWebDoc,
    ApehubWebDocCategory,
    ApehubWebEmailVerification,
    ApehubWebIncome,
    ApehubWebLedgerEntry,
    ApehubWebNavigationItem,
    ApehubWebOrder,
    ApehubWebPaymentEvent,
    ApehubWebPlugin,
    ApehubWebPluginDemo,
    ApehubWebPluginFile,
    ApehubWebPluginInstallation,
    ApehubWebPluginMedia,
    ApehubWebPluginReview,
    ApehubWebPluginVersion,
    ApehubWebProfile,
    ApehubWebPurchaseEntitlement,
    ApehubWebSiteConfig,
    ApehubWebSiteContent,
    ApehubWebWithdrawal,
    ApehubWebWallet,
    DemoType,
    OrderStatus,
    PluginStatus,
    PluginVersionStatus,
    WithdrawalStatus,
)
from src.plugins.builtin.apehub_web.schemas import (
    DocCategoryIn,
    DocIn,
    NavigationItemIn,
    PluginMediaIn,
    PluginReviewIn,
    PluginSubmitIn,
    PluginVersionCreateIn,
    PluginVersionUpdateIn,
    ProfileUpdateIn,
    PurchaseIn,
    RefundIn,
    SiteConfigIn,
    SiteContentIn,
    WithdrawIn,
    VersionReviewIn,
    WalletIn,
    WithdrawalHandleIn,
)

router = APIRouter(prefix="/apehub-web", tags=["Apehub_web"])

# Keep plugin uploads beside ApeAdmin's existing plugin upload directory.
UPLOAD_ROOT = str(Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web")
MAX_SITE_IMAGE_SIZE = 5 * 1024 * 1024


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


def _image_extension(content: bytes) -> str | None:
    """Recognize only safe raster image formats for public site assets."""
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
        return ".gif"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp"
    return None


def _money(value: Decimal | int | float | None) -> str:
    return format(Decimal(str(value or 0)).quantize(Decimal("0.00000001")), "f")


def _lempay_product_name(display_name: str) -> str:
    raw = f"ApeHub-{display_name}".encode("utf-8")[:127]
    return raw.decode("utf-8", errors="ignore")


def _version_summary(version: ApehubWebPluginVersion, include_report: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": version.id,
        "plugin_id": version.plugin_id,
        "version": version.version,
        "status": version.status.value,
        "compatibility": version.compatibility,
        "changelog": version.changelog,
        "documentation": version.documentation,
        "reject_reason": version.reject_reason,
        "submitted_at": version.submitted_at.isoformat() if version.submitted_at else None,
        "reviewed_at": version.reviewed_at.isoformat() if version.reviewed_at else None,
        "published_at": version.published_at.isoformat() if version.published_at else None,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }
    if include_report:
        data["analysis_report"] = version.analysis_report
    data["files"] = [
        {
            "id": file.id,
            "file_type": file.file_type,
            "filename": file.filename,
            "size": file.size,
            "md5": file.md5,
        }
        for file in version.files
    ]
    return data


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


def _decrypt_secret(ciphertext: str | None) -> str:
    if not ciphertext:
        return ""
    try:
        return decrypt_api_key(ciphertext)
    except Exception:
        # Compatibility for a schema <= 6 row loaded before its migration runs.
        return ciphertext


def _smtp_config(cfg: ApehubWebSiteConfig) -> dict[str, Any]:
    return {
        "mail_user": cfg.mail_user,
        "mail_code": _decrypt_secret(cfg.mail_code_enc),
        "mail_host": cfg.mail_host,
        "mail_port": cfg.mail_port,
    }


def _payment_config(cfg: ApehubWebSiteConfig) -> dict[str, Any]:
    return {
        "lempay_pid": cfg.lempay_pid,
        "lempay_key": _decrypt_secret(cfg.lempay_key_enc),
        "lempay_api_url": cfg.lempay_api_url,
        "lempay_submit_url": cfg.lempay_submit_url,
        "lempay_notify_url": cfg.lempay_notify_url,
        "lempay_return_url": cfg.lempay_return_url,
        "lempay_payment_type": cfg.lempay_payment_type,
    }


async def _get_or_create_profile(db: AsyncSession, user: User) -> ApehubWebProfile:
    result = await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == user.id))
    prof = result.scalar_one_or_none()
    if prof is None:
        prof = ApehubWebProfile(user_id=user.id, nickname=user.nickname or user.username)
        db.add(prof)
        await db.commit()
        await db.refresh(prof)
    return prof


async def _owned_plugin(db: AsyncSession, plugin_id: int, user_id: int) -> ApehubWebPlugin:
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if plugin is None or plugin.developer_id != user_id:
        raise NotFoundException("插件不存在")
    return plugin


async def _owned_version(
    db: AsyncSession, plugin_id: int, version_id: int, user_id: int
) -> tuple[ApehubWebPlugin, ApehubWebPluginVersion]:
    plugin = await _owned_plugin(db, plugin_id, user_id)
    version = await db.get(ApehubWebPluginVersion, version_id)
    if version is None or version.plugin_id != plugin.id:
        raise NotFoundException("插件版本不存在")
    return plugin, version


def _editable_version(version: ApehubWebPluginVersion) -> None:
    if version.status not in {
        PluginVersionStatus.DRAFT,
        PluginVersionStatus.REJECTED,
        PluginVersionStatus.ANALYSIS_FAILED,
    }:
        raise ConflictException("当前版本状态不允许修改")


def _safe_upload_path(stored_path: str) -> Path:
    root = Path(UPLOAD_ROOT).resolve()
    path = (root / stored_path).resolve()
    if root not in path.parents:
        raise ValidationException("文件路径非法")
    return path


async def _run_analysis_job(job_id: int) -> None:
    """Run one durable AI analysis job after the upload request returns."""
    async with SessionLocal() as db:
        job = await db.get(ApehubWebAnalysisJob, job_id)
        if job is None:
            return
        version = await db.get(ApehubWebPluginVersion, job.version_id)
        if version is None:
            job.status = AnalysisStatus.FAILED
            job.error = "插件版本不存在"
            job.finished_at = datetime.utcnow()
            await db.commit()
            return
        try:
            job.status = AnalysisStatus.RUNNING
            job.stage = "static_analysis"
            job.progress = 10
            job.started_at = datetime.utcnow()
            await db.commit()

            package = (
                await db.execute(
                    select(ApehubWebPluginFile)
                    .where(
                        ApehubWebPluginFile.version_id == version.id,
                        ApehubWebPluginFile.file_type == "package",
                    )
                    .order_by(ApehubWebPluginFile.id.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            if package is None:
                raise RuntimeError("请先上传插件安装包")

            report = await asyncio.to_thread(inspect_package, _safe_upload_path(package.stored_path))
            job.stage = "ai_documentation"
            job.progress = 45
            await db.commit()

            cfg = await _get_site_config(db)
            result, usage = await generate_documentation(
                report,
                api_key=_decrypt_secret(cfg.deepseek_api_key_enc),
                base_url=cfg.deepseek_base_url,
                model=cfg.deepseek_model,
            )
            stored_report = {key: value for key, value in report.items() if key != "source_context"}
            version.analysis_report = {**stored_report, "ai": result}
            version.documentation = str(result.get("documentation_markdown") or "").strip()
            version.status = PluginVersionStatus.DRAFT
            version.reject_reason = ""
            job.status = AnalysisStatus.SUCCEEDED
            job.stage = "completed"
            job.progress = 100
            job.result = result
            job.prompt_tokens = usage["prompt_tokens"]
            job.completion_tokens = usage["completion_tokens"]
            job.finished_at = datetime.utcnow()
            await db.commit()
        except Exception as exc:
            await db.rollback()
            job = await db.get(ApehubWebAnalysisJob, job_id)
            version = await db.get(ApehubWebPluginVersion, job.version_id) if job else None
            if job:
                job.status = AnalysisStatus.FAILED
                job.stage = "failed"
                job.error = str(exc)[:2000]
                job.finished_at = datetime.utcnow()
            if version:
                version.status = PluginVersionStatus.ANALYSIS_FAILED
            await db.commit()


async def _settle_due_incomes(db: AsyncSession, user_id: int | None = None) -> int:
    """Move matured revenue from pending into a developer's available balance."""
    stmt = select(ApehubWebIncome).where(
        ApehubWebIncome.status == "pending",
        ApehubWebIncome.available_at.is_not(None),
        ApehubWebIncome.available_at <= datetime.utcnow(),
    )
    if user_id is not None:
        stmt = stmt.where(ApehubWebIncome.user_id == user_id)
    incomes = list((await db.execute(stmt)).scalars().all())
    for income in incomes:
        profile = (
            await db.execute(
                select(ApehubWebProfile).where(ApehubWebProfile.user_id == income.user_id)
            )
        ).scalar_one_or_none()
        if profile is None:
            developer = await db.get(User, income.user_id)
            profile = ApehubWebProfile(
                user_id=income.user_id,
                nickname=(developer.nickname or developer.username) if developer else "",
            )
            db.add(profile)
        profile.balance = Decimal(profile.balance or 0) + Decimal(income.amount or 0)
        profile.total_income = Decimal(profile.total_income or 0) + Decimal(income.amount or 0)
        income.status = "available"
        ledger = (
            await db.execute(
                select(ApehubWebLedgerEntry).where(
                    ApehubWebLedgerEntry.order_id == income.order_id,
                    ApehubWebLedgerEntry.entry_type == "sale_income",
                )
            )
        ).scalar_one_or_none()
        if ledger:
            ledger.status = "available"
    await db.flush()
    return len(incomes)


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
        "price": _money(p.price),
        "currency": "USDT",
        "service_fee_rate": _money(p.service_fee_rate),
        "status": p.status.value,
        "download_count": p.download_count,
        "install_count": p.install_count,
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
        data["media"] = [
            {"id": media.id, "media_type": media.media_type, "url": media.url, "alt_text": media.alt_text, "sort": media.sort}
            for media in p.media
        ]
        data["versions"] = [
            _version_summary(version)
            for version in p.versions
            if version.status in {
                PluginVersionStatus.PUBLISHED,
                PluginVersionStatus.DEPRECATED,
            }
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
        "site_icon": cfg.site_icon,
        "site_domain": cfg.site_domain,
        "site_prefix": cfg.site_prefix,
        "seo_title": cfg.seo_title,
        "seo_description": cfg.seo_description,
        "seo_keywords": cfg.seo_keywords,
        "service_fee_rate": cfg.service_fee_rate,
        "currency": cfg.currency,
        "refund_days": cfg.refund_days,
        "min_withdrawal": cfg.min_withdrawal,
        "withdrawal_fee_type": cfg.withdrawal_fee_type,
        "withdrawal_fee_value": cfg.withdrawal_fee_value,
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


@router.get("/site/public/navigation")
async def public_navigation(db: Annotated[AsyncSession, Depends(get_db)]):
    """Enabled navigation items rendered by all public site pages."""
    result = await db.execute(
        select(ApehubWebNavigationItem)
        .where(ApehubWebNavigationItem.enabled.is_(True))
        .order_by(ApehubWebNavigationItem.sort, ApehubWebNavigationItem.id)
    )
    return success_response(data=[
        {
            "id": item.id,
            "title": item.title,
            "link": item.link,
            "icon_url": item.icon_url,
            "open_mode": item.open_mode,
            "sort": item.sort,
        }
        for item in result.scalars().all()
    ])


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
        "site_icon": cfg.site_icon,
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
        "lempay_payment_type": cfg.lempay_payment_type,
        "deepseek_base_url": cfg.deepseek_base_url,
        "deepseek_model": cfg.deepseek_model,
        "service_fee_rate": cfg.service_fee_rate,
        "currency": cfg.currency,
        "settlement_days": cfg.settlement_days,
        "refund_days": cfg.refund_days,
        "min_withdrawal": cfg.min_withdrawal,
        "withdrawal_fee_type": cfg.withdrawal_fee_type,
        "withdrawal_fee_value": cfg.withdrawal_fee_value,
        "mail_configured": bool(cfg.mail_code_enc),
        "lempay_configured": bool(cfg.lempay_key_enc and cfg.lempay_pid),
        "deepseek_configured": bool(cfg.deepseek_api_key_enc),
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
    secret_fields = {
        "mail_code": "mail_code_enc",
        "lempay_key": "lempay_key_enc",
        "deepseek_api_key": "deepseek_api_key_enc",
    }
    for input_name, model_name in secret_fields.items():
        if input_name not in payload:
            continue
        value = payload.pop(input_name)
        if value:
            payload[model_name] = encrypt_api_key(value)
    # Normalize site_prefix: must start with "/" and not end with "/"
    if "site_prefix" in payload:
        prefix = payload["site_prefix"].strip() or "/site"
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        payload["site_prefix"] = prefix.rstrip("/")
    for k, v in payload.items():
        if k == "currency":
            continue
        setattr(cfg, k, v)
    await db.commit()
    await db.refresh(cfg)
    return success_response(data={"id": cfg.id}, msg="配置已保存")


@router.post("/admin/assets/upload")
async def upload_site_asset(
    user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(...)],
):
    """Upload a public site image and return its stable public URL."""
    await _require_permission(user, "apehub_web:config:edit")
    content = await file.read(MAX_SITE_IMAGE_SIZE + 1)
    if not content or len(content) > MAX_SITE_IMAGE_SIZE:
        raise ValidationException("图片不能为空且不能超过 5MB")
    extension = _image_extension(content)
    if extension is None:
        raise ValidationException("仅支持 PNG、JPEG、GIF 或 WebP 图片")
    relative_path = f"site-assets/{uuid.uuid4().hex}{extension}"
    destination = Path(UPLOAD_ROOT) / relative_path
    _ensure_dir(str(destination.parent))
    destination.write_bytes(content)
    return success_response(
        data={"url": f"/apehub-web/uploads/{relative_path}", "filename": file.filename or destination.name},
        msg="图片上传成功",
    )


@router.get("/admin/navigation")
async def list_navigation(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:list")
    result = await db.execute(
        select(ApehubWebNavigationItem).order_by(ApehubWebNavigationItem.sort, ApehubWebNavigationItem.id)
    )
    return success_response(data=[
        {
            "id": item.id,
            "title": item.title,
            "link": item.link,
            "icon_url": item.icon_url,
            "open_mode": item.open_mode,
            "enabled": item.enabled,
            "sort": item.sort,
        }
        for item in result.scalars().all()
    ])


@router.post("/admin/navigation")
async def create_navigation(
    body: NavigationItemIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:edit")
    item = ApehubWebNavigationItem(**body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return success_response(data={"id": item.id}, msg="导航项已创建")


@router.put("/admin/navigation/{item_id}")
async def update_navigation(
    item_id: int,
    body: NavigationItemIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:edit")
    item = await db.get(ApehubWebNavigationItem, item_id)
    if item is None:
        raise NotFoundException("导航项不存在")
    for key, value in body.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    return success_response(msg="导航项已更新")


@router.delete("/admin/navigation/{item_id}")
async def delete_navigation(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:config:edit")
    item = await db.get(ApehubWebNavigationItem, item_id)
    if item is None:
        raise NotFoundException("导航项不存在")
    await db.delete(item)
    await db.commit()
    return success_response(msg="导航项已删除")


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


# Developer submission and release management
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
    default_rate = cfg.service_fee_rate if cfg else Decimal("30")
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
        service_fee_rate=default_rate,
        icon=body.icon,
    )
    db.add(plugin)
    await db.flush()
    version = ApehubWebPluginVersion(
        plugin_id=plugin.id,
        version=body.version,
        status=PluginVersionStatus.DRAFT,
    )
    db.add(version)
    for demo in body.demos or []:
        db.add(ApehubWebPluginDemo(plugin_id=plugin.id, demo_type=demo.demo_type, title=demo.title, url=demo.url, qr_image=demo.qr_image))
    await db.commit()
    await db.refresh(plugin)
    return success_response(
        data={"id": plugin.id, "slug": plugin.slug, "version_id": version.id},
        msg="插件草稿已创建，请完善资料后提交审核",
    )


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
    plugin = await _owned_plugin(db, plugin_id, user.id)
    data = _plugin_summary(plugin, with_demos=True)
    data["versions"] = [_version_summary(version, include_report=True) for version in plugin.versions]
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
    plugin = await _owned_plugin(db, plugin_id, user.id)
    payload = body.model_dump(exclude_unset=True)
    if "slug" in payload:
        payload.pop("slug", None)
    for k, v in payload.items():
        if k in {"demos", "version"}:
            continue
        if k in ("name",):
            v = services.gen_slug(v)
            plugin.slug = v
        setattr(plugin, k, v)
    # Replace demos as a single transaction.
    await db.execute(sa_delete(ApehubWebPluginDemo).where(ApehubWebPluginDemo.plugin_id == plugin_id))
    for demo in body.demos or []:
        db.add(ApehubWebPluginDemo(plugin_id=plugin_id, demo_type=demo.demo_type, title=demo.title, url=demo.url, qr_image=demo.qr_image))
    await db.commit()
    return success_response(msg="插件基本信息已更新")


@router.get("/developer/plugins/{plugin_id}/versions")
async def list_my_plugin_versions(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    return success_response(data=[_version_summary(version, include_report=True) for version in plugin.versions])


@router.post("/developer/plugins/{plugin_id}/versions")
async def create_plugin_version(
    plugin_id: int,
    body: PluginVersionCreateIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    duplicate = (
        await db.execute(
            select(ApehubWebPluginVersion.id).where(
                ApehubWebPluginVersion.plugin_id == plugin.id,
                ApehubWebPluginVersion.version == body.version,
            )
        )
    ).scalar_one_or_none()
    if duplicate:
        raise ConflictException("该版本号已存在")
    version = ApehubWebPluginVersion(plugin_id=plugin.id, **body.model_dump())
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return success_response(data=_version_summary(version), msg="新版本草稿已创建")


@router.put("/developer/plugins/{plugin_id}/versions/{version_id}")
async def update_plugin_version(
    plugin_id: int,
    version_id: int,
    body: PluginVersionUpdateIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _, version = await _owned_version(db, plugin_id, version_id, user.id)
    _editable_version(version)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(version, key, value)
    await db.commit()
    return success_response(msg="版本资料已保存")


@router.post("/developer/plugins/{plugin_id}/media")
async def create_plugin_media(
    plugin_id: int,
    body: PluginMediaIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    media = ApehubWebPluginMedia(plugin_id=plugin.id, **body.model_dump())
    db.add(media)
    if body.media_type == "logo":
        plugin.icon = body.url
    await db.commit()
    await db.refresh(media)
    return success_response(data={"id": media.id, "url": media.url}, msg="图片已添加")


@router.post("/developer/plugins/{plugin_id}/media/upload")
async def upload_plugin_media(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(...)],
    media_type: str = Query(..., pattern="^(logo|carousel)$"),
    alt_text: str = Query("", max_length=255),
    sort: int = Query(0, ge=0, le=9999),
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    content = await file.read(MAX_SITE_IMAGE_SIZE + 1)
    if not content or len(content) > MAX_SITE_IMAGE_SIZE:
        raise ValidationException("图片不能为空且不能超过 5MB")
    extension = _image_extension(content)
    if extension is None:
        raise ValidationException("仅支持 PNG、JPEG、GIF 或 WebP 图片")
    stored = f"plugin-media/{plugin.id}/{uuid.uuid4().hex}{extension}"
    destination = _safe_upload_path(stored)
    _ensure_dir(str(destination.parent))
    destination.write_bytes(content)
    url = f"/apehub-web/uploads/{stored}"
    media = ApehubWebPluginMedia(
        plugin_id=plugin.id,
        media_type=media_type,
        url=url,
        alt_text=alt_text,
        sort=sort,
    )
    db.add(media)
    if media_type == "logo":
        plugin.icon = url
    await db.commit()
    await db.refresh(media)
    return success_response(data={"id": media.id, "url": url}, msg="图片上传成功")


@router.delete("/developer/plugins/{plugin_id}/media/{media_id}")
async def delete_plugin_media(
    plugin_id: int,
    media_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    media = await db.get(ApehubWebPluginMedia, media_id)
    if media is None or media.plugin_id != plugin.id:
        raise NotFoundException("图片不存在")
    if media.url.startswith("/apehub-web/uploads/"):
        relative = media.url.removeprefix("/apehub-web/uploads/")
        path = _safe_upload_path(relative)
        if path.is_file():
            path.unlink()
    if plugin.icon == media.url:
        plugin.icon = ""
    await db.delete(media)
    await db.commit()
    return success_response(msg="图片已删除")


@router.post("/developer/plugins/{plugin_id}/files")
async def upload_plugin_file(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File(...)],
    file_type: str = Query("package", pattern="^(package|doc|screenshot)$"),
    version_id: int | None = Query(None),
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    if version_id is None:
        version = (
            await db.execute(
                select(ApehubWebPluginVersion)
                .where(ApehubWebPluginVersion.plugin_id == plugin.id)
                .order_by(ApehubWebPluginVersion.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
    else:
        _, version = await _owned_version(db, plugin_id, version_id, user.id)
    if version is None:
        raise ValidationException("请先创建插件版本")
    _editable_version(version)
    if file_type == "package" and not (file.filename or "").lower().endswith(".zip"):
        raise ValidationException("插件安装包必须是 ZIP 文件")
    extension = Path(file.filename or "").suffix.lower() or ".bin"
    stored = f"plugins/{plugin.id}/{version.id}/{uuid.uuid4().hex}{extension}"
    dest = _safe_upload_path(stored)
    _ensure_dir(str(dest.parent))
    size = 0
    try:
        with dest.open("wb") as fh:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_PACKAGE_SIZE:
                    raise ValidationException("插件文件不能超过 50MB")
                fh.write(chunk)
        if file_type == "package":
            report = await asyncio.to_thread(inspect_package, dest)
            manifest_version = str(report["manifest"].get("version") or "")
            if manifest_version != version.version:
                raise ValidationException(
                    f"plugin.json 版本号 {manifest_version} 与当前版本 {version.version} 不一致"
                )
    except Exception:
        if dest.is_file():
            dest.unlink()
        raise
    md5 = hashlib.md5(dest.read_bytes()).hexdigest()
    if file_type == "package":
        old_files = (
            await db.execute(
                select(ApehubWebPluginFile).where(
                    ApehubWebPluginFile.version_id == version.id,
                    ApehubWebPluginFile.file_type == "package",
                )
            )
        ).scalars().all()
        for old_file in old_files:
            old_path = _safe_upload_path(old_file.stored_path)
            if old_path.is_file():
                old_path.unlink()
            await db.delete(old_file)
        version.analysis_report = None
        version.documentation = ""
        version.status = PluginVersionStatus.DRAFT
    row = ApehubWebPluginFile(
        plugin_id=plugin_id, version_id=version.id, file_type=file_type,
        filename=file.filename or stored, stored_path=stored, size=size, md5=md5,
    )
    db.add(row)
    await db.commit()
    return success_response(
        data={"id": row.id, "version_id": version.id, "filename": row.filename, "size": size},
        msg="文件上传成功",
    )


@router.delete("/developer/plugins/{plugin_id}/files/{file_id}")
async def delete_plugin_file(
    plugin_id: int, file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin = await _owned_plugin(db, plugin_id, user.id)
    f = await db.get(ApehubWebPluginFile, file_id)
    if not f or f.plugin_id != plugin_id:
        raise NotFoundException("文件不存在")
    if f.version:
        _editable_version(f.version)
    path = _safe_upload_path(f.stored_path)
    if path.is_file():
        path.unlink()
    await db.delete(f)
    await db.commit()
    return success_response(msg="文件已删除")


@router.post("/developer/plugins/{plugin_id}/versions/{version_id}/analyze")
async def analyze_plugin_version(
    plugin_id: int,
    version_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _, version = await _owned_version(db, plugin_id, version_id, user.id)
    _editable_version(version)
    package = (
        await db.execute(
            select(ApehubWebPluginFile.id).where(
                ApehubWebPluginFile.version_id == version.id,
                ApehubWebPluginFile.file_type == "package",
            )
        )
    ).scalar_one_or_none()
    if package is None:
        raise ValidationException("请先上传插件 ZIP 安装包")
    running = (
        await db.execute(
            select(ApehubWebAnalysisJob.id).where(
                ApehubWebAnalysisJob.version_id == version.id,
                ApehubWebAnalysisJob.status.in_([AnalysisStatus.QUEUED, AnalysisStatus.RUNNING]),
            )
        )
    ).scalar_one_or_none()
    if running:
        raise ConflictException("该版本正在分析")
    cfg = await _get_site_config(db)
    if not cfg.deepseek_api_key_enc:
        raise ValidationException("请先在官网配置中设置 DeepSeek API Key")
    job = ApehubWebAnalysisJob(
        plugin_id=plugin_id,
        version_id=version.id,
        status=AnalysisStatus.QUEUED,
        model=cfg.deepseek_model,
    )
    db.add(job)
    version.status = PluginVersionStatus.ANALYZING
    await db.commit()
    await db.refresh(job)
    background_tasks.add_task(_run_analysis_job, job.id)
    return success_response(data={"job_id": job.id, "status": job.status.value}, msg="AI 分析已开始")


@router.get("/developer/plugins/{plugin_id}/versions/{version_id}/analysis")
async def get_plugin_analysis(
    plugin_id: int,
    version_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _, version = await _owned_version(db, plugin_id, version_id, user.id)
    job = (
        await db.execute(
            select(ApehubWebAnalysisJob)
            .where(ApehubWebAnalysisJob.version_id == version.id)
            .order_by(ApehubWebAnalysisJob.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return success_response(data={
        "version_status": version.status.value,
        "documentation": version.documentation,
        "analysis_report": version.analysis_report,
        "job": None if job is None else {
            "id": job.id,
            "status": job.status.value,
            "stage": job.stage,
            "progress": job.progress,
            "model": job.model,
            "error": job.error,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        },
    })


@router.post("/developer/plugins/{plugin_id}/versions/{version_id}/submit")
async def submit_plugin_version_for_review(
    plugin_id: int,
    version_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    plugin, version = await _owned_version(db, plugin_id, version_id, user.id)
    _editable_version(version)
    package = (
        await db.execute(
            select(ApehubWebPluginFile.id).where(
                ApehubWebPluginFile.version_id == version.id,
                ApehubWebPluginFile.file_type == "package",
            )
        )
    ).scalar_one_or_none()
    carousel = (
        await db.execute(
            select(ApehubWebPluginMedia.id).where(
                ApehubWebPluginMedia.plugin_id == plugin.id,
                ApehubWebPluginMedia.media_type == "carousel",
            ).limit(1)
        )
    ).scalar_one_or_none()
    if package is None:
        raise ValidationException("请先上传插件 ZIP 安装包")
    if not plugin.icon:
        raise ValidationException("请上传插件 Logo")
    if carousel is None:
        raise ValidationException("请至少上传一张轮播图")
    if not version.documentation.strip():
        raise ValidationException("请先生成或填写完整技术文档")
    version.status = PluginVersionStatus.SUBMITTED
    version.submitted_at = datetime.utcnow()
    version.reject_reason = ""
    if plugin.status in {PluginStatus.REJECTED, PluginStatus.OFFLINE}:
        plugin.status = PluginStatus.PENDING
        plugin.reject_reason = ""
    await db.commit()
    return success_response(msg="版本已提交审核")


# ---------------------------------------------------------------------------
# Admin review / marketplace management
# ---------------------------------------------------------------------------

async def _plugin_management_stats(db: AsyncSession, plugin_ids: list[int]) -> dict[int, dict[str, Any]]:
    """Fetch purchase and installation metrics in bulk for management views."""
    if not plugin_ids:
        return {}
    paid_orders = await db.execute(
        select(
            ApehubWebOrder.plugin_id,
            func.count(ApehubWebOrder.id),
            func.count(func.distinct(ApehubWebOrder.user_id)),
            func.coalesce(func.sum(ApehubWebOrder.amount), 0),
        )
        .where(
            ApehubWebOrder.plugin_id.in_(plugin_ids),
            ApehubWebOrder.status == OrderStatus.PAID,
        )
        .group_by(ApehubWebOrder.plugin_id)
    )
    installations = await db.execute(
        select(
            ApehubWebPluginInstallation.plugin_id,
            func.count(ApehubWebPluginInstallation.id),
            func.coalesce(func.sum(ApehubWebPluginInstallation.download_count), 0),
        )
        .where(ApehubWebPluginInstallation.plugin_id.in_(plugin_ids))
        .group_by(ApehubWebPluginInstallation.plugin_id)
    )
    stats = {
        plugin_id: {"paid_order_count": 0, "buyer_count": 0, "paid_amount": 0.0, "install_users": 0, "download_total": 0}
        for plugin_id in plugin_ids
    }
    for plugin_id, order_count, buyer_count, paid_amount in paid_orders.all():
        stats[plugin_id].update(
            paid_order_count=order_count,
            buyer_count=buyer_count,
            paid_amount=float(paid_amount or 0),
        )
    for plugin_id, install_users, download_total in installations.all():
        stats[plugin_id].update(install_users=install_users, download_total=download_total)
    return stats

@router.get("/admin/plugins")
async def admin_list_plugins(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    status: str | None = Query(None),
    keyword: str | None = Query(None, max_length=100),
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
    if keyword:
        like = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                ApehubWebPlugin.name.like(like),
                ApehubWebPlugin.display_name.like(like),
                ApehubWebPlugin.description.like(like),
            )
        )
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(ApehubWebPlugin.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    plugins = list(result.scalars().all())
    developers = {
        developer.id: developer
        for developer in (
            await db.execute(select(User).where(User.id.in_([p.developer_id for p in plugins])))
        ).scalars().all()
    } if plugins else {}
    stats = await _plugin_management_stats(db, [plugin.id for plugin in plugins])
    items = []
    for p in plugins:
        d = _plugin_summary(p, with_demos=True)
        d["review_queue_count"] = sum(
            version.status in {PluginVersionStatus.SUBMITTED, PluginVersionStatus.REVIEWING}
            for version in p.versions
        )
        d["metrics"] = stats[p.id]
        dev = developers.get(p.developer_id)
        d["developer"] = None
        if dev:
            d["developer"] = {"id": dev.id, "username": dev.username, "nickname": dev.nickname}
        items.append(d)
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/admin/plugins/{plugin_id}")
async def admin_plugin_detail(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Complete review and commercial data for one plugin."""
    await _require_permission(user, "apehub_web:plugins:review")
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if plugin is None:
        raise NotFoundException("插件不存在")
    data = _plugin_summary(plugin, with_demos=True)
    data["versions"] = [_version_summary(version, include_report=True) for version in plugin.versions]
    developer = await db.get(User, plugin.developer_id)
    data["developer"] = (
        {"id": developer.id, "username": developer.username, "nickname": developer.nickname, "email": developer.email}
        if developer else None
    )
    data["metrics"] = (await _plugin_management_stats(db, [plugin.id]))[plugin.id]
    data["files"] = [
        {
            "id": file.id,
            "file_type": file.file_type,
            "filename": file.filename,
            "size": file.size,
            "md5": file.md5,
            "created_at": file.created_at.isoformat() if file.created_at else None,
        }
        for file in plugin.files
    ]
    reviews = (
        await db.execute(
            select(ApehubWebPluginReview)
            .where(ApehubWebPluginReview.plugin_id == plugin.id)
            .order_by(ApehubWebPluginReview.id.desc())
        )
    ).scalars().all()
    data["reviews"] = [
        {
            "id": review.id,
            "version_id": review.version_id,
            "reviewer_id": review.reviewer_id,
            "action": review.action,
            "comment": review.comment,
            "service_fee_rate": _money(review.service_fee_rate),
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }
        for review in reviews
    ]
    return success_response(data=data)


async def _admin_plugin_version(
    db: AsyncSession, plugin_id: int, version_id: int
) -> tuple[ApehubWebPlugin, ApehubWebPluginVersion]:
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    version = await db.get(ApehubWebPluginVersion, version_id)
    if plugin is None or version is None or version.plugin_id != plugin.id:
        raise NotFoundException("插件版本不存在")
    return plugin, version


@router.get("/admin/plugins/{plugin_id}/versions/{version_id}/source-tree")
async def admin_version_source_tree(
    plugin_id: int,
    version_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    _, version = await _admin_plugin_version(db, plugin_id, version_id)
    report = version.analysis_report or {}
    tree = report.get("file_tree")
    if tree is None:
        package = (
            await db.execute(
                select(ApehubWebPluginFile)
                .where(
                    ApehubWebPluginFile.version_id == version.id,
                    ApehubWebPluginFile.file_type == "package",
                )
                .order_by(ApehubWebPluginFile.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if package is None:
            raise NotFoundException("插件安装包不存在")
        inspected = await asyncio.to_thread(inspect_package, _safe_upload_path(package.stored_path))
        tree = inspected["file_tree"]
    return success_response(data={"files": tree, "risk_level": report.get("risk_level"), "warnings": report.get("warnings", [])})


@router.get("/admin/plugins/{plugin_id}/versions/{version_id}/source")
async def admin_version_source_file(
    plugin_id: int,
    version_id: int,
    path: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    _, version = await _admin_plugin_version(db, plugin_id, version_id)
    normalized = path.replace("\\", "/").lstrip("/")
    if not normalized or ".." in normalized.split("/"):
        raise ValidationException("源码路径非法")
    if Path(normalized).suffix.lower() not in {
        ".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".json", ".md", ".toml",
        ".yaml", ".yml", ".ini", ".cfg", ".sql", ".css", ".scss", ".html", ".txt",
    }:
        raise ValidationException("该文件不支持在线预览")
    package = (
        await db.execute(
            select(ApehubWebPluginFile)
            .where(
                ApehubWebPluginFile.version_id == version.id,
                ApehubWebPluginFile.file_type == "package",
            )
            .order_by(ApehubWebPluginFile.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if package is None:
        raise NotFoundException("插件安装包不存在")
    try:
        with zipfile.ZipFile(_safe_upload_path(package.stored_path)) as archive:
            info = archive.getinfo(normalized)
            if info.file_size > 1024 * 1024:
                raise ValidationException("单个预览文件不能超过 1MB")
            content = archive.read(info).decode("utf-8")
    except KeyError as exc:
        raise NotFoundException("源码文件不存在") from exc
    except UnicodeDecodeError as exc:
        raise ValidationException("该文件不是 UTF-8 文本") from exc
    return success_response(data={"path": normalized, "content": content})


@router.post("/admin/plugins/{plugin_id}/versions/{version_id}/review")
async def review_plugin_version(
    plugin_id: int,
    version_id: int,
    body: VersionReviewIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    plugin, version = await _admin_plugin_version(db, plugin_id, version_id)
    if version.status not in {PluginVersionStatus.SUBMITTED, PluginVersionStatus.REVIEWING}:
        raise ConflictException("仅待审核版本可操作")
    if body.action == "approve":
        has_published = any(item.status == PluginVersionStatus.PUBLISHED for item in plugin.versions)
        if not has_published and body.service_fee_rate is None:
            raise ValidationException("首次审核通过时必须设置平台服务费百分比")
        if body.service_fee_rate is not None:
            plugin.service_fee_rate = body.service_fee_rate
        if not version.documentation.strip():
            raise ValidationException("版本技术文档不完整")
        version.status = PluginVersionStatus.APPROVED
        version.reject_reason = ""
        version.reviewed_at = datetime.utcnow()
        action = "approve"
    else:
        version.status = PluginVersionStatus.REJECTED
        version.reject_reason = body.reason or "未通过审核"
        version.reviewed_at = datetime.utcnow()
        if not any(item.status == PluginVersionStatus.PUBLISHED for item in plugin.versions):
            plugin.status = PluginStatus.REJECTED
            plugin.reject_reason = version.reject_reason
        action = "reject"
    db.add(ApehubWebPluginReview(
        plugin_id=plugin.id,
        version_id=version.id,
        reviewer_id=user.id,
        action=action,
        comment=body.reason,
        service_fee_rate=body.service_fee_rate,
    ))
    await db.commit()
    return success_response(msg="版本审核已完成")


@router.post("/admin/plugins/{plugin_id}/versions/{version_id}/publish")
async def publish_plugin_version(
    plugin_id: int,
    version_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:plugins:review")
    plugin, version = await _admin_plugin_version(db, plugin_id, version_id)
    if version.status != PluginVersionStatus.APPROVED:
        raise ConflictException("仅已审核通过的版本可发布")
    now = datetime.utcnow()
    for other in plugin.versions:
        if other.id != version.id and other.status == PluginVersionStatus.PUBLISHED:
            other.status = PluginVersionStatus.DEPRECATED
    version.status = PluginVersionStatus.PUBLISHED
    version.published_at = now
    plugin.version = version.version
    plugin.status = PluginStatus.APPROVED
    plugin.reject_reason = ""
    db.add(ApehubWebPluginReview(
        plugin_id=plugin.id,
        version_id=version.id,
        reviewer_id=user.id,
        action="publish",
        comment="发布至插件市场",
        service_fee_rate=plugin.service_fee_rate,
    ))
    await db.commit()
    return success_response(msg=f"版本 {version.version} 已上架")


@router.get("/admin/plugins/{plugin_id}/files/{file_id}/download")
async def admin_download_plugin_file(
    plugin_id: int,
    file_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Allow a reviewer to inspect an uploaded package without purchaser checks."""
    await _require_permission(user, "apehub_web:plugins:review")
    file = await db.get(ApehubWebPluginFile, file_id)
    if file is None or file.plugin_id != plugin_id:
        raise NotFoundException("插件文件不存在")
    root = Path(UPLOAD_ROOT).resolve()
    path = (root / file.stored_path).resolve()
    if root not in path.parents or not path.is_file():
        raise NotFoundException("插件文件不存在")
    from fastapi.responses import FileResponse

    return FileResponse(path, filename=file.filename)


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
    version = (
        await db.execute(
            select(ApehubWebPluginVersion)
            .where(
                ApehubWebPluginVersion.plugin_id == plugin.id,
                ApehubWebPluginVersion.status == PluginVersionStatus.SUBMITTED,
            )
            .order_by(ApehubWebPluginVersion.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if version is None:
        raise ConflictException("没有待审核的插件版本")
    if body.action == "approve":
        has_published = any(item.status == PluginVersionStatus.PUBLISHED for item in plugin.versions)
        if not has_published and body.service_fee_rate is None:
            raise ValidationException("首次审核通过时必须设置平台服务费百分比")
        if body.service_fee_rate is not None:
            plugin.service_fee_rate = body.service_fee_rate
        version.status = PluginVersionStatus.APPROVED
        version.reviewed_at = datetime.utcnow()
        version.reject_reason = ""
    elif body.action == "reject":
        version.status = PluginVersionStatus.REJECTED
        version.reviewed_at = datetime.utcnow()
        version.reject_reason = body.reason or "未通过审核"
        plugin.status = PluginStatus.REJECTED
        plugin.reject_reason = version.reject_reason
    else:
        raise ValidationException("action 必须为 approve 或 reject")
    db.add(ApehubWebPluginReview(
        plugin_id=plugin.id,
        version_id=version.id,
        reviewer_id=user.id,
        action=body.action,
        comment=body.reason,
        service_fee_rate=body.service_fee_rate,
    ))
    await db.commit()
    return success_response(data={"version_id": version.id}, msg="审核完成，通过后还需单独发布上架")


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
    if plugin.status != PluginStatus.OFFLINE:
        raise ConflictException("当前状态不能直接上架")
    if not any(
        version.status in {PluginVersionStatus.PUBLISHED, PluginVersionStatus.DEPRECATED}
        for version in plugin.versions
    ):
        raise ValidationException("没有已审核发布的版本，不能直接上架")
    plugin.status = PluginStatus.APPROVED
    await db.commit()
    return success_response(msg="插件已重新上架")


@router.delete("/admin/plugins/{plugin_id}")
async def delete_admin_plugin(
    plugin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Delete only unpurchased plugin submissions and their local files."""
    await _require_permission(user, "apehub_web:plugins:review")
    plugin = await db.get(ApehubWebPlugin, plugin_id)
    if plugin is None:
        raise NotFoundException("插件不存在")
    paid_count = (
        await db.execute(
            select(func.count()).select_from(ApehubWebOrder).where(
                ApehubWebOrder.plugin_id == plugin.id,
                ApehubWebOrder.status == OrderStatus.PAID,
            )
        )
    ).scalar() or 0
    if paid_count:
        raise ConflictException("已有购买记录的插件不能删除，请使用下架")
    root = Path(UPLOAD_ROOT).resolve()
    for file in plugin.files:
        path = (root / file.stored_path).resolve()
        if root in path.parents and path.is_file():
            path.unlink()
    version_ids = [version.id for version in plugin.versions]
    if version_ids:
        await db.execute(
            sa_delete(ApehubWebAnalysisJob).where(ApehubWebAnalysisJob.version_id.in_(version_ids))
        )
    await db.execute(sa_delete(ApehubWebPluginReview).where(ApehubWebPluginReview.plugin_id == plugin.id))
    await db.execute(sa_delete(ApehubWebPluginMedia).where(ApehubWebPluginMedia.plugin_id == plugin.id))
    await db.execute(
        sa_delete(ApehubWebPluginInstallation).where(ApehubWebPluginInstallation.plugin_id == plugin.id)
    )
    await db.delete(plugin)
    await db.commit()
    return success_response(msg="插件提交及未售文件已删除")


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
    payment_amount = Decimal(plugin.price).quantize(Decimal("0.01"))
    if payment_amount != Decimal(plugin.price):
        raise ValidationException("LemPay 支付金额最多支持两位小数，请联系管理员调整定价")

    cfg = await _get_site_config(db)
    payment_cfg = _payment_config(cfg)
    if not payment_cfg["lempay_pid"] or not payment_cfg["lempay_key"] or not payment_cfg["lempay_submit_url"]:
        raise ValidationException("支付通道尚未配置完成")

    entitlement = await db.execute(select(ApehubWebPurchaseEntitlement).where(
        ApehubWebPurchaseEntitlement.user_id == user.id,
        ApehubWebPurchaseEntitlement.plugin_id == plugin.id,
        ApehubWebPurchaseEntitlement.active.is_(True),
    ))
    if entitlement.scalar_one_or_none():
        raise ConflictException("您已购买该插件")

    dev_income, fee = services.calc_split(plugin.price, plugin.service_fee_rate)
    order = ApehubWebOrder(
        order_no=services.gen_order_no(),
        user_id=user.id,
        plugin_id=plugin.id,
        amount=plugin.price,
        service_fee=fee,
        developer_income=dev_income,
        currency="USDT",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    submit_url = services.build_lepay_submit_url(
        payment_cfg,
        {
            "type": "usdt",
            "name": _lempay_product_name(plugin.display_name),
            "money": format(payment_amount, ".2f"),
            "out_trade_no": order.order_no,
            "notify_url": cfg.lempay_notify_url or "",
            "return_url": cfg.lempay_return_url or "",
        },
    )
    return success_response(data={
        "order": {
            "id": order.id,
            "order_no": order.order_no,
            "amount": _money(order.amount),
            "currency": "USDT",
            "status": order.status.value,
        },
        "pay_url": submit_url,
    }, msg="订单已创建")


@router.get("/notify", response_class=PlainTextResponse)
@router.post("/notify", response_class=PlainTextResponse)
async def lepay_notify(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """LemPay 异步通知：验签 → 更新订单 → 分成入账。"""
    params = dict(request.query_params)
    if request.method == "POST":
        try:
            params.update(dict(await request.form()))
        except Exception:
            pass
    params = {k: str(v) for k, v in params.items()}
    cfg = await _get_site_config(db)
    try:
        signature_valid = services.lempay_verify_notify(params, _decrypt_secret(cfg.lempay_key_enc))
    except Exception:
        signature_valid = False
    if not signature_valid:
        return PlainTextResponse("fail", status_code=400)

    out_trade_no = params.get("out_trade_no", "")
    trade_status = params.get("trade_status", "")
    trade_no = params.get("trade_no", "")
    order = (await db.execute(select(ApehubWebOrder).where(ApehubWebOrder.order_no == out_trade_no))).scalar_one_or_none()
    if not order:
        return PlainTextResponse("fail", status_code=404)
    if order.status == OrderStatus.PAID:
        return PlainTextResponse("success")
    if trade_status != "TRADE_SUCCESS":
        return PlainTextResponse("fail", status_code=400)
    if str(params.get("pid") or "") != str(cfg.lempay_pid):
        return PlainTextResponse("fail", status_code=400)
    if params.get("type") != "usdt":
        return PlainTextResponse("fail", status_code=400)
    try:
        notified_amount = Decimal(params.get("money") or "-1").quantize(Decimal("0.01"))
    except Exception:
        return PlainTextResponse("fail", status_code=400)
    if notified_amount != Decimal(order.amount).quantize(Decimal("0.01")):
        return PlainTextResponse("fail", status_code=400)
    plugin = await db.get(ApehubWebPlugin, order.plugin_id)
    if plugin is None or params.get("name") != _lempay_product_name(plugin.display_name):
        return PlainTextResponse("fail", status_code=400)

    event_id = trade_no or hashlib.sha256(str(sorted(params.items())).encode("utf-8")).hexdigest()
    existing_event = (
        await db.execute(
            select(ApehubWebPaymentEvent).where(ApehubWebPaymentEvent.provider_event_id == event_id)
        )
    ).scalar_one_or_none()
    if existing_event and existing_event.processed:
        return PlainTextResponse("success")
    event = existing_event or ApehubWebPaymentEvent(
        order_id=order.id,
        provider_event_id=event_id,
        event_type="payment",
        signature_valid=True,
        payload=params,
    )
    if existing_event is None:
        db.add(event)

    now = datetime.utcnow()
    hold_days = max(cfg.settlement_days, cfg.refund_days)
    available_at = now + timedelta(days=hold_days)
    order.status = OrderStatus.PAID
    order.lepay_trade_no = trade_no
    order.paid_at = now
    entitlement = (
        await db.execute(
            select(ApehubWebPurchaseEntitlement).where(
                ApehubWebPurchaseEntitlement.user_id == order.user_id,
                ApehubWebPurchaseEntitlement.plugin_id == order.plugin_id,
            )
        )
    ).scalar_one_or_none()
    if entitlement is None:
        db.add(ApehubWebPurchaseEntitlement(
            user_id=order.user_id,
            plugin_id=order.plugin_id,
            order_id=order.id,
            active=True,
        ))
    else:
        entitlement.active = True
        entitlement.order_id = order.id
        entitlement.revoked_at = None
    income = (
        await db.execute(select(ApehubWebIncome).where(ApehubWebIncome.order_id == order.id))
    ).scalar_one_or_none()
    if income is None:
        db.add(ApehubWebIncome(
            order_id=order.id,
            user_id=plugin.developer_id,
            plugin_id=plugin.id,
            amount=order.developer_income,
            rate=plugin.service_fee_rate,
            available_at=available_at,
            status="pending",
        ))
    ledger = (
        await db.execute(
            select(ApehubWebLedgerEntry).where(
                ApehubWebLedgerEntry.order_id == order.id,
                ApehubWebLedgerEntry.entry_type == "sale_income",
            )
        )
    ).scalar_one_or_none()
    if ledger is None:
        db.add(ApehubWebLedgerEntry(
            user_id=plugin.developer_id,
            order_id=order.id,
            entry_type="sale_income",
            amount=order.developer_income,
            status="pending",
            available_at=available_at,
            note=f"插件销售：{plugin.display_name}",
        ))
    event.processed = True
    event.processed_at = now
    await db.commit()
    return PlainTextResponse("success")


@router.post("/admin/orders/{order_id}/refund")
async def refund_order(
    order_id: int,
    body: RefundIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:orders:list")
    order = await db.get(ApehubWebOrder, order_id)
    if order is None or order.status != OrderStatus.PAID or order.paid_at is None:
        raise ConflictException("仅已支付订单可退款")
    cfg = await _get_site_config(db)
    if datetime.utcnow() > order.paid_at + timedelta(days=cfg.refund_days):
        raise ConflictException("该订单已超过退款期限")
    try:
        await services.request_lepay_refund(
            _payment_config(cfg),
            trade_no=order.lepay_trade_no,
            out_trade_no=order.order_no,
            money=Decimal(order.amount),
        )
    except Exception as exc:
        raise ValidationException(f"退款提交失败：{str(exc)[:200]}") from exc
    now = datetime.utcnow()
    order.status = OrderStatus.REFUNDED
    order.refunded_at = now
    order.refund_reason = body.reason
    entitlement = (
        await db.execute(
            select(ApehubWebPurchaseEntitlement).where(
                ApehubWebPurchaseEntitlement.order_id == order.id
            )
        )
    ).scalar_one_or_none()
    if entitlement:
        entitlement.active = False
        entitlement.revoked_at = now
    income = (
        await db.execute(select(ApehubWebIncome).where(ApehubWebIncome.order_id == order.id))
    ).scalar_one_or_none()
    if income:
        if income.status == "available":
            profile = (
                await db.execute(
                    select(ApehubWebProfile).where(ApehubWebProfile.user_id == income.user_id)
                )
            ).scalar_one_or_none()
            if profile:
                profile.balance = Decimal(profile.balance or 0) - Decimal(income.amount or 0)
                profile.total_income = Decimal(profile.total_income or 0) - Decimal(income.amount or 0)
        income.status = "refunded"
    ledger = (
        await db.execute(
            select(ApehubWebLedgerEntry).where(
                ApehubWebLedgerEntry.order_id == order.id,
                ApehubWebLedgerEntry.entry_type == "sale_income",
            )
        )
    ).scalar_one_or_none()
    if ledger:
        ledger.status = "cancelled"
    db.add(ApehubWebPaymentEvent(
        order_id=order.id,
        provider_event_id=f"refund:{order.lepay_trade_no or order.order_no}",
        event_type="refund",
        signature_valid=True,
        payload={"reason": body.reason, "reviewer_id": user.id},
        processed=True,
        processed_at=now,
    ))
    await db.commit()
    return success_response(msg="订单已退款并撤销下载权限")


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
    result = await db.execute(select(ApehubWebPurchaseEntitlement).where(
        ApehubWebPurchaseEntitlement.user_id == user.id,
        ApehubWebPurchaseEntitlement.active.is_(True),
    ))
    items = []
    for entitlement in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, entitlement.plugin_id)
        if not plugin:
            continue
        data = _plugin_summary(plugin)
        data["files"] = [
            {
                "id": file.id,
                "version_id": file.version_id,
                "version": file.version.version if file.version else plugin.version,
                "file_type": file.file_type,
                "filename": file.filename,
                "size": file.size,
            }
            for file in plugin.files
            if file.version is None or file.version.status in {
                PluginVersionStatus.PUBLISHED,
                PluginVersionStatus.DEPRECATED,
            }
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
    if f.version and f.version.status not in {
        PluginVersionStatus.PUBLISHED,
        PluginVersionStatus.DEPRECATED,
    } and plugin.developer_id != user.id:
        raise PermissionException("该版本尚未发布")
    if plugin.price > 0 and plugin.developer_id != user.id:
        entitlement = await db.execute(select(ApehubWebPurchaseEntitlement).where(
            ApehubWebPurchaseEntitlement.user_id == user.id,
            ApehubWebPurchaseEntitlement.plugin_id == plugin.id,
            ApehubWebPurchaseEntitlement.active.is_(True),
        ))
        if not entitlement.scalar_one_or_none():
            raise PermissionException("请先购买该插件")
    root = Path(UPLOAD_ROOT).resolve()
    path = (root / f.stored_path).resolve()
    if root not in path.parents or not path.is_file():
        raise NotFoundException("文件不存在")
    installation = (
        await db.execute(
            select(ApehubWebPluginInstallation).where(
                ApehubWebPluginInstallation.plugin_id == plugin.id,
                ApehubWebPluginInstallation.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    if installation is None:
        db.add(ApehubWebPluginInstallation(plugin_id=plugin.id, user_id=user.id))
        plugin.install_count += 1
    else:
        installation.download_count += 1
        installation.last_downloaded_at = datetime.utcnow()
    plugin.download_count += 1
    await db.commit()
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
    if record is None:
        raise ValidationException("该邮箱没有有效验证码，请使用发送验证码的同一邮箱")
    if record.consumed_at is not None:
        raise ValidationException("验证码已使用，请重新获取")
    if record.expires_at <= now:
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
        remaining = max(1, int(services.RESEND_INTERVAL - (now - record.sent_at).total_seconds()))
        raise ValidationException(f"验证码已发送，请 {remaining} 秒后再试")

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
    smtp_config = _smtp_config(config)
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
    await _settle_due_incomes(db, user.id)
    await db.commit()
    prof = await _get_or_create_profile(db, user)
    return success_response(data={
        "id": prof.id, "user_id": prof.user_id, "username": user.username,
        "nickname": prof.nickname, "avatar": prof.avatar, "bio": prof.bio,
        "is_developer": prof.is_developer,
        "balance": _money(prof.balance), "frozen_balance": _money(prof.frozen_balance),
        "total_income": _money(prof.total_income), "total_withdrawn": _money(prof.total_withdrawn),
        "currency": "USDT",
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


@router.get("/wallet")
async def get_wallet(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    wallet = (
        await db.execute(select(ApehubWebWallet).where(ApehubWebWallet.user_id == user.id))
    ).scalar_one_or_none()
    return success_response(data=None if wallet is None else {
        "id": wallet.id,
        "network": wallet.network,
        "address": wallet.address,
        "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
    })


@router.put("/wallet")
async def update_wallet(
    body: WalletIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    wallet = (
        await db.execute(select(ApehubWebWallet).where(ApehubWebWallet.user_id == user.id))
    ).scalar_one_or_none()
    if wallet is None:
        wallet = ApehubWebWallet(user_id=user.id, network="TRC20", address=body.address)
        db.add(wallet)
    else:
        wallet.address = body.address
        wallet.network = "TRC20"
    await db.commit()
    return success_response(data={"network": "TRC20", "address": body.address}, msg="收款钱包已保存")


@router.post("/withdrawals")
async def create_withdrawal(
    body: WithdrawIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _settle_due_incomes(db, user.id)
    prof = await _get_or_create_profile(db, user)
    cfg = await _get_site_config(db)
    amount = Decimal(body.amount)
    if amount < Decimal(cfg.min_withdrawal):
        raise ValidationException(f"最低提现金额为 {_money(cfg.min_withdrawal)} USDT")
    if body.amount > prof.balance:
        raise ValidationException("余额不足")
    fee = services.calc_withdrawal_fee(amount, cfg.withdrawal_fee_type, Decimal(cfg.withdrawal_fee_value))
    net_amount = amount - fee
    if net_amount <= 0:
        raise ValidationException("扣除提现手续费后的到账金额必须大于 0")
    wallet = (
        await db.execute(select(ApehubWebWallet).where(ApehubWebWallet.user_id == user.id))
    ).scalar_one_or_none()
    if wallet is None:
        wallet = ApehubWebWallet(user_id=user.id, network="TRC20", address=body.account)
        db.add(wallet)
    else:
        wallet.address = body.account
    prof.balance = Decimal(prof.balance) - amount
    prof.frozen_balance = Decimal(prof.frozen_balance) + amount
    wd = ApehubWebWithdrawal(
        user_id=user.id,
        amount=amount,
        fee=fee,
        net_amount=net_amount,
        method="trc20",
        network="TRC20",
        account=body.account,
    )
    db.add(wd)
    await db.flush()
    db.add(ApehubWebLedgerEntry(
        user_id=user.id,
        withdrawal_id=wd.id,
        entry_type="withdrawal_hold",
        amount=-amount,
        status="frozen",
        note=f"提现冻结，手续费 {_money(fee)} USDT",
    ))
    await db.commit()
    await db.refresh(wd)
    return success_response(data={
        "id": wd.id,
        "amount": _money(wd.amount),
        "fee": _money(wd.fee),
        "net_amount": _money(wd.net_amount),
        "currency": "USDT",
        "network": "TRC20",
        "status": wd.status.value,
    }, msg="提现申请已提交")


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
            "id": w.id, "amount": _money(w.amount), "fee": _money(w.fee),
            "net_amount": _money(w.net_amount), "currency": "USDT",
            "method": w.method, "network": w.network, "account": w.account,
            "status": w.status.value, "remark": w.remark, "tx_hash": w.tx_hash,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in result.scalars().all()
    ])


@router.get("/incomes")
async def my_incomes(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _settle_due_incomes(db, user.id)
    await db.commit()
    result = await db.execute(
        select(ApehubWebIncome).where(ApehubWebIncome.user_id == user.id).order_by(ApehubWebIncome.id.desc()).limit(100)
    )
    items = []
    for inc in result.scalars().all():
        plugin = await db.get(ApehubWebPlugin, inc.plugin_id)
        items.append({
            "id": inc.id, "order_id": inc.order_id, "plugin_id": inc.plugin_id,
            "plugin_name": plugin.display_name if plugin else "",
            "amount": _money(inc.amount), "rate": _money(inc.rate), "currency": "USDT",
            "status": inc.status,
            "available_at": inc.available_at.isoformat() if inc.available_at else None,
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
            "amount": _money(w.amount), "fee": _money(w.fee), "net_amount": _money(w.net_amount),
            "currency": "USDT", "method": w.method, "network": w.network, "account": w.account,
            "status": w.status.value, "remark": w.remark, "tx_hash": w.tx_hash,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        })
    return success_response(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.post("/admin/withdrawals/{wd_id}/handle")
async def handle_withdrawal(
    wd_id: int,
    body: WithdrawalHandleIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    await _require_permission(user, "apehub_web:withdrawals:review")
    wd = await db.get(ApehubWebWithdrawal, wd_id)
    if not wd:
        raise NotFoundException("提现申请不存在")
    prof = (await db.execute(select(ApehubWebProfile).where(ApehubWebProfile.user_id == wd.user_id))).scalar_one_or_none()
    ledger = (
        await db.execute(
            select(ApehubWebLedgerEntry).where(
                ApehubWebLedgerEntry.withdrawal_id == wd.id,
                ApehubWebLedgerEntry.entry_type == "withdrawal_hold",
            )
        )
    ).scalar_one_or_none()
    now = datetime.utcnow()
    if body.action == "approve":
        if wd.status != WithdrawalStatus.PENDING:
            raise ConflictException("仅待审核申请可通过")
        wd.status = WithdrawalStatus.APPROVED
        wd.remark = body.remark or "已通过，等待人工打款"
        wd.reviewer_id = user.id
        wd.reviewed_at = now
        if ledger:
            ledger.status = "approved"
    elif body.action == "reject":
        if wd.status != WithdrawalStatus.PENDING:
            raise ConflictException("仅待审核申请可驳回")
        wd.status = WithdrawalStatus.REJECTED
        if prof:
            prof.frozen_balance = max(Decimal(prof.frozen_balance) - Decimal(wd.amount), Decimal("0"))
            prof.balance = Decimal(prof.balance) + Decimal(wd.amount)
        wd.remark = body.remark or "已驳回"
        wd.reviewer_id = user.id
        wd.reviewed_at = now
        if ledger:
            ledger.status = "cancelled"
    else:  # done
        if wd.status != WithdrawalStatus.APPROVED:
            raise ConflictException("仅已审核通过的申请可确认打款")
        if not body.tx_hash.strip():
            raise ValidationException("确认打款时必须填写 TRC20 交易哈希")
        wd.status = WithdrawalStatus.DONE
        if prof:
            prof.frozen_balance = max(Decimal(prof.frozen_balance) - Decimal(wd.amount), Decimal("0"))
            prof.total_withdrawn = Decimal(prof.total_withdrawn) + Decimal(wd.net_amount)
        wd.tx_hash = body.tx_hash.strip()
        wd.paid_at = now
        wd.remark = body.remark or "已人工打款"
        if ledger:
            ledger.status = "completed"
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
