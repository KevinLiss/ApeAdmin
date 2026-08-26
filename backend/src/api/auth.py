"""Authentication routes: login, refresh, logout, user info, profile."""

from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.deps import (
    get_current_user,
    get_user_menu_tree,
    get_user_permissions,
)
from src.core.exceptions import AuthException, success_response
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.crud import crud_user
from src.db import get_db
from src.models import User
from src.schemas import LoginSchema, TokenSchema


class ProfileUpdateSchema(BaseModel):
    """Update current user's profile fields."""

    nickname: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    avatar: str | None = Field(default=None, max_length=500)


class PasswordChangeSchema(BaseModel):
    """Change current user's password."""

    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login")
async def login(
    body: LoginSchema,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """User login — returns JWT access + refresh tokens."""
    from src.plugins import plugin_manager
    await plugin_manager.before_login(body.model_dump())
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

    access = create_access_token(user.id, extra={"username": user.username})
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
        # Super admins bypass permission checks, but disabled/hidden menus
        # must still stay out of the sidebar after a plugin is turned off.
        menu_tree = _build_menu_tree(
            [menu for menu in all_menus if menu.status == 1 and menu.visible == 1]
        )
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


@router.get("/profile")
async def get_profile(
    user: Annotated[User, Depends(get_current_user)],
):
    """Get current user's profile details (for 个人中心)."""
    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "dept_id": user.dept_id,
            "dept": {"id": user.dept.id, "name": user.dept.name} if user.dept else None,
            "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in user.roles],
            "status": user.status,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "last_login_ip": user.last_login_ip,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    )


@router.put("/profile")
async def update_profile(
    body: ProfileUpdateSchema,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user's own profile."""
    payload = body.model_dump(exclude_unset=True, exclude_none=True)
    if not payload:
        return success_response(data={"id": user.id}, msg="无修改内容")

    await crud_user.update(db, user.id, payload)
    # Refresh user object to return fresh data
    refreshed = await crud_user.get(db, user.id)
    return success_response(
        data={
            "id": refreshed.id,
            "username": refreshed.username,
            "nickname": refreshed.nickname,
            "email": refreshed.email,
            "phone": refreshed.phone,
            "avatar": refreshed.avatar,
        },
        msg="资料更新成功",
    )


@router.put("/profile/password")
async def change_password(
    body: PasswordChangeSchema,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change current user's password (requires old password)."""
    if not verify_password(body.old_password, user.password):
        raise AuthException("原密码不正确")

    if body.new_password == body.old_password:
        raise AuthException("新密码不能与原密码相同")

    await crud_user.update_password(db, user.id, body.new_password)
    return success_response(msg="密码修改成功，请重新登录")
