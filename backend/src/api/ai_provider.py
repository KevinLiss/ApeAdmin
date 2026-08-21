"""AI provider management routes (model key CRUD + connectivity test)."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crypto import decrypt_api_key, encrypt_api_key, mask_api_key
from src.core.deps import require_permission
from src.core.exceptions import ConflictException, NotFoundException, success_response
from src.crud.ai import crud_ai_provider
from src.db import get_db
from src.models import User
from src.models.ai import AiProvider
from src.schemas.ai import ProviderCreate, ProviderUpdate

router = APIRouter(prefix="/ai/providers", tags=["AI 模型管理"])


def _provider_to_dict(p: AiProvider) -> dict:
    """Convert provider ORM to dict with masked API key."""
    try:
        models_list = json.loads(p.models) if p.models else []
    except (json.JSONDecodeError, TypeError):
        models_list = []
    try:
        masked = mask_api_key(decrypt_api_key(p.api_key_enc))
    except Exception:
        masked = "****"
    return {
        "id": p.id,
        "name": p.name,
        "provider_type": p.provider_type,
        "base_url": p.base_url,
        "models": models_list,
        "enabled": p.enabled,
        "sort": p.sort,
        "remark": p.remark,
        "api_key_masked": masked,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get("")
async def list_providers(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:list"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all AI providers (paginated)."""
    items, total = await crud_ai_provider.get_multi(db, page=page, page_size=page_size)
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_provider_to_dict(p) for p in items],
    })


@router.get("/all")
async def list_all_providers(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:list"))],
):
    """List all enabled providers (for dropdown selection)."""
    providers = await crud_ai_provider.list_enabled(db)
    return success_response(data=[_provider_to_dict(p) for p in providers])


@router.post("")
async def create_provider(
    body: ProviderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:add"))],
):
    """Create a new AI provider."""
    exists = await crud_ai_provider.exists(db, name=body.name)
    if exists:
        raise ConflictException(f"供应商 '{body.name}' 已存在")

    provider = await crud_ai_provider.create(db, {
        "name": body.name,
        "provider_type": body.provider_type,
        "api_key_enc": encrypt_api_key(body.api_key),
        "base_url": body.base_url,
        "models": json.dumps(body.models, ensure_ascii=False),
        "enabled": body.enabled,
        "sort": body.sort,
        "remark": body.remark,
    })
    return success_response(data={"id": provider.id}, msg="创建成功")


@router.put("/{provider_id}")
async def update_provider(
    provider_id: int,
    body: ProviderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:edit"))],
):
    """Update an AI provider."""
    provider = await crud_ai_provider.get(db, provider_id)
    if not provider:
        raise NotFoundException("供应商不存在")

    update_data: dict = {}
    if body.name is not None:
        update_data["name"] = body.name
    if body.provider_type is not None:
        update_data["provider_type"] = body.provider_type
    if body.base_url is not None:
        update_data["base_url"] = body.base_url
    if body.models is not None:
        update_data["models"] = json.dumps(body.models, ensure_ascii=False)
    if body.enabled is not None:
        update_data["enabled"] = body.enabled
    if body.sort is not None:
        update_data["sort"] = body.sort
    if body.remark is not None:
        update_data["remark"] = body.remark
    if body.api_key is not None:
        update_data["api_key_enc"] = encrypt_api_key(body.api_key)

    if update_data:
        await crud_ai_provider.update(db, provider_id, update_data)

    return success_response(msg="更新成功")


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:delete"))],
):
    """Delete an AI provider (hard delete)."""
    provider = await crud_ai_provider.get(db, provider_id)
    if not provider:
        raise NotFoundException("供应商不存在")
    await crud_ai_provider.delete(db, provider_id, soft=False)
    return success_response(msg="删除成功")


@router.post("/{provider_id}/test")
async def test_provider(
    provider_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("ai:provider:list"))],
):
    """Test connectivity for an AI provider by calling the models endpoint."""
    import httpx

    provider = await crud_ai_provider.get(db, provider_id)
    if not provider:
        raise NotFoundException("供应商不存在")

    api_key = decrypt_api_key(provider.api_key_enc)
    base_url = provider.base_url or "https://api.deepseek.com"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            models = [m.get("id", "") for m in data.get("data", [])]
            return success_response(data={"ok": True, "models": models}, msg="连通成功")
    except httpx.HTTPStatusError as e:
        return success_response(data={"ok": False, "error": f"HTTP {e.response.status_code}"}, msg="连通失败")
    except Exception as e:
        return success_response(data={"ok": False, "error": str(e)}, msg="连通失败")
