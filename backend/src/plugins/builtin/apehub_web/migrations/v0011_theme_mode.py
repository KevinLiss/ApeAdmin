"""Add theme_mode column to the site config table."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def upgrade_add_theme_mode(connection: AsyncConnection) -> None:
    """Add theme_mode (light/dark) to apehub_web_site_config."""
    table = "apehub_web_site_config"

    def _column_names(sync_connection) -> set[str]:
        return {column["name"] for column in inspect(sync_connection).get_columns(table)}

    existing = await connection.run_sync(_column_names)
    if "theme_mode" not in existing:
        await connection.execute(
            text(f"ALTER TABLE {table} ADD COLUMN theme_mode VARCHAR(16) NOT NULL DEFAULT 'light'")
        )