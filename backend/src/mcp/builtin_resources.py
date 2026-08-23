"""Built-in MCP resources and tools: system-level data sources + CRUD operations.

MCP Tools registered here are automatically available to:
1. The AI Agent (via ai/tools.py → build_tools_for_llm → MCP merge)
2. The MCP HTTP API (via mcp/routes.py → /mcp/tools/call)
3. The frontend MCP management page (via /mcp/tools)
"""

import json
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import SessionLocal
from src.mcp.manager import mcp_manager
from src.models import Dept, Menu, Role, User


def register_builtin_resources() -> None:
    """Register the core MCP resources, tools, and prompts."""

    # ---- Resources (read-only) ----
    mcp_manager.register_resource(
        uri="apeadmin://system/status",
        name="系统状态",
        description="获取系统运行状态信息，包括版本、运行时间等",
        handler=_get_system_status,
    )
    mcp_manager.register_resource(
        uri="apeadmin://users/count",
        name="用户统计",
        description="获取系统用户总数和活跃用户数",
        handler=_get_user_count,
    )
    mcp_manager.register_resource(
        uri="apeadmin://system/info",
        name="系统信息",
        description="系统基本信息（静态）",
        static_content=(
            "ApeAdmin v0.1.0\n"
            "FastAPI + Vue3 admin framework with plugin & MCP support\n"
            "Author: ApeAdmin Team"
        ),
    )

    # ---- System tools ----
    mcp_manager.register_tool(
        name="system_health_check",
        description="检查系统健康状态，返回各服务运行状况",
        handler=_health_check_tool,
    )
    mcp_manager.register_tool(
        name="system_list_plugins",
        description="列出所有已安装的插件及其状态",
        handler=_list_plugins_tool,
    )

    # ---- Role CRUD tools ----
    mcp_manager.register_tool(
        name="role_list",
        description="获取角色列表，支持关键词搜索。返回角色ID、名称、编码、数据范围、状态。",
        handler=_role_list,
        required_permissions=["system:role:list"],
    )
    mcp_manager.register_tool(
        name="role_create",
        description="创建新角色。需要提供角色名称和编码。",
        handler=_role_create,
        required_permissions=["system:role:add"],
    )
    mcp_manager.register_tool(
        name="role_update",
        description="更新角色信息。只传需要修改的字段。",
        handler=_role_update,
        required_permissions=["system:role:edit"],
    )
    mcp_manager.register_tool(
        name="role_delete",
        description="删除角色（软删除）。",
        handler=_role_delete,
        required_permissions=["system:role:delete"],
    )

    # ---- Department CRUD tools ----
    mcp_manager.register_tool(
        name="dept_list",
        description="获取部门树形结构。返回所有部门的完整信息。",
        handler=_dept_list,
        required_permissions=["system:dept:list"],
    )
    mcp_manager.register_tool(
        name="dept_create",
        description="创建新部门。需要提供部门名称，可指定父级ID（默认0=顶级）。",
        handler=_dept_create,
        required_permissions=["system:dept:add"],
    )
    mcp_manager.register_tool(
        name="dept_update",
        description="更新部门信息。只传需要修改的字段。",
        handler=_dept_update,
        required_permissions=["system:dept:edit"],
    )
    mcp_manager.register_tool(
        name="dept_delete",
        description="删除部门（软删除）。",
        handler=_dept_delete,
        required_permissions=["system:dept:delete"],
    )

    # ---- Menu CRUD tools ----
    mcp_manager.register_tool(
        name="menu_list",
        description="获取菜单树形结构。返回所有菜单（目录/菜单/按钮）的完整信息。",
        handler=_menu_list,
        required_permissions=["system:menu:list"],
    )
    mcp_manager.register_tool(
        name="menu_create",
        description="创建新菜单项。类型: M=目录 C=菜单 F=按钮。",
        handler=_menu_create,
        required_permissions=["system:menu:add"],
    )
    mcp_manager.register_tool(
        name="menu_update",
        description="更新菜单信息。只传需要修改的字段。",
        handler=_menu_update,
        required_permissions=["system:menu:edit"],
    )
    mcp_manager.register_tool(
        name="menu_delete",
        description="删除菜单项。",
        handler=_menu_delete,
        required_permissions=["system:menu:delete"],
    )

    # ---- Prompt ----
    mcp_manager.register_prompt(
        name="system_summary",
        description="生成系统运行概况摘要",
        template="请基于以下信息生成一份系统运行概况报告：\n系统名称：{system_name}\n版本：{version}\n检查时间：{check_time}",
        arguments=["system_name", "version", "check_time"],
    )


# ===========================================================================
# Resource handlers
# ===========================================================================

