"""Department management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user, require_permission
from src.core.exceptions import NotFoundException, success_response
from src.crud import crud_dept
from src.db import get_db
from src.models import Dept, User
from src.schemas import DeptCreate, DeptUpdate

router = APIRouter(prefix="/depts", tags=["部门管理"])


def _build_dept_tree(depts: list[Dept], parent_id: int = 0) -> list[dict]:
    """Recursively build a tree structure from a flat dept list."""
    tree: list[dict] = []
    for d in depts:
        if d.parent_id == parent_id:
            node = {
                "id": d.id,
                "name": d.name,
                "parent_id": d.parent_id,
                "sort": d.sort,
                "leader": d.leader,
                "phone": d.phone,
                "status": d.status,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "children": _build_dept_tree(depts, d.id),
            }
            tree.append(node)
    tree.sort(key=lambda x: x.get("sort", 0))
    return tree


@router.get("/tree")
async def dept_tree(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:dept:list"))],
):
    """Get the full department tree."""
    depts = await crud_dept.get_tree(db)
    tree = _build_dept_tree(depts)
    return success_response(data=tree)


@router.post("")
async def create_dept(
    body: DeptCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:dept:add"))],
):
    """Create a new department."""
    new_dept = await crud_dept.create(db, body.model_dump())
    return success_response(data={"id": new_dept.id}, msg="创建成功")


@router.put("/{dept_id}")
async def update_dept(
    dept_id: int,
    body: DeptUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:dept:edit"))],
):
    """Update a department."""
    updated = await crud_dept.update(db, dept_id, body.model_dump(exclude_unset=True, exclude_none=True))
    if not updated:
        raise NotFoundException("部门不存在")
    return success_response(msg="更新成功")


@router.delete("/{dept_id}")
async def delete_dept(
    dept_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:dept:delete"))],
):
    """Soft-delete a department."""
    ok = await crud_dept.delete(db, dept_id, soft=True)
    if not ok:
        raise NotFoundException("部门不存在")
    return success_response(msg="删除成功")
