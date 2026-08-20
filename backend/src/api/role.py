"""Role management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, require_permission
from src.core.exceptions import ConflictException, NotFoundException, success_response
from src.crud import crud_role
from src.db import get_db
from src.models import User
from src.schemas import RoleCreate, RoleUpdate

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("")
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:role:list"))],
    page: int = 1,
    page_size: int = 20,
):
    """Paginated role list."""
    items, total = await crud_role.get_multi(db, page=page, page_size=page_size)
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": r.id,
                    "name": r.name,
                    "code": r.code,
                    "data_scope": r.data_scope,
                    "sort": r.sort,
                    "status": r.status,
                    "remark": r.remark,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in items
            ],
        }
    )


@router.get("/all")
async def list_all_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Get all roles without pagination (for dropdowns/selects)."""
    items, _ = await crud_role.get_multi(db, page=1, page_size=1000)
    return success_response(
        data=[
            {"id": r.id, "name": r.name, "code": r.code}
            for r in items
            if r.status == 1
        ]
    )


@router.post("")
async def create_role(
    body: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:role:add"))],
):
    """Create a new role."""
    if await crud_role.exists(db, code=body.code):
        raise ConflictException(f"角色编码 '{body.code}' 已存在")
    new_role = await crud_role.create(db, body.model_dump(exclude={"menu_ids"}))
    if body.menu_ids:
        await crud_role.assign_menus(db, new_role.id, body.menu_ids)
    return success_response(data={"id": new_role.id}, msg="创建成功")


@router.get("/{role_id}")
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:role:list"))],
):
    """Get a single role with its menu IDs."""
    role = await crud_role.get(db, role_id)
    if not role:
        raise NotFoundException("角色不存在")
    from sqlalchemy import select
    menu_ids = [m.id for m in role.menus] if role.menus else []
    return success_response(
        data={
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "data_scope": role.data_scope,
            "sort": role.sort,
            "status": role.status,
            "remark": role.remark,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "menu_ids": menu_ids,
        }
    )


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    body: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:role:edit"))],
):
    """Update role info."""
    update_data = body.model_dump(exclude_unset=True, exclude_none=True)
    menu_ids = update_data.pop("menu_ids", None)

    updated = await crud_role.update(db, role_id, update_data)
    if not updated:
        raise NotFoundException("角色不存在")

    if menu_ids is not None:
        await crud_role.assign_menus(db, role_id, menu_ids)

    return success_response(msg="更新成功")


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:role:delete"))],
):
    """Soft-delete a role."""
    ok = await crud_role.delete(db, role_id, soft=True)
    if not ok:
        raise NotFoundException("角色不存在")
    return success_response(msg="删除成功")
