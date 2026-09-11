"""AI 会议助手插件——seed 数据（菜单 + 权限 + 绑定 admin 角色）。

在 ``install()`` 时调用，幂等。
"""
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Menu, Role
from src.models.rbac import role_menu


async def seed_aimeeting_data(db: AsyncSession) -> None:
    """Seed 菜单 + 权限 + 绑定 admin 角色（幂等）。"""
    # ── 1. 创建顶级目录菜单 ──────────────────────────
    result = await db.execute(
        select(Menu).where(Menu.path == "/aimeeting", Menu.parent_id == 0)
    )
    parent = result.scalars().first()

    if not parent:
        parent = Menu(
            name="AI 会议",
            parent_id=0,
            type="M",
            path="/aimeeting",
            component=None,
            permission=None,
            icon="Calendar",
            sort=40,
            visible=1,
            status=1,
        )
        db.add(parent)
        await db.flush()
        logger.info("[aimeeting] Created 'AI 会议' top-level menu")

    # ── 2. 子菜单 + 按钮权限 ──────────────────────────────────
    menu_specs = [
        ("数据面板", "AI 会议", "C", "dashboard", "aimeeting/dashboard/index", "aimeeting:meeting:list", "DataAnalysis", 0),
        ("会议管理", "AI 会议", "C", "list", "aimeeting/list/index", "aimeeting:meeting:list", "Calendar", 1),
        ("新增会议", "会议管理", "F", None, None, "aimeeting:meeting:create", None, 1),
        ("编辑会议", "会议管理", "F", None, None, "aimeeting:meeting:edit", None, 2),
        ("删除会议", "会议管理", "F", None, None, "aimeeting:meeting:delete", None, 3),
        ("会议记录管理", "会议管理", "F", None, None, "aimeeting:record:list", None, 4),
        ("新增会议记录", "会议管理", "F", None, None, "aimeeting:record:create", None, 5),
        ("编辑会议记录", "会议管理", "F", None, None, "aimeeting:record:edit", None, 6),
        ("删除会议记录", "会议管理", "F", None, None, "aimeeting:record:delete", None, 7),
        ("生成会议纪要", "会议管理", "F", None, None, "aimeeting:minutes:generate", None, 8),
        ("查看会议纪要", "会议管理", "F", None, None, "aimeeting:minutes:list", None, 9),
        ("运行环境", "AI 会议", "C", "env", "aimeeting/env/index", "aimeeting:meeting:list", "Monitor", 2),
    ]

    existing = list((await db.execute(select(Menu))).scalars().all())
    created_menus: list[Menu] = []

    for name, parent_name, mtype, path, component, permission, icon, sort in menu_specs:
        parent_menu = next((m for m in existing + created_menus if m.name == parent_name), None)
        if not parent_menu:
            logger.warning(f"[aimeeting] Skip menu '{name}': parent '{parent_name}' not found")
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

    if created_menus:
        logger.info(f"[aimeeting] Created {len(created_menus)} menus")

    # ── 3. 绑定到 admin 角色 ──────────────────────────────
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
            from sqlalchemy import insert

            await db.execute(insert(role_menu), new_bindings)
            await db.flush()
            logger.info(f"[aimeeting] Bound {len(new_bindings)} menus to admin role")