"""Hermes 插件菜单与权限 seed——install() 时注册。

全面移植 hermes-agent 核心功能到 ApeAdmin，菜单覆盖：
- AI 对话（WS 流式聊天）
- 会话管理（列表/删除/导出/统计）
- 模型配置（切换/辅助模型/MoA）
- 配置管理（config 读写）
- 环境变量（env 管理）
- 文件管理（浏览/上传/编辑）
- 技能管理（启用/安装/卸载）
- MCP 服务器（添加/删除/测试）
- 日志查看（过滤/着色）
- 用量分析（统计/趋势）
- 定时任务（cron 管理）
- 系统管理（网关/更新/ops）
- Profiles（切换/创建）
"""

from loguru import logger
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Menu, Role
from src.models.rbac import role_menu


async def seed_hermes_menus(db: AsyncSession) -> None:
    """注册 hermes 全功能菜单 + 权限，并绑定 admin 角色。幂等。"""
    # ── 1. 顶级目录菜单 ──────────────────────────────
    result = await db.execute(
        select(Menu).where(Menu.path == "/hermes", Menu.parent_id == 0)
    )
    parent = result.scalars().first()

    if not parent:
        parent = Menu(
            name="Hermes AI 助手",
            parent_id=0,
            type="M",
            path="/hermes",
            component=None,
            permission=None,
            icon="Sparkles",
            sort=60,
            visible=1,
            status=1,
        )
        db.add(parent)
        await db.flush()
        logger.info("Created 'Hermes AI 助手' top-level menu")

    # ── 2. 子菜单 + 按钮权限 ──────────────────────────
    # (name, parent_name, type, path, component, permission, icon, sort)
    menu_specs = [
        # 页面菜单 (type=C)
        ("AI 对话", "Hermes AI 助手", "C", "chat", "hermes/chat/index", "hermes:chat", "Chat", 1),
        ("会话管理", "Hermes AI 助手", "C", "sessions", "hermes/sessions/index", "hermes:sessions:list", "MessageSquare", 2),
        ("模型配置", "Hermes AI 助手", "C", "models", "hermes/models/index", "hermes:models:view", "Setting", 3),
        ("配置管理", "Hermes AI 助手", "C", "config", "hermes/config/index", "hermes:config:view", "Tools", 4),
        ("环境变量", "Hermes AI 助手", "C", "env", "hermes/env/index", "hermes:env:view", "Coordinate", 5),
        ("文件管理", "Hermes AI 助手", "C", "files", "hermes/files/index", "hermes:files:view", "Folder", 6),
        ("技能管理", "Hermes AI 助手", "C", "skills", "hermes/skills/index", "hermes:skills:view", "MagicStick", 7),
        ("MCP 服务器", "Hermes AI 助手", "C", "mcp", "hermes/mcp/index", "hermes:mcp:view", "Connection", 8),
        ("日志查看", "Hermes AI 助手", "C", "logs", "hermes/logs/index", "hermes:logs:view", "Document", 9),
        ("用量分析", "Hermes AI 助手", "C", "analytics", "hermes/analytics/index", "hermes:analytics:view", "DataLine", 10),
        ("定时任务", "Hermes AI 助手", "C", "cron", "hermes/cron/index", "hermes:cron:view", "AlarmClock", 11),
        ("系统管理", "Hermes AI 助手", "C", "system", "hermes/system/index", "hermes:system:view", "Monitor", 12),
        ("Profiles", "Hermes AI 助手", "C", "profiles", "hermes/profiles/index", "hermes:profiles:view", "UserFilled", 13),
        ("插件中心", "Hermes AI 助手", "C", "plugins", "hermes/plugins/index", "hermes:plugins:view", "Present", 14),
        ("消息渠道", "Hermes AI 助手", "C", "channels", "hermes/channels/index", "hermes:channels:view", "ChatDotRound", 15),
        ("Webhooks", "Hermes AI 助手", "C", "webhooks", "hermes/webhooks/index", "hermes:webhooks:view", "Link", 16),
        ("设备配对", "Hermes AI 助手", "C", "pairing", "hermes/pairing/index", "hermes:pairing:view", "Lock", 17),
        ("新建 Profile", "Profiles", "C", "profile-builder", "hermes/profile-builder/index", "hermes:profiles:create", "Plus", 4),
        ("官方文档", "Hermes AI 助手", "C", "docs", "hermes/docs/index", "hermes:docs:view", "Reading", 18),

        # 按钮权限 (type=F)
        ("使用 AI 对话", "AI 对话", "F", None, None, "hermes:chat", None, 1),
        ("删除会话", "会话管理", "F", None, None, "hermes:sessions:delete", None, 2),
        ("导出会话", "会话管理", "F", None, None, "hermes:sessions:export", None, 3),
        ("切换模型", "模型配置", "F", None, None, "hermes:models:set", None, 2),
        ("保存配置", "配置管理", "F", None, None, "hermes:config:save", None, 2),
        ("管理环境变量", "环境变量", "F", None, None, "hermes:env:manage", None, 2),
        ("上传文件", "文件管理", "F", None, None, "hermes:files:upload", None, 2),
        ("删除文件", "文件管理", "F", None, None, "hermes:files:delete", None, 3),
        ("安装技能", "技能管理", "F", None, None, "hermes:skills:install", None, 2),
        ("卸载技能", "技能管理", "F", None, None, "hermes:skills:uninstall", None, 3),
        ("添加 MCP 服务器", "MCP 服务器", "F", None, None, "hermes:mcp:add", None, 2),
        ("删除 MCP 服务器", "MCP 服务器", "F", None, None, "hermes:mcp:delete", None, 3),
        ("管理定时任务", "定时任务", "F", None, None, "hermes:cron:manage", None, 2),
        ("重启网关", "系统管理", "F", None, None, "hermes:system:gateway", None, 2),
        ("系统更新", "系统管理", "F", None, None, "hermes:system:update", None, 3),
        ("切换 Profile", "Profiles", "F", None, None, "hermes:profiles:switch", None, 2),
        ("创建 Profile", "Profiles", "F", None, None, "hermes:profiles:create", None, 3),
        ("安装插件", "插件中心", "F", None, None, "hermes:plugins:install", None, 2),
        ("移除插件", "插件中心", "F", None, None, "hermes:plugins:remove", None, 3),
        ("配置渠道", "消息渠道", "F", None, None, "hermes:channels:manage", None, 2),
        ("管理 Webhooks", "Webhooks", "F", None, None, "hermes:webhooks:manage", None, 2),
        ("审批配对", "设备配对", "F", None, None, "hermes:pairing:approve", None, 2),
    ]

    existing = list((await db.execute(select(Menu))).scalars().all())
    created_menus: list[Menu] = []

    # 只在 hermes 菜单子树中查找父菜单，避免与系统同名菜单冲突
    hermes_menu_ids = {parent.id}
    for m in existing:
        # 收集所有 parent_id 链回溯到 hermes 顶级菜单的菜单
        p = m
        while p and p.id not in hermes_menu_ids and p.parent_id != 0:
            p = next((x for x in existing if x.id == p.parent_id), None)
        if p and p.id in hermes_menu_ids:
            hermes_menu_ids.add(m.id)

    for name, parent_name, mtype, path, component, permission, icon, sort in menu_specs:
        parent_menu = next((m for m in existing + created_menus if m.name == parent_name and m.id in hermes_menu_ids), None)
        if not parent_menu:
            logger.warning(f"Skip menu '{name}': parent '{parent_name}' not found")
            continue
        dup = any(m.name == name and m.parent_id == parent_menu.id for m in existing)
        if dup:
            continue
        menu = Menu(
            name=name,
            parent_id=parent_menu.id,
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
        existing.append(menu)
        created_menus.append(menu)
        # 新建菜单本身也属于 hermes 子树，允许作为后续 F 按钮的父菜单
        hermes_menu_ids.add(menu.id)

    if created_menus:
        logger.info(f"Created {len(created_menus)} hermes menus")

    # ── 3. 绑定到 admin 角色 ──────────────────────────
    admin_result = await db.execute(select(Role).where(Role.code == "admin"))
    admin_role = admin_result.scalars().first()
    if admin_role and created_menus:
        bound_ids = {m.id for m in admin_role.menus}
        new_bindings = [
            {"role_id": admin_role.id, "menu_id": menu.id}
            for menu in created_menus
            if menu.id not in bound_ids
        ]
        if new_bindings:
            await db.execute(insert(role_menu), new_bindings)
            await db.flush()
            logger.info(f"Bound {len(new_bindings)} hermes menus to admin role")
