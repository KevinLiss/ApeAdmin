"""Menu management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import _build_menu_tree, get_current_user, require_permission
from src.core.exceptions import NotFoundException, ValidationException, success_response
from src.crud import crud_menu
from src.db import get_db
from src.models import User
from src.schemas import MenuCreate, MenuUpdate

router = APIRouter(prefix="/menus", tags=["菜单管理"])


async def _validate_parent(db: AsyncSession, parent_id: int, menu_id: int | None = None) -> None:
    """Validate that a menu parent exists and cannot create an invalid hierarchy."""
    if parent_id == 0:
        return

    menus = await crud_menu.get_tree(db)
    by_id = {menu.id: menu for menu in menus}
    parent = by_id.get(parent_id)
    if parent is None:
        raise ValidationException("父级菜单不存在")
    if parent.type == "F":
        raise ValidationException("按钮类型不能作为父级菜单")

    visited: set[int] = set()
    current_id = parent_id
    while current_id:
        if current_id == menu_id:
            raise ValidationException("不能选择当前菜单或其下级作为父级")
        if current_id in visited:
            raise ValidationException("菜单层级存在循环，请先修复父级关系")
        visited.add(current_id)
        current = by_id.get(current_id)
        if current is None:
            raise ValidationException("菜单层级引用了不存在的父级")
        current_id = current.parent_id


@router.get("/tree")
async def menu_tree(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:menu:list"))],
):
    """Get the full menu tree (flat list → tree on server side)."""
    menus = await crud_menu.get_tree(db)
    tree = _build_menu_tree(menus)
    return success_response(data=tree)


@router.post("")
async def create_menu(
    body: MenuCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:menu:add"))],
):
    """Create a new menu item."""
    await _validate_parent(db, body.parent_id)
    new_menu = await crud_menu.create(db, body.model_dump())
    return success_response(data={"id": new_menu.id}, msg="创建成功")


@router.put("/{menu_id}")
async def update_menu(
    menu_id: int,
    body: MenuUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:menu:edit"))],
):
    """Update a menu item."""
    existing = await crud_menu.get(db, menu_id)
    if not existing:
        raise NotFoundException("菜单不存在")

    update_data = body.model_dump(exclude_unset=True)
    if "parent_id" in update_data:
        # The frontend sends null when a clearable parent selector is emptied.
        # Persist root menus using the system-wide parent_id=0 convention.
        update_data["parent_id"] = update_data["parent_id"] or 0
        await _validate_parent(db, update_data["parent_id"], menu_id)

    updated = await crud_menu.update(db, menu_id, update_data)
    if not updated:
        raise NotFoundException("菜单不存在")
    return success_response(msg="更新成功")


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:menu:delete"))],
):
    """Delete a menu item."""
    ok = await crud_menu.delete(db, menu_id, soft=False)
    if not ok:
        raise NotFoundException("菜单不存在")
    return success_response(msg="删除成功")
