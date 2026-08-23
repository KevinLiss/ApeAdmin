"""Seed initial data: super admin, default role, default menus.

Creates:
- 1 super admin user (admin / admin123)
- 1 default admin role with all menus
- Full menu tree matching the frontend routes (system:user, system:role, etc.)
"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import hash_password
from src.db import SessionLocal
from src.models import Dept, Menu, Role, User


async def seed_initial_data() -> None:
    """Seed the database with essential initial data if not already present."""
    async with SessionLocal() as db:
        await _seed_dept(db)
        await _seed_menus(db)
        await _seed_role(db)
        await _seed_super_admin(db)
        await db.commit()
    logger.info("Initial data seeded")


async def _seed_dept(db: AsyncSession) -> None:
    """Create a default root department if none exists."""
    result = await db.execute(select(Dept).where(Dept.parent_id == 0))
    if result.scalars().first():
        return
    root = Dept(
        name="ApeAdmin",
        parent_id=0,
        sort=0,
        leader="admin",
        phone="",
        status=1,
    )
    db.add(root)
    await db.flush()
    logger.info("Created root department 'ApeAdmin'")


async def _seed_menus(db: AsyncSession) -> None:
    """Create the default system management menu tree."""
    # Check if any menus exist
    result = await db.execute(select(Menu).limit(1))
    if result.scalars().first():
        # Incremental seeding: add any missing MCP/AI sub-menus on existing installs
        await _seed_missing_menus(db)
        return

    menus_data = [
        # (name, parent_key, type, path, component, permission, icon, sort)
        ("系统管理", None, "M", "/system", None, None, "Setting", 10),
        ("用户管理", "系统管理", "C", "user", "system/user/index", "system:user:list", "User", 1),
        ("新增用户", "用户管理", "F", None, None, "system:user:add", None, 1),
        ("编辑用户", "用户管理", "F", None, None, "system:user:edit", None, 2),
        ("删除用户", "用户管理", "F", None, None, "system:user:delete", None, 3),
        ("重置密码", "用户管理", "F", None, None, "system:user:reset-password", None, 4),
        ("角色管理", "系统管理", "C", "role", "system/role/index", "system:role:list", "UserFilled", 2),
        ("新增角色", "角色管理", "F", None, None, "system:role:add", None, 1),
        ("编辑角色", "角色管理", "F", None, None, "system:role:edit", None, 2),
        ("删除角色", "角色管理", "F", None, None, "system:role:delete", None, 3),
        ("菜单管理", "系统管理", "C", "menu", "system/menu/index", "system:menu:list", "Menu", 3),
        ("新增菜单", "菜单管理", "F", None, None, "system:menu:add", None, 1),
        ("编辑菜单", "菜单管理", "F", None, None, "system:menu:edit", None, 2),
        ("删除菜单", "菜单管理", "F", None, None, "system:menu:delete", None, 3),
        ("部门管理", "系统管理", "C", "dept", "system/dept/index", "system:dept:list", "OfficeBuilding", 4),
        ("新增部门", "部门管理", "F", None, None, "system:dept:add", None, 1),
        ("编辑部门", "部门管理", "F", None, None, "system:dept:edit", None, 2),
        ("删除部门", "部门管理", "F", None, None, "system:dept:delete", None, 3),
        ("插件管理", "系统管理", "C", "plugin", "system/plugin/index", "system:plugin:list", "Box", 5),
        ("启用/禁用插件", "插件管理", "F", None, None, "system:plugin:toggle", None, 1),
        ("插件配置", "插件管理", "F", None, None, "system:plugin:config", None, 2),
        # MCP menu
        ("MCP 管理", None, "M", "/mcp", None, None, "Connection", 20),
        ("工具列表", "MCP 管理", "C", "tools", "mcp/tools", "mcp:tools:list", "Tools", 1),
        ("资源列表", "MCP 管理", "C", "resources", "mcp/resources", "mcp:resources:list", "FolderOpened", 2),
        # AI module menu
        ("AI 助手", None, "M", "/ai", None, None, "ChatDotRound", 30),
        ("AI 对话", "AI 助手", "C", "chat", "ai/chat/index", "ai:chat", "ChatLineRound", 1),
        ("模型密钥管理", "AI 助手", "C", "providers", "ai/providers/index", "ai:provider:list", "Key", 2),
        ("新增模型密钥", "模型密钥管理", "F", None, None, "ai:provider:add", None, 1),
        ("编辑模型密钥", "模型密钥管理", "F", None, None, "ai:provider:edit", None, 2),
        ("删除模型密钥", "模型密钥管理", "F", None, None, "ai:provider:delete", None, 3),
    ]

    # Track created menus by name for parent linking
    name_to_menu: dict[str, Menu] = {}

    for name, parent_name, mtype, path, component, permission, icon, sort in menus_data:
        parent_id = name_to_menu[parent_name].id if parent_name and parent_name in name_to_menu else 0
        menu = Menu(
            name=name,
            parent_id=parent_id,
            type=mtype,
            path=path,
            component=component,
            permission=permission,
            icon=icon,
            sort=sort,
            visible=1,
            status=1,
        )
        db.add(menu)
        await db.flush()  # Get the ID
        name_to_menu[name] = menu

    logger.info(f"Created {len(menus_data)} menu items")


async def _seed_missing_menus(db: AsyncSession) -> None:
    """Idempotently add menus that were introduced after the initial seed.

    Handles upgrades of existing installs: checks by name + parent, only inserts missing rows.
    """
    existing = await db.execute(select(Menu))
    existing_menus = list(existing.scalars().all())

    def find(name: str, parent_name: str | None = None) -> Menu | None:
        """Find a menu by name (optionally scoped to a parent's name).

        Parent lookup is name-based across any tree level (not restricted to
        top-level menus), so sub-menus like '工具列表' or 'AI 对话' can be
        used as parents for button-level (F) permission entries.
        """
        if parent_name is None:
            return next((m for m in existing_menus if m.name == name and m.parent_id == 0), None)
        parent = next((m for m in existing_menus if m.name == parent_name), None)
        if not parent:
            return None
        return next((m for m in existing_menus if m.name == name and m.parent_id == parent.id), None)

    # (name, parent_name, type, path, component, permission, icon, sort)
    missing_menus = [
        # MCP management additions
        ("提示词列表", "MCP 管理", "C", "prompts", "mcp/prompts", "mcp:prompts:list", "ChatLineSquare", 3),
        ("调用工具", "工具列表", "F", None, None, "mcp:tools:call", None, 1),
        ("调用日志", "MCP 管理", "C", "audit-logs", "mcp/audit-logs", "mcp:audit:list", "List", 4),
        # AI module button-level permissions
        ("调用AI对话", "AI 对话", "F", None, None, "ai:chat:call", None, 1),
    ]

    added = 0
    for name, parent_name, mtype, path, component, permission, icon, sort in missing_menus:
        # Determine parent (any level, not just top-level menus)
        parent_menu: Menu | None = None
        if parent_name:
            parent_menu = next((m for m in existing_menus if m.name == parent_name), None)
            if parent_menu is None:
                logger.warning(f"Skip menu '{name}': parent '{parent_name}' not found")
                continue

        pid = parent_menu.id if parent_menu else 0

        # Skip if already exists (by parent id)
        dup = any(m.name == name and m.parent_id == pid for m in existing_menus)
        if dup:
            continue

        menu = Menu(
            name=name,
            parent_id=pid,
            type=mtype,
            path=path,
            component=component,
            permission=permission,
            icon=icon,
            sort=sort,
            visible=1,
            status=1,
        )
        db.add(menu)
        await db.flush()
        existing_menus.append(menu)
        added += 1

    if added:
        logger.info(f"Added {added} missing menu items")


async def _seed_role(db: AsyncSession) -> None:
    """Create a default admin role with all menus."""
    result = await db.execute(select(Role).where(Role.code == "admin"))
    if result.scalars().first():
        return

    all_menus = await db.execute(select(Menu))
    menus = list(all_menus.scalars().all())

    role = Role(
        name="超级管理员",
        code="admin",
        data_scope=4,  # All data
        sort=1,
        status=1,
        remark="系统内置超级管理员角色",
    )
    role.menus = menus
    db.add(role)
    await db.flush()
    logger.info("Created role '超级管理员'")


async def _seed_super_admin(db: AsyncSession) -> None:
    """Create the super admin user."""
    result = await db.execute(select(User).where(User.username == settings.SUPER_ADMIN_USERNAME))
    if result.scalars().first():
        return

    # Get dept
    dept_result = await db.execute(select(Dept).where(Dept.name == "ApeAdmin"))
    dept = dept_result.scalars().first()

    # Get admin role
    role_result = await db.execute(select(Role).where(Role.code == "admin"))
    role = role_result.scalars().first()

    user = User(
        username=settings.SUPER_ADMIN_USERNAME,
        nickname="超级管理员",
        password=hash_password(settings.SUPER_ADMIN_PASSWORD),
        email="admin@apeadmin.local",
        phone="",
        dept_id=dept.id if dept else None,
        status=1,
    )
    if role:
        user.roles = [role]

    db.add(user)
    await db.flush()
    logger.info(f"Created super admin user '{settings.SUPER_ADMIN_USERNAME}'")
