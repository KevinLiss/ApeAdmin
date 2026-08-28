"""Add configurable navigation, visual icon support, and installation metrics."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.plugins.builtin.apehub_web.models import (
    ApehubWebNavigationItem,
    ApehubWebPluginInstallation,
)


async def add_navigation_and_installation_schema(connection: AsyncConnection) -> None:
    """Upgrade only Apehub_web-owned tables, retaining all existing site data."""
    columns = await connection.run_sync(
        lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("apehub_web_site_config")}
    )
    if "site_icon" not in columns:
        await connection.execute(
            text(
                "ALTER TABLE apehub_web_site_config "
                "ADD COLUMN site_icon VARCHAR(255) NOT NULL DEFAULT '/apehub-web/assets/logo.png'"
            )
        )

    plugin_columns = await connection.run_sync(
        lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("apehub_web_plugin")}
    )
    if "install_count" not in plugin_columns:
        await connection.execute(
            text("ALTER TABLE apehub_web_plugin ADD COLUMN install_count INTEGER NOT NULL DEFAULT 0")
        )

    await connection.run_sync(
        lambda sync_connection: ApehubWebNavigationItem.__table__.create(sync_connection, checkfirst=True)
    )
    await connection.run_sync(
        lambda sync_connection: ApehubWebPluginInstallation.__table__.create(sync_connection, checkfirst=True)
    )