async def _get_system_status() -> str:
    from src.core.config import settings
    return (
        f"App: {settings.APP_NAME} v{settings.APP_VERSION}\n"
        f"Debug: {settings.DEBUG}\n"
        f"DB: {settings.DB_TYPE}\n"
        f"MCP: {'enabled' if settings.MCP_ENABLED else 'disabled'}\n"
        f"Plugins: {'enabled' if settings.PLUGINS_ENABLED else 'disabled'}"
    )


async def _get_user_count() -> str:
    from sqlalchemy import func
    async with SessionLocal() as db:
        result = await db.execute(
            select(func.count()).select_from(User).where(User.deleted_at.is_(None))
        )
        total = result.scalar() or 0
        active_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.deleted_at.is_(None), User.status == 1
            )
        )
        active = active_result.scalar() or 0
    return f"总用户数: {total}\n活跃用户数: {active}"


# ===========================================================================
# System tool handlers
# ===========================================================================

async def _health_check_tool() -> str:
    from src.core.config import settings
    return f"System healthy. {settings.APP_NAME} v{settings.APP_VERSION} is running."


async def _list_plugins_tool() -> str:
    from src.plugins import plugin_manager
    plugins = plugin_manager.list_plugins()
    if not plugins:
        return "No plugins installed."
    lines = [f"Installed plugins ({len(plugins)}):"]
    for p in plugins:
        status = "✓" if p.enabled else "✗"
        lines.append(f"  {status} {p.name} v{p.version} - {p.display_name}")
    return "\n".join(lines)


# ===========================================================================
# Role CRUD tool handlers
# ===========================================================================

async def _role_list(keyword: str = "") -> str:
    """获取角色列表，支持关键词搜索。"""
    async with SessionLocal() as db:
        stmt = select(Role).where(Role.deleted_at.is_(None))
        if keyword:
            stmt = stmt.where(or_(Role.name.ilike(f"%{keyword}%"), Role.code.ilike(f"%{keyword}%")))
        stmt = stmt.order_by(Role.sort, Role.id)
        result = await db.execute(stmt)
        roles = result.scalars().all()
    items = [
        {"id": r.id, "name": r.name, "code": r.code, "data_scope": r.data_scope,
         "status": r.status, "remark": r.remark, "sort": r.sort}
        for r in roles
    ]
    return json.dumps({"total": len(items), "items": items}, ensure_ascii=False)


async def _role_create(name: str, code: str, data_scope: int = 1,
                       sort: int = 0, remark: str = "", status: int = 1) -> str:
    """创建新角色。name=角色名称, code=角色编码（唯一）, data_scope=数据范围(1本人2本部门及以下3本部门4全部)。"""
    async with SessionLocal() as db:
        exists = await db.execute(select(Role).where(Role.code == code, Role.deleted_at.is_(None)))
        if exists.scalar_one_or_none():
            return json.dumps({"error": f"角色编码 '{code}' 已存在"}, ensure_ascii=False)
        role = Role(name=name, code=code, data_scope=data_scope, sort=sort,
                    remark=remark or None, status=status)
        db.add(role)
        await db.commit()
        await db.refresh(role)
    return json.dumps({"id": role.id, "name": role.name, "code": role.code, "message": "角色创建成功"}, ensure_ascii=False)


async def _role_update(role_id: int, name: str = "", code: str = "",
                       data_scope: int = -1, sort: int = -1,
                       remark: str = "", status: int = -1) -> str:
    """更新角色信息。只传需要修改的字段。role_id=角色ID。"""
    async with SessionLocal() as db:
        stmt = select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            return json.dumps({"error": "角色不存在"}, ensure_ascii=False)
        if name:
            role.name = name
        if code:
            role.code = code
        if data_scope != -1:
            role.data_scope = data_scope
        if sort != -1:
            role.sort = sort
        if remark:
            role.remark = remark
        if status != -1:
            role.status = status
        await db.commit()
    return json.dumps({"id": role_id, "message": "角色更新成功"}, ensure_ascii=False)


async def _role_delete(role_id: int) -> str:
    """删除角色（软删除）。role_id=角色ID。"""
    async with SessionLocal() as db:
        stmt = select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            return json.dumps({"error": "角色不存在"}, ensure_ascii=False)
        role.deleted_at = datetime.now(timezone.utc)
        await db.commit()
    return json.dumps({"message": "角色已删除"}, ensure_ascii=False)


# ===========================================================================
# Department CRUD tool handlers
# ===========================================================================

async def _dept_list() -> str:
    """获取部门树形结构。"""
    async with SessionLocal() as db:
        stmt = select(Dept).where(Dept.status == 1, Dept.deleted_at.is_(None)).order_by(Dept.sort, Dept.id)
        result = await db.execute(stmt)
        depts = result.scalars().all()
    items = [{"id": d.id, "name": d.name, "parent_id": d.parent_id,
              "leader": d.leader, "phone": d.phone, "sort": d.sort, "status": d.status}
             for d in depts]
    return json.dumps({"total": len(items), "items": items}, ensure_ascii=False)


