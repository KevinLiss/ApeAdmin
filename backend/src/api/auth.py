"""Authentication routes: login, refresh, logout, user info, profile."""

from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.i18n import t, get_locale
from src.core import auth_guard
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


class LogoutSchema(BaseModel):
    """Logout body — the frontend also sends the stored refresh token so
    it can be revoked together with the access token."""

    refresh_token: str | None = Field(default=None, max_length=4096)

router = APIRouter(prefix="/auth", tags=["认证管理"])


async def _blacklist_token(db: AsyncSession, user_id: int, payload: dict) -> None:
    """Blacklist one decoded token payload (DB row + Redis fast-path flag).

    Shared by logout for both the access token and the refresh token so a
    stolen refresh token cannot outlive the session it belonged to.
    """
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        return
    from sqlalchemy import delete

    from src.core.redis_client import kv_set
    from src.models import TokenBlacklist

    db.add(
        TokenBlacklist(
            jti=jti,
            user_id=user_id,
            token_type=payload.get("type", "access"),
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
        )
    )
    # Opportunistic cleanup: drop entries whose tokens already expired.
    await db.execute(
        delete(TokenBlacklist).where(
            TokenBlacklist.expires_at < datetime.now(timezone.utc)
        )
    )
    await db.commit()
    # Redis fast-path flag: get_current_user checks this before hitting
    # the DB. TTL = remaining token lifetime (same as the DB row).
    remaining = max(1, int(exp - datetime.now(timezone.utc).timestamp()))
    await kv_set("bl", jti, "1", ttl=remaining)


async def _login_captcha_enabled(db: AsyncSession) -> bool:
    """Read the ``login_captcha_enabled`` sys_setting (default off)."""
    from src.crud import crud_setting

    value = await crud_setting.get_value(db, "login_captcha_enabled", "0")
    return value.strip().lower() in ("1", "true", "yes", "on")


@router.post("/login")
async def login(
    body: LoginSchema,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """User login — returns JWT access + refresh tokens.

    Brute-force guard: after {MAX_FAILURES} consecutive failures for the
    same (username, IP) pair the pair is locked for {LOCK_SECONDS}s.
    """
    locale = get_locale(request)
    client_ip = request.client.host if request.client else "unknown"

    lock = await auth_guard.check_lock(body.username, client_ip)
    if lock.locked:
        raise AuthException(
            t("auth.too_many_attempts", locale, minutes=max(1, lock.retry_after // 60 + 1))
        )

    # Server-side captcha gate (off by default; enable via sys_setting
    # ``login_captcha_enabled``). Previously the slider was purely a UX
    # gate and login requests carried no verifiable proof.
    if await _login_captcha_enabled(db):
        if not body.captcha_id or not body.captcha_code:
            raise AuthException(t("auth.captcha_required", locale))
        from src.core import captcha as _captcha

        if not _captcha.verify(body.captcha_id, body.captcha_code):
            raise AuthException(t("auth.captcha_invalid", locale))

    from src.plugins import plugin_manager
    await plugin_manager.before_login(body.model_dump())
    user = await crud_user.authenticate(db, body.username, body.password)
    if not user:
        result = await auth_guard.record_failure(body.username, client_ip)
        if result.locked:
            raise AuthException(
                t("auth.too_many_attempts", locale, minutes=max(1, result.retry_after // 60 + 1))
            )
        raise AuthException(t("auth.login_failed", locale))

    await auth_guard.record_success(body.username, client_ip)

    # Update last login info
    from sqlalchemy import update
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
        msg=t("auth.login_success", locale),
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a refresh token for a new access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthException(t("auth.invalid_refresh_token"))

    # Honor logout revocation for refresh tokens too.
    from sqlalchemy import select

    from src.models import TokenBlacklist

    jti = payload.get("jti")
    if jti:
        blacklisted = (
            await db.execute(
                select(TokenBlacklist.id).where(TokenBlacklist.jti == jti).limit(1)
            )
        ).scalar()
        if blacklisted:
            raise AuthException(t("auth.token_revoked"))

    user_id = payload.get("sub")
    user = await crud_user.get(db, int(user_id))
    if not user or user.status != 1:
        raise AuthException(t("auth.user_not_found_or_disabled"))

    new_access = create_access_token(user.id)
    return success_response(data={"access_token": new_access, "token_type": "bearer"})


@router.post("/logout")
async def logout(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: LogoutSchema | None = None,
):
    """Logout — blacklist the presented access token until its natural expiry.

    If the client also submits its stored refresh token, that one is
    blacklisted too: without this a leaked refresh token could mint fresh
    access tokens for up to ``JWT_REFRESH_EXPIRE_DAYS`` days after logout.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token) if token else None
    if payload:
        await _blacklist_token(db, user.id, payload)

    # Revoke the companion refresh token when the client provides one.
    refresh_token = (body.refresh_token if body else None) or ""
    refresh_payload = decode_token(refresh_token) if refresh_token else None
    if refresh_payload and refresh_payload.get("type") == "refresh":
        await _blacklist_token(db, user.id, refresh_payload)
    return success_response(msg=t("auth.logout_success"))


@router.get("/captcha-config")
async def captcha_config(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Whether the login flow requires a server-verified captcha."""
    return success_response(data={"enabled": await _login_captcha_enabled(db)})


@router.get("/captcha")
async def new_captcha():
    """Issue a signed arithmetic captcha (stateless, multi-worker safe)."""
    from src.core import captcha as _captcha

    return success_response(data=_captcha.generate())


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
        return success_response(data={"id": user.id}, msg=t("auth.profile_no_change"))

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
        msg=t("auth.profile_updated"),
    )


@router.put("/profile/password")
async def change_password(
    body: PasswordChangeSchema,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change current user's password (requires old password)."""
    if not verify_password(body.old_password, user.password):
        raise AuthException(t("auth.old_password_wrong"))

    if body.new_password == body.old_password:
        raise AuthException(t("auth.new_password_same_as_old"))

    await crud_user.update_password(db, user.id, body.new_password)
    return success_response(msg=t("auth.password_changed_relogin"))
