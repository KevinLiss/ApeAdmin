"""插件 seed 数据——在 ``install()`` 时调用。

.. important:: 菜单注册约定
   插件管理器通过以下规则自动识别插件拥有的菜单：
   - ``permission`` 以 ``{plugin_name}:`` 开头
   - ``component`` 等于 ``{plugin_name}`` 或以 ``{plugin_name}/`` 开头
   - ``path`` 等于 ``/{plugin_name}`` 或以 ``/{plugin_name}/`` 开头
   （下划线转连字符版本也会匹配）

   禁用插件时这些菜单 ``status = 0``（隐藏），启用时恢复 ``status = 1``。

.. note:: 菜单结构
   - ``M`` = 目录（含子菜单的容器）
   - ``C`` = 菜单（对应一个前端页面，有 ``component`` 和 ``path``）
   - ``F`` = 按钮/权限（无路由，仅用于权限控制）
"""
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Menu, Role
from src.models.rbac import role_menu


async def seed_dev_example_data(db: AsyncSession) -> None:
    """Seed 菜单 + 权限 + 绑定 admin 角色。

    幂等：重复调用不会创建重复菜单。
    """
    # ── 1. 创建顶级目录菜单 ──────────────────────────
    result = await db.execute(
        select(Menu).where(Menu.path == "/dev-example", Menu.parent_id == 0)
    )
    parent = result.scalars().first()

    if not parent:
        parent = Menu(
            name="插件示例",
            parent_id=0,
            type="M",
            path="/dev-example",
            component=None,
            permission=None,
            icon="Lightning",
            sort=50,
            visible=1,
            status=1,
        )
        db.add(parent)
        await db.flush()
        logger.info("Created '插件示例' top-level menu")

    # ── 2. 子菜单 + 按钮权限 ──────────────────────────
    # (name, parent, type, path, component, permission, icon, sort)
    menu_specs = [
        ("备忘录管理", "插件示例", "C", "notes", "dev_example/notes/index", "dev_example:notes:list", "Document", 1),
        ("新增备忘录", "备忘录管理", "F", None, None, "dev_example:notes:create", None, 1),
        ("编辑备忘录", "备忘录管理", "F", None, None, "dev_example:notes:edit", None, 2),
        ("删除备忘录", "备忘录管理", "F", None, None, "dev_example:notes:delete", None, 3),
    ]

    # 获取所有已存在菜单（用于幂等判断）
    existing = list((await db.execute(select(Menu))).scalars().all())

    created_menus: list[Menu] = []
    for name, parent_name, mtype, path, component, permission, icon, sort in menu_specs:
        # 查找父菜单
        parent_menu = next((m for m in existing + created_menus if m.name == parent_name), None)
        if not parent_menu:
            logger.warning(f"Skip menu '{name}': parent '{parent_name}' not found")
            continue

        # 幂等：检查是否已存在（按 name + parent_id）
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
        logger.info(f"Created {len(created_menus)} dev_example menus")

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
            from sqlalchemy import insert
            await db.execute(insert(role_menu), new_bindings)
            await db.flush()
            logger.info(f"Bound {len(new_bindings)} dev_example menus to admin role")

    # ── 4. Seed 示例数据 ──────────────────────────
    from src.plugins.builtin.dev_example.models import DevExampleNote

    existing_notes = await db.execute(select(DevExampleNote).limit(1))
    if not existing_notes.scalars().first():
        sample_notes = [
            DevExampleNote(title="欢迎使用插件开发示例", content="这是一条示例备忘录。你可以新增、编辑、删除备忘录。", priority=1, completed=False),
            DevExampleNote(title="阅读 plugin.py", content="plugin.py 是插件入口类，包含 install/uninstall/register 等生命周期方法。", priority=2, completed=False),
            DevExampleNote(title="阅读 api.py", content="api.py 定义了 RESTful 路由，演示了权限检查和数据库操作。", priority=0, completed=True),
        ]
        for note in sample_notes:
            db.add(note)
        await db.flush()
        logger.info("Seeded 3 sample notes")
