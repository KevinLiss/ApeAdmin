"""Seed initial data: super admin, default role, default menus.

Creates:
- 1 super admin user (admin / admin123)
- 1 default admin role with all menus
- Full menu tree matching the frontend routes (system:user, system:role, etc.)
"""

from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.crypto import encrypt_api_key
from src.core.security import hash_password
from src.db import SessionLocal
from src.models import Dept, Menu, Role, User
from src.models.rbac import role_menu
from src.models.ai import AiProvider


_REMOVED_COMPONENT_PREFIX = "apeui/components/pages/"


def _is_removed_component_menu(component: str | None) -> bool:
    """Identify legacy static component-demo menus retired from the product."""
    return bool(component and component.startswith(_REMOVED_COMPONENT_PREFIX))


async def seed_initial_data() -> None:
    """Seed the database with essential initial data if not already present."""
    async with SessionLocal() as db:
        await _seed_dept(db)
        await _seed_menus(db)
        await _seed_role(db)
        await _seed_developer_role(db)
        await _seed_super_admin(db)
        await _seed_ai_provider(db)
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
    await _retire_removed_component_menus(db)
    await _retire_style_library_menus(db)

    # Check if any menus exist
    result = await db.execute(select(Menu).limit(1))
    if result.scalars().first():
        # Incremental seeding: add any missing MCP/AI sub-menus on existing installs
        await _seed_missing_menus(db)
        return

    menus_data = [
        # (name, parent_key, type, path, component, permission, icon, sort)
        # Dashboard (top-level)
        ("系统仪表盘", None, "C", "/dashboard-monitor", "apeui/dashboard/Monitor", None, "Monitor", 1),
        # System management
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
        ("文件管理", "系统管理", "C", "file", "system/file/index", "system:file:list", "FolderOpened", 6),
        ("上传文件", "文件管理", "F", None, None, "system:file:upload", None, 1),
        ("新建文件夹", "文件管理", "F", None, None, "system:file:create-folder", None, 2),
        ("重命名文件", "文件管理", "F", None, None, "system:file:rename", None, 3),
        ("移动文件", "文件管理", "F", None, None, "system:file:move", None, 4),
        ("删除文件", "文件管理", "F", None, None, "system:file:delete", None, 5),
        ("下载文件", "文件管理", "F", None, None, "system:file:download", None, 6),
        ("导入插件", "插件管理", "F", None, None, "system:plugin:upload", None, 3),
        ("删除插件", "插件管理", "F", None, None, "system:plugin:delete", None, 4),
        ("重启后端", "插件管理", "F", None, None, "system:plugin:restart", None, 5),
        # System log
        ("系统日志", "系统管理", "C", "log", "system/log/index", "system:log:list", "Document", 6),
        ("删除日志", "系统日志", "F", None, None, "system:log:delete", None, 1),
        # MCP menu
        ("MCP 管理", None, "M", "/mcp", None, None, "Connection", 20),
        ("工具列表", "MCP 管理", "C", "tools", "mcp/tools", "mcp:tools:list", "Tools", 1),
        ("资源列表", "MCP 管理", "C", "resources", "mcp/resources", "mcp:resources:list", "FolderOpened", 2),
        # AI module menu
        ("AI 助手", None, "M", "/ai", None, None, "ChatDotRound", 30),
        ("AI 全能助手", "AI 助手", "C", "chat", "ai/chat/index", "ai:chat", "ChatLineRound", 1),
        ("模型密钥管理", "AI 助手", "C", "providers", "ai/providers/index", "ai:provider:list", "Key", 2),
        ("新增模型密钥", "模型密钥管理", "F", None, None, "ai:provider:add", None, 1),
        ("编辑模型密钥", "模型密钥管理", "F", None, None, "ai:provider:edit", None, 2),
        ("删除模型密钥", "模型密钥管理", "F", None, None, "ai:provider:delete", None, 3),
        # ApeHub management menus (also included in the first-run seed)
        ("ApeHub 管理", None, "M", "/apehub", None, None, "Shop", 40),
        ("官网配置", "ApeHub 管理", "C", "admin/config", "apehub/admin/config", "apehub:config", "Setting", 1),
        ("内容管理", "ApeHub 管理", "C", "admin/content", "apehub/admin/content", "apehub:content:list", "Document", 2),
        ("文档管理", "ApeHub 管理", "C", "admin/docs", "apehub/admin/docs", "apehub:docs:list", "Files", 3),
        ("插件审核", "ApeHub 管理", "C", "admin/plugins", "apehub/admin/plugins", "apehub:plugin:review", "Box", 4),
        ("提现审核", "ApeHub 管理", "C", "admin/withdrawals", "apehub/admin/withdrawals", "apehub:withdrawal:review", "Money", 5),
        ("用户列表", "ApeHub 管理", "C", "admin/users", "apehub/admin/users", "apehub:user:list", "User", 6),
        ("收入明细", "ApeHub 管理", "C", "admin/incomes", "apehub/admin/incomes", "apehub:income:list", "Tickets", 7),
        ("提交插件", "ApeHub 管理", "F", None, None, "apehub:plugin:submit", None, 8),
        ("订单列表", "ApeHub 管理", "F", None, None, "apehub:order:list", None, 9),
        ("申请提现", "ApeHub 管理", "F", None, None, "apehub:withdrawal:create", None, 10),
    ]

    # Track created menus by name for parent linking
    name_to_menu: dict[str, Menu] = {}

    menus_data = [
        item for item in menus_data
        if not _is_removed_component_menu(item[4])
        and item[0] != "Apeadmin 样式库"
        and item[1] != "Apeadmin 样式库"
    ]

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
        top-level menus), so sub-menus like '工具列表' or 'AI 全能助手' can be
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
        ("调用AI对话", "AI 全能助手", "F", None, None, "ai:chat:call", None, 1),
        # System log menu (incremental)
        ("系统日志", "系统管理", "C", "log", "system/log/index", "system:log:list", "Document", 6),
        ("删除日志", "系统日志", "F", None, None, "system:log:delete", None, 1),
        # Plugin management additions (incremental)
        ("导入插件", "插件管理", "F", None, None, "system:plugin:upload", None, 3),
        ("删除插件", "插件管理", "F", None, None, "system:plugin:delete", None, 4),
        ("重启后端", "插件管理", "F", None, None, "system:plugin:restart", None, 5),
        ("文件管理", "系统管理", "C", "file", "system/file/index", "system:file:list", "FolderOpened", 6),
        ("上传文件", "文件管理", "F", None, None, "system:file:upload", None, 1),
        ("新建文件夹", "文件管理", "F", None, None, "system:file:create-folder", None, 2),
        ("重命名文件", "文件管理", "F", None, None, "system:file:rename", None, 3),
        ("移动文件", "文件管理", "F", None, None, "system:file:move", None, 4),
        ("删除文件", "文件管理", "F", None, None, "system:file:delete", None, 5),
        ("下载文件", "文件管理", "F", None, None, "system:file:download", None, 6),
        # ApeHub plugin-owned management menus and developer actions
        ("ApeHub 管理", None, "M", "/apehub", None, None, "Shop", 40),
        ("官网配置", "ApeHub 管理", "C", "admin/config", "apehub/admin/config", "apehub:config", "Setting", 1),
        ("内容管理", "ApeHub 管理", "C", "admin/content", "apehub/admin/content", "apehub:content:list", "Document", 2),
        ("文档管理", "ApeHub 管理", "C", "admin/docs", "apehub/admin/docs", "apehub:docs:list", "Files", 3),
        ("插件审核", "ApeHub 管理", "C", "admin/plugins", "apehub/admin/plugins", "apehub:plugin:review", "Box", 4),
        ("提现审核", "ApeHub 管理", "C", "admin/withdrawals", "apehub/admin/withdrawals", "apehub:withdrawal:review", "Money", 5),
        ("用户列表", "ApeHub 管理", "C", "admin/users", "apehub/admin/users", "apehub:user:list", "User", 6),
        ("收入明细", "ApeHub 管理", "C", "admin/incomes", "apehub/admin/incomes", "apehub:income:list", "Tickets", 7),
        ("提交插件", "ApeHub 管理", "F", None, None, "apehub:plugin:submit", None, 8),
        ("订单列表", "ApeHub 管理", "F", None, None, "apehub:order:list", None, 9),
        ("申请提现", "ApeHub 管理", "F", None, None, "apehub:withdrawal:create", None, 10),
    ]

    missing_menus = [
        item for item in missing_menus
        if not _is_removed_component_menu(item[4])
        and item[0] != "Apeadmin 样式库"
        and item[1] != "Apeadmin 样式库"
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
        # Bind new menus to the admin role so they are accessible
        from sqlalchemy import select as sa_select
        admin_role = await db.execute(sa_select(Role).where(Role.code == "admin"))
        role = admin_role.scalars().first()
        if role:
            # Get all menu IDs currently bound to the role
            bound_ids = {m.id for m in role.menus}
            # Add any new menus that aren't bound yet
            new_menus = [m for m in existing_menus if m.id not in bound_ids]
            if new_menus:
                role.menus = list(role.menus) + new_menus
                await db.flush()
                logger.info(f"Bound {len(new_menus)} new menus to admin role")


async def _retire_removed_component_menus(db: AsyncSession) -> None:
    """Hide legacy component-demo menus on existing installations."""
    result = await db.execute(
        update(Menu)
        .where(Menu.component.like(f"{_REMOVED_COMPONENT_PREFIX}%"))
        .where((Menu.status != 0) | (Menu.visible != 0))
        .values(status=0, visible=0)
    )
    if result.rowcount:
        logger.info(f"Retired {result.rowcount} legacy component-demo menus")


async def _retire_style_library_menus(db: AsyncSession) -> None:
    """Hide the obsolete Apeadmin style-library directory and descendants."""
    result = await db.execute(select(Menu).where(Menu.name == "Apeadmin 样式库", Menu.parent_id == 0))
    roots = list(result.scalars().all())
    if not roots:
        return
    all_menus = list((await db.execute(select(Menu))).scalars().all())
    descendants = {menu.id for menu in roots}
    changed = True
    while changed:
        changed = False
        for menu in all_menus:
            if menu.parent_id in descendants and menu.id not in descendants:
                descendants.add(menu.id)
                changed = True
    retired = 0
    for menu in all_menus:
        if menu.id in descendants and (menu.status != 0 or menu.visible != 0):
            menu.status = 0
            menu.visible = 0
            retired += 1
    if retired:
        logger.info(f"Retired {retired} Apeadmin style-library menus")


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


async def _seed_developer_role(db: AsyncSession) -> None:
    """Create or update the least-privilege ApeHub developer role."""
    result = await db.execute(select(Role).where(Role.code == "developer"))
    role = result.scalars().first()
    if role is None:
        role = Role(
            name="开发者",
            code="developer",
            data_scope=1,
            sort=2,
            status=1,
            remark="ApeHub 插件开发者角色",
        )
        db.add(role)
        await db.flush()

    menus_result = await db.execute(
        select(Menu).where(Menu.permission.like("apehub:%"), Menu.status == 1)
    )
    apehub_menus = list(menus_result.scalars().all())
    bound_result = await db.execute(select(role_menu.c.menu_id).where(role_menu.c.role_id == role.id))
    bound_ids = set(bound_result.scalars().all())
    missing = [menu for menu in apehub_menus if menu.id not in bound_ids]
    if missing:
        await db.execute(insert(role_menu), [{"role_id": role.id, "menu_id": menu.id} for menu in missing])
        await db.flush()
    logger.info(f"Developer role ready ({len(apehub_menus)} ApeHub permissions)")


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


async def _seed_ai_provider(db: AsyncSession) -> None:
    """Seed a default DeepSeek provider so the user just needs to fill in the API Key."""
    result = await db.execute(select(AiProvider).where(AiProvider.name == "DeepSeek-V4Pro"))
    if result.scalars().first():
        return

    import json

    provider = AiProvider(
        name="DeepSeek-V4Pro",
        provider_type="deepseek",
        api_key_enc=encrypt_api_key("sk-placeholder"),
        base_url="https://api.deepseek.com",
        models=json.dumps(["deepseek-chat", "deepseek-reasoner"], ensure_ascii=False),
        enabled=1,
        sort=1,
        remark="默认供应商，请编辑后填入真实 API Key",
    )
    db.add(provider)
    await db.flush()
    logger.info("Created default AI provider 'DeepSeek-V4Pro'")
