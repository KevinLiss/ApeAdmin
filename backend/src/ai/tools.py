"""System tools that can be called by the AI agent.

Each tool is exposed to the LLM as a function-calling tool.
Execution respects the current user's RBAC permissions.
"""

import json
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Dept, Menu, Role, User

# ---------------------------------------------------------------------------
# Tool definitions for LLM function calling
# ---------------------------------------------------------------------------

SYSTEM_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_user_list",
            "description": "获取系统用户列表（分页）。返回用户ID、用户名、昵称、邮箱、手机、状态、角色信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "页码，默认1", "default": 1},
                    "page_size": {"type": "integer", "description": "每页数量，默认10", "default": 10},
                    "keyword": {"type": "string", "description": "搜索关键词（用户名或昵称）", "default": ""},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_detail",
            "description": "获取单个用户的详细信息，包括角色和部门。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "用户ID"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_user",
            "description": "创建新用户。需要提供用户名和密码。",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名（唯一）"},
                    "nickname": {"type": "string", "description": "昵称", "default": ""},
                    "password": {"type": "string", "description": "密码（至少6位）"},
                    "email": {"type": "string", "description": "邮箱", "default": ""},
                    "phone": {"type": "string", "description": "手机号", "default": ""},
                },
                "required": ["username", "password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_user",
            "description": "更新用户信息。只传需要修改的字段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "用户ID"},
                    "nickname": {"type": "string", "description": "昵称"},
                    "email": {"type": "string", "description": "邮箱"},
                    "phone": {"type": "string", "description": "手机号"},
                    "status": {"type": "integer", "description": "状态: 0=禁用 1=启用"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_user",
            "description": "删除用户（软删除）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "用户ID"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_role_list",
            "description": "获取所有角色列表。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_menu_tree",
            "description": "获取完整的菜单树形结构。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dept_tree",
            "description": "获取完整的部门树形结构。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_stats",
            "description": "获取系统统计信息：用户总数、角色总数、菜单总数、部门总数。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


# Permission mapping: tool name -> required permission
TOOL_PERMISSIONS: dict[str, list[str]] = {
    "get_user_list": ["system:user:list"],
    "get_user_detail": ["system:user:list"],
    "create_user": ["system:user:add"],
    "update_user": ["system:user:edit"],
    "delete_user": ["system:user:delete"],
    "get_role_list": ["system:role:list"],
    "get_menu_tree": ["system:menu:list"],
    "get_dept_tree": ["system:dept:list"],
    "get_system_stats": [],
}


# ---------------------------------------------------------------------------
# MCP tools integration
# ---------------------------------------------------------------------------

def build_tools_for_llm(enable_tools: bool) -> list[dict[str, Any]]:
    """Return the tools list for LLM function calling.

    Merges the hard-coded SYSTEM_TOOLS with all currently registered MCP tools,
    so the AI agent can invoke MCP tools (health check, plugin list, etc.).
    """
    if not enable_tools:
        return []

    tools = list(SYSTEM_TOOLS)

    # Merge registered MCP tools as function-calling definitions
    try:
        from src.mcp.manager import mcp_manager

        for t in mcp_manager.list_tools():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or f"MCP 工具: {t.name}",
                        "parameters": t.input_schema or {"type": "object", "properties": {}},
                    },
                }
            )
    except Exception as exc:  # MCP not enabled / import error — degrade gracefully
        logger.warning(f"Failed to merge MCP tools for LLM: {exc}")

    return tools


def check_tool_permission(tool_name: str, user_permissions: set[str]) -> bool:
    """Check if the user has permission to call a tool."""
    required = TOOL_PERMISSIONS.get(tool_name, [])
    if not required:
        return True
    if "*" in user_permissions:
        return True
    return any(p in user_permissions for p in required)


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    db: AsyncSession,
    user_permissions: set[str],
) -> str:
    """Execute a system tool by name and return the result as a JSON string."""
    if not check_tool_permission(tool_name, user_permissions):
        return json.dumps({"error": f"权限不足，无法调用工具: {tool_name}"}, ensure_ascii=False)

    handlers = {
        "get_user_list": _handle_get_user_list,
        "get_user_detail": _handle_get_user_detail,
        "create_user": _handle_create_user,
        "update_user": _handle_update_user,
        "delete_user": _handle_delete_user,
        "get_role_list": _handle_get_role_list,
        "get_menu_tree": _handle_get_menu_tree,
        "get_dept_tree": _handle_get_dept_tree,
        "get_system_stats": _handle_get_system_stats,
    }

    handler = handlers.get(tool_name)
    if handler:
        try:
            result = await handler(db, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": f"工具执行失败: {e}"}, ensure_ascii=False)

    # MCP tools: try registered MCP tools as fallback
    try:
        from src.mcp.manager import mcp_manager

        # Permission check: MCP tool call requires mcp:tools:call (super admin has "*")
        if "mcp:tools:call" not in user_permissions and "*" not in user_permissions:
            return json.dumps({"error": f"权限不足，无法调用 MCP 工具: {tool_name}"}, ensure_ascii=False)

        available = mcp_manager.list_tools(user_permissions)
        if tool_name not in {t.name for t in available}:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)

        result = await mcp_manager.call_tool(tool_name, arguments)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": f"MCP 工具执行失败: {e}"}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

