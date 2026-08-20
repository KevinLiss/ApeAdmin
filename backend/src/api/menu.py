"""Menu management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import _build_menu_tree, get_current_user, require_permission
from src.core.exceptions import NotFoundException, success_response
from src.crud import crud_menu
from src.db import get_db
from src.models import User
from src.schemas import MenuCreate, MenuUpdate

router = APIRouter(prefix="/menus", tags=["菜单管理"])


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
    updated = await crud_menu.update(db, menu_id, body.model_dump(exclude_unset=True, exclude_none=True))
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
