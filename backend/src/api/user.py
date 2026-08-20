"""User management routes."""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, require_permission
from src.core.exceptions import ConflictException, NotFoundException, success_response
from src.crud import crud_user
from src.db import get_db
from src.models import User
from src.schemas import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:list"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, description="搜索用户名/昵称"),
    status: int | None = Query(None, description="状态筛选"),
):
    """Paginated user list with optional search."""
    filters = []
    if keyword:
        filters.append(
            or_(User.username.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%"))
        )
    if status is not None:
        filters.append(User.status == status)

    items, total = await crud_user.get_multi(
        db, page=page, page_size=page_size, filters=filters
    )
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": u.id,
                    "username": u.username,
                    "nickname": u.nickname,
                    "email": u.email,
                    "phone": u.phone,
                    "dept_id": u.dept_id,
                    "status": u.status,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in u.roles],
                    "dept": {"id": u.dept.id, "name": u.dept.name} if u.dept else None,
                }
                for u in items
            ],
        }
    )


@router.post("")
async def create_user(
    body: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:add"))],
):
    """Create a new user."""
    exists = await crud_user.exists(db, username=body.username)
    if exists:
        raise ConflictException(f"用户名 '{body.username}' 已存在")

    new_user = await crud_user.create(db, body.model_dump(exclude={"role_ids"}))
    if body.role_ids:
        await crud_user.assign_roles(db, new_user.id, body.role_ids)

    return success_response(data={"id": new_user.id}, msg="创建成功")


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:list"))],
):
    """Get a single user by ID."""
    u = await crud_user.get(db, user_id)
    if not u:
        raise NotFoundException("用户不存在")
    return success_response(
        data={
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "email": u.email,
            "phone": u.phone,
            "dept_id": u.dept_id,
            "status": u.status,
            "avatar": u.avatar,
            "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in u.roles],
        }
    )


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:edit"))],
):
    """Update user info."""
    update_data = body.model_dump(exclude_unset=True, exclude_none=True)
    role_ids = update_data.pop("role_ids", None)

    updated = await crud_user.update(db, user_id, update_data)
    if not updated:
        raise NotFoundException("用户不存在")

    if role_ids is not None:
        await crud_user.assign_roles(db, user_id, role_ids)

    return success_response(msg="更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:delete"))],
):
    """Soft-delete a user."""
    ok = await crud_user.delete(db, user_id, soft=True)
    if not ok:
        raise NotFoundException("用户不存在")
    return success_response(msg="删除成功")


@router.put("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    new_password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:user:reset-password"))],
):
    """Admin reset a user's password."""
    ok = await crud_user.update_password(db, user_id, new_password)
    if not ok:
        raise NotFoundException("用户不存在")
    return success_response(msg="密码已重置")
