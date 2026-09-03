"""插件入口类——ApeAdmin 插件开发完整示例。

.. sidebar:: 插件开发快速上手
   :title: 你需要做什么

   1. 复制本目录，改名为你的插件名（``snake_case``，如 ``my_plugin``）
   2. 修改 ``plugin.json`` 中的 ``name`` / ``display_name`` / ``version``
   3. 修改 ``plugin.py`` 中的类属性 ``name`` / ``display_name`` / ``version``
   4. 在 ``models.py`` 中定义数据库模型（表名以 ``{plugin_name}_`` 开头）
   5. 在 ``api.py`` 中定义路由（权限以 ``{plugin_name}:`` 开头）
   6. 在 ``seed.py`` 中注册菜单（``install()`` 时调用）
   7. 在 ``frontend/src/views/{plugin_name}/`` 下放置 Vue 页面
   8. 重启后端，在后台 → 插件管理中启用

.. important:: 生命周期方法
   =========== ========== ================================= ==============
   方法        类型       说明                              必须实现
   =========== ========== ================================= ==============
   install()  async      建表、seed 数据、注册菜单          是
   uninstall() async      删表、清理数据                    是
   register() sync       注册路由、挂载静态资源              是
   register_mcp_tools() sync 注册 MCP 工具（可选）              否
   unregister() sync       释放运行时资源（可选）              否
   on_load()  sync       内存加载回调（可选）                否
   on_unload() sync       内存卸载回调（可选）                否
   before_login() async  登录前置守卫（可选）                否
   =========== ========== ================================= ==============
"""
from typing import Any

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import inspect

from src.core.config import settings
from src.db import Base, SessionLocal
from src.plugins import Event, PluginInterface, event_bus
from src.plugins.builtin.dev_example.models import DevExampleNote  # noqa: F401 — register ORM metadata
from src.plugins.builtin.dev_example.seed import seed_dev_example_data


