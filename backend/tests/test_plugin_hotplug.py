import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.seed import _remove_unimplemented_apeui_menus
from src.db import Base
from src.mcp import mcp_manager
from src.models import Menu, Role
from src.models.rbac import role_menu
from src.plugins.base import event_bus
from src.plugins.manager import PluginManager


@pytest.fixture(autouse=True)
def reset_global_resources():
    mcp_manager._tools.clear()
    event_bus._handlers.clear()
    yield
    mcp_manager._tools.clear()
    event_bus._handlers.clear()


@pytest.mark.asyncio
async def test_enable_disable_reenable_tracks_and_removes_resources():
    app = FastAPI()
    manager = PluginManager()
    manager._discover_one("login_captcha")

    enabled = await manager.enable_plugin("login_captcha", app)
    assert enabled["status"] == "active"
    assert enabled["routes_registered"] == 1

    disabled = await manager.disable_plugin("login_captcha", app)
    assert disabled["routes_removed"] == 1
    assert disabled["mcp_tools_removed"] == 0
    assert disabled["events_unsubscribed"] == 1

    enabled_again = await manager.enable_plugin("login_captcha", app)
    assert enabled_again["status"] == "active"
    assert enabled_again["routes_registered"] == 1
    await manager.disable_plugin("login_captcha", app)


def test_plugin_zip_rejects_unsafe_name_and_supports_single_root():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        valid_zip = root / "valid.zip"
        with zipfile.ZipFile(valid_zip, "w") as archive:
            archive.writestr("bundle/plugin.json", '{"name":"demo","display_name":"Demo","version":"1"}')
            archive.writestr("bundle/demo/__init__.py", "")

        manager = PluginManager()
        manager._builtin_dir = root / "builtin"
        manager.import_plugin(valid_zip)
        assert (root / "builtin" / "demo" / "__init__.py").exists()

        unsafe_zip = root / "unsafe.zip"
        with zipfile.ZipFile(unsafe_zip, "w") as archive:
            archive.writestr("plugin.json", '{"name":"../bad","display_name":"Bad","version":"1"}')
            archive.writestr("../outside.txt", "blocked")

        with pytest.raises(ValueError):
            manager._validate_plugin_zip(unsafe_zip)


@pytest.mark.asyncio
async def test_seed_removes_unimplemented_apeui_admin_menu_branch():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        async with session_factory() as db:
            root = Menu(name="ApeUI 官网", parent_id=0, type="M", path="/apeui")
            config = Menu(
                name="官网配置",
                parent_id=0,
                type="C",
                path="apeui/admin/config",
                component="apeui/admin/Config",
                permission="apeui:config",
            )
            dashboard = Menu(
                name="系统仪表盘",
                parent_id=0,
                type="C",
                path="/dashboard-monitor",
                component="apeui/dashboard/Monitor",
            )
            role = Role(name="超级管理员", code="admin")
            db.add_all([root, config, dashboard, role])
            await db.flush()
            config.parent_id = root.id
            await db.flush()
            await db.execute(
                insert(role_menu),
                [
                    {"role_id": role.id, "menu_id": root.id},
                    {"role_id": role.id, "menu_id": config.id},
                    {"role_id": role.id, "menu_id": dashboard.id},
                ],
            )
            await db.commit()

            await _remove_unimplemented_apeui_menus(db)
            await db.commit()

            remaining = list((await db.execute(select(Menu))).scalars().all())
            assert [menu.component for menu in remaining] == ["apeui/dashboard/Monitor"]
            role_menu_ids = set((await db.execute(select(role_menu.c.menu_id))).scalars().all())
            assert role_menu_ids == {dashboard.id}
    finally:
        await engine.dispose()