async def _dept_create(name: str, parent_id: int = 0, leader: str = "",
                       phone: str = "", sort: int = 0, status: int = 1) -> str:
    """创建新部门。name=部门名称, parent_id=父级ID(0=顶级)。"""
    async with SessionLocal() as db:
        dept = Dept(name=name, parent_id=parent_id, leader=leader or None,
                    phone=phone or None, sort=sort, status=status)
        db.add(dept)
        await db.commit()
        await db.refresh(dept)
    return json.dumps({"id": dept.id, "name": dept.name, "message": "部门创建成功"}, ensure_ascii=False)


async def _dept_update(dept_id: int, name: str = "", parent_id: int = -1,
                       leader: str = "", phone: str = "", sort: int = -1,
                       status: int = -1) -> str:
    """更新部门信息。只传需要修改的字段。dept_id=部门ID。"""
    async with SessionLocal() as db:
        stmt = select(Dept).where(Dept.id == dept_id, Dept.deleted_at.is_(None))
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        if not dept:
            return json.dumps({"error": "部门不存在"}, ensure_ascii=False)
        if name:
            dept.name = name
        if parent_id != -1:
            dept.parent_id = parent_id
        if leader:
            dept.leader = leader
        if phone:
            dept.phone = phone
        if sort != -1:
            dept.sort = sort
        if status != -1:
            dept.status = status
        await db.commit()
    return json.dumps({"id": dept_id, "message": "部门更新成功"}, ensure_ascii=False)


async def _dept_delete(dept_id: int) -> str:
    """删除部门（软删除）。dept_id=部门ID。"""
    async with SessionLocal() as db:
        stmt = select(Dept).where(Dept.id == dept_id, Dept.deleted_at.is_(None))
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        if not dept:
            return json.dumps({"error": "部门不存在"}, ensure_ascii=False)
        dept.deleted_at = datetime.now(timezone.utc)
        await db.commit()
    return json.dumps({"message": "部门已删除"}, ensure_ascii=False)


# ===========================================================================
# Menu CRUD tool handlers
# ===========================================================================

async def _menu_list() -> str:
    """获取菜单树形结构。"""
    async with SessionLocal() as db:
        stmt = select(Menu).where(Menu.status == 1).order_by(Menu.sort, Menu.id)
        result = await db.execute(stmt)
        menus = result.scalars().all()
    items = [{"id": m.id, "name": m.name, "parent_id": m.parent_id, "type": m.type,
              "path": m.path, "permission": m.permission, "icon": m.icon,
              "sort": m.sort, "visible": m.visible, "status": m.status}
             for m in menus]
    return json.dumps({"total": len(items), "items": items}, ensure_ascii=False)


async def _menu_create(name: str, type: str = "C", parent_id: int = 0,
                       path: str = "", permission: str = "", icon: str = "",
                       sort: int = 0, visible: int = 1, status: int = 1,
                       component: str = "") -> str:
    """创建新菜单项。name=名称, type=类型(M目录/C菜单/F按钮), parent_id=父级ID(0=顶级)。"""
    async with SessionLocal() as db:
        menu = Menu(name=name, type=type, parent_id=parent_id,
                    path=path or None, permission=permission or None,
                    icon=icon or None, sort=sort, visible=visible,
                    status=status, component=component or None)
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
    return json.dumps({"id": menu.id, "name": menu.name, "message": "菜单创建成功"}, ensure_ascii=False)


async def _menu_update(menu_id: int, name: str = "", type: str = "",
                       parent_id: int = -1, path: str = "", permission: str = "",
                       icon: str = "", sort: int = -1, visible: int = -1,
                       status: int = -1, component: str = "") -> str:
    """更新菜单信息。只传需要修改的字段。menu_id=菜单ID。"""
    async with SessionLocal() as db:
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        if not menu:
            return json.dumps({"error": "菜单不存在"}, ensure_ascii=False)
        if name:
            menu.name = name
        if type:
            menu.type = type
        if parent_id != -1:
            menu.parent_id = parent_id
        if path:
            menu.path = path
        if permission:
            menu.permission = permission
        if icon:
            menu.icon = icon
        if sort != -1:
            menu.sort = sort
        if visible != -1:
            menu.visible = visible
        if status != -1:
            menu.status = status
        if component:
            menu.component = component
        await db.commit()
    return json.dumps({"id": menu_id, "message": "菜单更新成功"}, ensure_ascii=False)


async def _menu_delete(menu_id: int) -> str:
    """删除菜单项。menu_id=菜单ID。"""
    async with SessionLocal() as db:
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        if not menu:
            return json.dumps({"error": "菜单不存在"}, ensure_ascii=False)
        await db.delete(menu)
        await db.commit()
    return json.dumps({"message": "菜单已删除"}, ensure_ascii=False)