class DevExamplePlugin(PluginInterface):
    """插件开发示例——备忘录管理。

    演示了一个完整插件的全部要素：
    - 数据库模型（models.py）
    - RESTful API（api.py）
    - 菜单与权限注册（seed.py）
    - MCP 工具注册（mcp_tools.py）
    - 事件订阅（USER_LOGIN）
    """

    # ── 插件元数据（与 plugin.json 对应）──────────────
    name = "dev_example"
    display_name = "插件开发示例"
    description = "完整的插件开发示例——包含数据库模型、API 路由、菜单注册、事件订阅、MCP 工具"
    version = "1.0.0"
    author = "ApeAdmin"

    # ── 内存状态 ──────────────────────────────────────
    _login_count: int = 0

    # ── 生命周期：内存加载 ─────────────────────────────
    def on_load(self) -> None:
        """插件被加载到内存时调用（模块被 import）。

        适合初始化内存状态。此时尚未建表、尚未注册路由。
        """
        logger.info("[DevExample] loaded into memory")

    # ── 生命周期：安装（建表 + seed）──────────────────
    async def install(self) -> None:
        """插件被启用时调用。

        职责：
        1. 创建数据库表（显式 ``create_all`` 确保表存在）
        2. Seed 初始数据 + 注册菜单

        .. note::
           ``Base.metadata.create_all`` 只创建不存在的表，不会修改已有表结构。
           正常启动流程中 ``init_db()`` 已执行过 ``create_all``，
           但热启用插件时需确保表存在，所以这里显式再调一次。
        """
        from src.db import engine
        from src.models.mixins import IDMixin, TimestampMixin  # noqa: F401 — ensure mixins imported

        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn, tables=[DevExampleNote.__table__]
                )
            )

        async with SessionLocal() as db:
            await seed_dev_example_data(db)
            await db.commit()
        logger.info("[DevExample] installed — tables ready, menus seeded")

    # ── 生命周期：卸载（清理）────────────────────────
    async def uninstall(self) -> None:
        """插件被卸载时调用（keep_data=False 时）。

        职责：
        1. 删除插件表
        2. 清理菜单（可选——菜单联动机制会自动隐藏）

        .. warning::
           此操作**不可逆**，会删除所有插件数据。
           热禁用时默认 keep_data=True，不会调用此方法。
        """
        async with SessionLocal() as db:
            # 删除插件表
            from src.db import engine
            async with engine.begin() as conn:
                await conn.run_sync(
                    lambda sync_conn: Base.metadata.drop_all(
                        sync_conn, tables=[DevExampleNote.__table__]
                    )
                )

            # 清理菜单（可选：菜单联动机制会自动隐藏，但彻底清理更干净）
            from sqlalchemy import delete
            from src.models import Menu
            await db.execute(
                delete(Menu).where(Menu.permission.like("dev_example:%"))
            )
            await db.execute(
                delete(Menu).where(Menu.path == "/dev-example")
            )
            await db.commit()
        logger.info("[DevExample] uninstalled — tables dropped, menus removed")

    # ── 生命周期：注册路由 + 事件 ───────────────────────
    def register(self, app: FastAPI) -> None:
        """注册路由、静态资源、事件订阅。

        .. important::
           - 此方法在 ``install()`` 之后调用
           - 路由通过 ``app.include_router`` 挂载，前缀为 ``settings.API_PREFIX``
           - 事件订阅必须传 ``plugin_name=self.name``，卸载时自动清理
        """
        from src.plugins.builtin.dev_example.api import router

        app.include_router(router, prefix=settings.API_PREFIX)

        # 订阅 USER_LOGIN 事件——演示事件总线用法
        event_bus.on(
            Event.USER_LOGIN,
            self._on_user_login,
            plugin_name=self.name,
        )
        logger.info("[DevExample] registered — routes + event subscription")

    # ── 生命周期：注册 MCP 工具（可选）──────────────────
    def register_mcp_tools(self) -> None:
        """注册 MCP 工具，让 AI 助手能调用本插件的功能。

        .. note::
           - 在 ``register()`` 之后调用
           - 必须传 ``plugin_name``，卸载时自动清理
           - 工具函数签名会自动推断为 JSON Schema
        """
        from src.plugins.builtin.dev_example.mcp_tools import register_dev_example_mcp_tools

        register_dev_example_mcp_tools()

    # ── 生命周期：卸载运行时资源 ───────────────────────
    def unregister(self, app: FastAPI) -> None:
        """插件被禁用时调用，释放运行时资源。

        .. note::
           - 路由和 MCP 工具由插件管理器自动移除（通过资源跟踪机制）
           - 事件订阅也由 ``off_plugin`` 自动清理
           - 此方法用于插件自定义的清理逻辑
        """
        logger.info("[DevExample] unregistered — runtime resources released")

    # ── 生命周期：内存卸载 ─────────────────────────────
    def on_unload(self) -> None:
        """插件从内存中卸载时调用。

        适合清理内存状态。"""
        logger.info("[DevExample] unloaded from memory")

    # ── 事件处理函数 ──────────────────────────────────
    async def _on_user_login(self, *args, **kwargs) -> None:
        """USER_LOGIN 事件处理函数。

        演示如何订阅事件。事件处理函数可以是同步或异步。
        """
        user_id = kwargs.get("user_id", "unknown")
        self._login_count += 1
        logger.info(
            "[DevExample] observed user login: {} (total: {})",
            user_id,
            self._login_count,
        )

    # ── 可选：登录前置守卫 ─────────────────────────────
    async def before_login(self, payload: dict[str, Any]) -> None:
        """登录前置守卫（可选）。

        在核心凭据验证之前调用。可以抛异常阻止登录（如验证码校验）。
        payload 包含 ``username``、``password``、``source`` 等字段。
        """
        # 本示例不拦截登录，仅演示接口
        return None
