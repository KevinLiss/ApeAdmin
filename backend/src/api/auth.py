"""Authentication routes: login, refresh, logout, user info."""

from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import (
    get_current_user,
    get_user_menu_tree,
    get_user_permissions,
)
from src.core.exceptions import AuthException, success_response
from src.core.security import create_access_token, create_refresh_token, decode_token
from src.crud import crud_user
from src.db import get_db
from src.models import User
from src.schemas import LoginSchema, TokenSchema

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login")
async def login(
    body: LoginSchema,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """User login — returns JWT access + refresh tokens."""
    user = await crud_user.authenticate(db, body.username, body.password)
    if not user:
        raise AuthException("用户名或密码错误")

    # Update last login info
    from sqlalchemy import update
    client_ip = request.client.host if request.client else "unknown"
    stmt = (
        update(User)
        .where(User.id == user.id)
        .values(last_login_at=datetime.now(timezone.utc), last_login_ip=client_ip)
    )
    await db.execute(stmt)
    await db.commit()

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return success_response(
        data={
            "access_token": access,
            "token_type": "bearer",
            "refresh_token": refresh,
        },
        msg="登录成功",
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a refresh token for a new access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthException("Invalid refresh token")

    user_id = payload.get("sub")
    user = await crud_user.get(db, int(user_id))
    if not user or user.status != 1:
        raise AuthException("User not found or disabled")

    new_access = create_access_token(user.id)
    return success_response(data={"access_token": new_access, "token_type": "bearer"})


@router.post("/logout")
async def logout(
    user: Annotated[User, Depends(get_current_user)],
):
    """Logout — stateless JWT, client just discards the token."""
    return success_response(msg="已退出登录")


@router.get("/userinfo")
async def user_info(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current user info, permissions, and menu tree."""
    permissions = get_user_permissions(user)

    # For super admin, return all menus
    if user.username == settings.SUPER_ADMIN_USERNAME:
        from src.crud import crud_menu
        all_menus = await crud_menu.get_tree(db)
        from src.core.deps import _build_menu_tree
        menu_tree = _build_menu_tree(all_menus)
    else:
        menu_tree = get_user_menu_tree(user)

    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "permissions": list(permissions),
            "menus": menu_tree,
            "roles": [r.code for r in user.roles],
        }
    )
