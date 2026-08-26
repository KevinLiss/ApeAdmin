"""ApeUI official website plugin entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.plugins.base import PluginInterface


class ApeUiPlugin(PluginInterface):
    """ApeAdmin 官网门户插件 — 首页 / 插件市场 / 技术文档 / 个人中心 / 支付提现。"""

    name = "apeui"
    display_name = "ApeUI 官网"
    description = "ApeAdmin 官网门户插件 — 首页、插件市场、技术文档、个人中心、支付提现"
    version = "1.0.0"
    author = "ApeAdmin"

    async def install(self) -> None:
        """Create apeui_* tables and seed initial data."""
        from src.db.engine import Base, engine
        # Ensure the core user table is registered when this plugin is enabled
        # outside the normal application startup sequence.
        from src.models import User  # noqa: F401
        from src.plugins.builtin.apeui import models  # noqa: F401
        from src.plugins.builtin.apeui.seed import seed_apeui_data

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await seed_apeui_data()
        logger.info("ApeUiPlugin installed: tables created, seed data inserted")

    async def uninstall(self) -> None:
        """Drop all apeui_* tables (FK reverse order)."""
        from sqlalchemy import text
        from src.db.engine import engine

        tables = [
            "apeui_withdrawal",
            "apeui_income",
            "apeui_order",
            "apeui_plugin_demo",
            "apeui_plugin_file",
            "apeui_plugin",
            "apeui_doc",
            "apeui_doc_category",
            "apeui_site_content",
            "apeui_site_config",
            "apeui_profile",
        ]
        async with engine.begin() as conn:
            for tbl in tables:
                await conn.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
        logger.info("ApeUiPlugin uninstalled: tables dropped")

    def register(self, app: FastAPI) -> None:
        """Register API routes + static file serving."""
        from src.core.config import settings
        from src.plugins.builtin.apeui.api import router

        # API 路由 → /api/v1/apeui/*
        app.include_router(router, prefix=settings.API_PREFIX)

        # 静态文件 → /apeui/index.html, /apeui/plugins.html, ...
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            app.mount(
                "/apeui",
                StaticFiles(directory=static_dir, html=True),
                name="apeui_static",
            )
        logger.info("ApeUiPlugin routes registered under /api/v1/apeui, static at /apeui")

    def on_load(self) -> None:
        logger.info("ApeUiPlugin loaded into memory")

    def on_unload(self) -> None:
        logger.info("ApeUiPlugin unloaded")
