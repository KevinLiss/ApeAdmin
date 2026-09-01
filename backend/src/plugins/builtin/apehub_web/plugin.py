"""Apehub_web plugin entry point.

ApeHub is the official website for ApeAdmin, packaged as a plugin.
It provides:

- Public website: home/hero, tech docs, plugin marketplace, user profile
- Admin management: site content/config, docs management, plugin review,
  payment config, user management

The plugin reuses ApeAdmin's auth (sys_user) and plugin lifecycle.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.plugins import PluginInterface


class ApehubWebPlugin(PluginInterface):
    """Apehub_web official website plugin."""

    name = "apehub_web"
    display_name = "ApeHub 官网门户"
    description = "ApeAdmin 官网门户：产品介绍、插件市场、技术文档和个人中心，含开发者 Demo 管理"
    version = "1.7.0"
    author = "ApeAdmin"

    async def install(self) -> None:
        """Apply the plugin schema migration and idempotent seed data."""
        from src.models import User  # noqa: F401  register sys_user before FK resolution
        from src.plugins.builtin.apehub_web import models  # noqa: F401  register models
        from src.plugins.builtin.apehub_web.migrations import apply_migrations
        from src.plugins.builtin.apehub_web.seed import seed_apehub_web_data

        await apply_migrations()
        await seed_apehub_web_data()
        logger.info("Apehub_web installed: schema migrated and seed data ensured")

    async def uninstall(self) -> None:
        """Drop all apehub_web_* tables."""
        from sqlalchemy import text

        from src.db import engine

        tables = [
            "apehub_web_ledger_entry",
            "apehub_web_payment_event",
            "apehub_web_wallet",
            "apehub_web_purchase_entitlement",
            "apehub_web_plugin_review",
            "apehub_web_analysis_job",
            "apehub_web_plugin_media",
            "apehub_web_plugin_version",
            "apehub_web_withdrawal",
            "apehub_web_income",
            "apehub_web_order",
            "apehub_web_plugin_demo",
            "apehub_web_plugin_installation",
            "apehub_web_plugin_file",
            "apehub_web_plugin",
            "apehub_web_doc",
            "apehub_web_doc_category",
            "apehub_web_site_config",
            "apehub_web_site_content",
            "apehub_web_navigation_item",
            "apehub_web_profile",
            "apehub_web_release",
            "apehub_web_schema_version",
        ]
        async with engine.begin() as conn:
            for tbl in tables:
                await conn.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
        logger.info("Apehub_web uninstalled: plugin-owned tables dropped")

    def register(self, app: FastAPI) -> None:
        """Register the API and isolated static website surface."""
        from src.core.config import settings
        from src.plugins.builtin.apehub_web.api import router

        app.include_router(router, prefix=settings.API_PREFIX)
        static_dir = Path(__file__).parent / "static"
        upload_dir = Path(settings.PLUGINS_UPLOAD_DIR).parent / "apehub_web"
        upload_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/apehub-web/uploads",
            StaticFiles(directory=upload_dir),
            name="apehub_web_uploads",
        )
        if static_dir.exists():
            app.mount(
                "/apehub-web",
                StaticFiles(directory=static_dir, html=True),
                name="apehub_web_static",
            )
        logger.info("Apehub_web routes registered under /api/v1/apehub-web and /apehub-web")

    def register_mcp_tools(self) -> None:
        """Register apehub_web marketplace MCP tools for AI agents."""
        from src.plugins.builtin.apehub_web.mcp_tools import register_mcp_tools

        register_mcp_tools()
