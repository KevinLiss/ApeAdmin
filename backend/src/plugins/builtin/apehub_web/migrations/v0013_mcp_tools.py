"""Add mcp_tools JSON column to the plugin table for MCP tool declarations."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def upgrade_add_mcp_tools(connection: AsyncConnection) -> None:
    """Add mcp_tools column to apehub_web_plugin."""
    table = "apehub_web_plugin"

    def _column_names(sync_connection) -> set[str]:
        return {column["name"] for column in inspect(sync_connection).get_columns(table)}

    existing = await connection.run_sync(_column_names)
    if "mcp_tools" not in existing:
        await connection.execute(text(f"ALTER TABLE {table} ADD COLUMN mcp_tools JSON"))