async def _handle_get_user_list(db: AsyncSession, args: dict) -> dict:
    page = max(1, args.get("page", 1))
    page_size = min(100, max(1, args.get("page_size", 10)))
    keyword = args.get("keyword", "")

    stmt = select(User).where(User.deleted_at.is_(None))
    if keyword:
        stmt = stmt.where(or_(User.username.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%")))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size).order_by(User.id.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()

    count_stmt = select(User).where(User.deleted_at.is_(None))
    if keyword:
        count_stmt = count_stmt.where(
            or_(User.username.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%"))
        )
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    return {
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
                "status": u.status,
                "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in u.roles],
            }
            for u in users
        ],
    }


async def _handle_get_user_detail(db: AsyncSession, args: dict) -> dict:
    user_id = args.get("user_id")
    if not user_id:
        return {"error": "缺少参数: user_id"}
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    u = result.scalar_one_or_none()
    if not u:
        return {"error": "用户不存在"}
    return {
        "id": u.id,
        "username": u.username,
        "nickname": u.nickname,
        "email": u.email,
        "phone": u.phone,
        "status": u.status,
        "dept_id": u.dept_id,
        "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in u.roles],
    }


async def _handle_create_user(db: AsyncSession, args: dict) -> dict:
    from src.core.security import hash_password

    username = args.get("username", "")
    password = args.get("password", "")
    if not username or not password:
        return {"error": "用户名和密码不能为空"}

    exists = await db.execute(select(User).where(User.username == username, User.deleted_at.is_(None)))
    if exists.scalar_one_or_none():
        return {"error": f"用户名 '{username}' 已存在"}

    user = User(
        username=username,
        nickname=args.get("nickname", username),
        password=hash_password(password),
        email=args.get("email") or None,
        phone=args.get("phone") or None,
        status=1,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "message": "用户创建成功"}


async def _handle_update_user(db: AsyncSession, args: dict) -> dict:
    user_id = args.get("user_id")
    if not user_id:
        return {"error": "缺少参数: user_id"}

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "用户不存在"}

    for field in ("nickname", "email", "phone", "status"):
        if field in args and args[field] is not None:
            setattr(user, field, args[field])

    await db.commit()
    return {"id": user.id, "message": "用户更新成功"}


async def _handle_delete_user(db: AsyncSession, args: dict) -> dict:
    user_id = args.get("user_id")
    if not user_id:
        return {"error": "缺少参数: user_id"}

    from datetime import datetime, timezone

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "用户不存在"}

    user.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "用户已删除"}


async def _handle_get_role_list(db: AsyncSession, args: dict) -> dict:
    stmt = select(Role).where(Role.deleted_at.is_(None)).order_by(Role.sort, Role.id)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "data_scope": r.data_scope,
                "status": r.status,
                "remark": r.remark,
            }
            for r in roles
        ]
    }


async def _handle_get_menu_tree(db: AsyncSession, args: dict) -> dict:
    stmt = select(Menu).where(Menu.status == 1).order_by(Menu.sort, Menu.id)
    result = await db.execute(stmt)
    menus = result.scalars().all()

    def build_tree(items: list, parent_id: int = 0) -> list:
        tree = []
        for m in items:
            if m.parent_id == parent_id:
                node = {
                    "id": m.id,
                    "name": m.name,
                    "type": m.type,
                    "path": m.path,
                    "permission": m.permission,
                    "icon": m.icon,
                    "sort": m.sort,
                    "children": build_tree(items, m.id),
                }
                tree.append(node)
        return tree

    return {"tree": build_tree(list(menus))}


async def _handle_get_dept_tree(db: AsyncSession, args: dict) -> dict:
    stmt = select(Dept).where(Dept.status == 1, Dept.deleted_at.is_(None)).order_by(Dept.sort, Dept.id)
    result = await db.execute(stmt)
    depts = result.scalars().all()

    def build_tree(items: list, parent_id: int = 0) -> list:
        tree = []
        for d in items:
            if d.parent_id == parent_id:
                node = {
                    "id": d.id,
                    "name": d.name,
                    "leader": d.leader,
                    "phone": d.phone,
                    "sort": d.sort,
                    "children": build_tree(items, d.id),
                }
                tree.append(node)
        return tree

    return {"tree": build_tree(list(depts))}


async def _handle_get_system_stats(db: AsyncSession, args: dict) -> dict:
    user_count = len((await db.execute(select(User).where(User.deleted_at.is_(None)))).scalars().all())
    role_count = len((await db.execute(select(Role).where(Role.deleted_at.is_(None)))).scalars().all())
    menu_count = len((await db.execute(select(Menu).where(Menu.status == 1))).scalars().all())
    dept_count = len((await db.execute(select(Dept).where(Dept.deleted_at.is_(None)))).scalars().all())
    return {
        "user_count": user_count,
        "role_count": role_count,
        "menu_count": menu_count,
        "dept_count": dept_count,
    }
