"""FastAPI dependency injection: authentication, current user, permission checking.

Implements FastAdmin's four-layer permission model:
1. No-auth (免登录)   — no dependency
2. Auth-only (免鉴权)  — Depends(get_current_user)
3. Rule-based (规则鉴权) — Depends(require_permission("system:user:add"))
4. Data-scope (数据权限) — Depends(get_current_user) + data_scope filtering in service
"""

from typing import Annotated, Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import AuthException, PermissionException
from src.core.security import decode_token
from src.crud import crud_user
from src.db import get_db
from src.models import Menu, Role, User

# Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the current authenticated user from the Bearer token."""
    if credentials is None:
        raise AuthException("Missing authentication token")

    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise AuthException("Invalid or expired token")

    # Logout revocation: reject tokens whose jti was blacklisted.
    # Pre-feature tokens carry no jti and age out naturally.
    # Fast path: Redis flag "bl:<jti>" set at logout (TTL = token lifetime)
    # avoids the DB query on every authenticated request; DB remains the
    # source of truth (fallback path + flag written on logout).
    jti = payload.get("jti")
    if jti:
        from sqlalchemy import select

        from src.core.redis_client import kv_get
        from src.models import TokenBlacklist

        flag = await kv_get("bl", jti)
        if flag == "1":
            raise AuthException("Token has been revoked")
        blacklisted = (
            await db.execute(
                select(TokenBlacklist.id).where(TokenBlacklist.jti == jti).limit(1)
            )
        ).scalar()
        if blacklisted:
            raise AuthException("Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException("Invalid token payload")

    # Attach user to request state for downstream use
    # User.roles and Role.menus use lazy="selectin", so they are
    # already loaded here without triggering sync lazy-loading.
    user = await crud_user.get(db, int(user_id))
    if not user:
        raise AuthException("User not found")
    if user.status != 1:
        raise AuthException("Account disabled")

    # Store on request state
    request.state.user = user
    return user


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Alias for get_current_user, can add extra checks."""
    return user


def require_permission(permission: str) -> Callable:
    """Return a dependency that checks if the current user has the given permission.

    The permission string matches the `sys_menu.permission` field, e.g. "system:user:add".
    Super admin (username == settings.SUPER_ADMIN_USERNAME) bypasses permission checks.
    """
    async def _checker(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        # Super admin bypass
        if user.username == settings.SUPER_ADMIN_USERNAME:
            return user

        # Gather all permission strings from the user's roles' menus
        user_permissions: set[str] = set()
        for role in user.roles:
            if role.status != 1:
                continue
            for menu in role.menus:
                if menu.permission and menu.status == 1:
                    user_permissions.add(menu.permission)

        if permission not in user_permissions:
            raise PermissionException(f"Missing permission: {permission}")

        return user

    return _checker


def get_user_permissions(user: User) -> set[str]:
    """Extract all permission strings for a user (for frontend menu rendering)."""
    if user.username == settings.SUPER_ADMIN_USERNAME:
        return {"*"}  # Wildcard = all permissions

    perms: set[str] = set()
    for role in user.roles:
        if role.status != 1:
            continue
        for menu in role.menus:
            if menu.permission and menu.status == 1:
                perms.add(menu.permission)
    return perms


def get_user_menu_tree(user: User) -> list[dict]:
    """Build a tree of menus the user can access (for frontend dynamic routing)."""
    if user.username == settings.SUPER_ADMIN_USERNAME:
        # Return all menus - handled at the API level
        return []

    seen: set[int] = set()
    menus: list[Menu] = []
    for role in user.roles:
        if role.status != 1:
            continue
        for menu in role.menus:
            if menu.id not in seen and menu.status == 1 and menu.visible == 1:
                seen.add(menu.id)
                menus.append(menu)

    return _build_menu_tree(menus)


def _build_menu_tree(menus: list[Menu], parent_id: int = 0) -> list[dict]:
    """Recursively build a tree structure from a flat menu list."""
    tree: list[dict] = []
    for menu in menus:
        if menu.parent_id == parent_id:
            node = {
                "id": menu.id,
                "name": menu.name,
                "parent_id": menu.parent_id,
                "type": menu.type,
                "path": menu.path,
                "component": menu.component,
                "permission": menu.permission,
                "icon": menu.icon,
                "sort": menu.sort,
                "visible": menu.visible,
                "status": menu.status,
                "children": _build_menu_tree(menus, menu.id),
            }
            tree.append(node)
    tree.sort(key=lambda x: x.get("sort", 0))
    return tree


# ---------------------------------------------------------------------------
# Layer 4 — data scope (数据权限)
# ---------------------------------------------------------------------------
# Role.data_scope: 1=本人 2=本部门及以下 3=本部门 4=全部.
# The scope filter is applied by list endpoints; scope 4 (or the superadmin)
# bypasses filtering. Currently wired into the user list; other resources
# should reuse ``user_data_scope_filters`` as they gain scope awareness.


def get_user_data_scope(user: User) -> int:
    """Most permissive scope across the user's active roles (4 = widest)."""
    if user.username == settings.SUPER_ADMIN_USERNAME:
        return 4
    scopes = [r.data_scope or 1 for r in user.roles if r.status == 1]
    return max(scopes) if scopes else 1


def _collect_dept_subtree(flat_depts, root_id: int | None) -> set[int]:
    """Collect a department and all its descendants from a flat dept list."""
    if root_id is None:
        return set()
    children_by_parent: dict[int, list[int]] = {}
    for d in flat_depts:
        children_by_parent.setdefault(d.parent_id, []).append(d.id)
    ids: set[int] = set()
    stack = [root_id]
    while stack:
        current = stack.pop()
        ids.add(current)
        stack.extend(children_by_parent.get(current, []))
    return ids


async def user_data_scope_filters(db: AsyncSession, user: User, model) -> list:
    """Build SQLAlchemy filters restricting ``model`` rows by data scope.

    ``model`` must expose ``id`` (owner semantics) and ``dept_id`` columns.
    Returns an empty list when the user sees everything (scope 4 / superadmin).
    """
    scope = get_user_data_scope(user)
    if scope >= 4:
        return []

    from src.crud import crud_dept

    if scope == 1:  # 本人 — the user themselves (User model semantics)
        return [model.id == user.id]
    if scope == 3:  # 本部门
        if user.dept_id:
            return [model.dept_id == user.dept_id]
        return [model.id == user.id]
    # scope == 2 — 本部门及以下
    subtree = _collect_dept_subtree(await crud_dept.get_tree(db), user.dept_id)
    if not subtree:
        return [model.id == user.id]
    return [model.dept_id.in_(subtree)]
