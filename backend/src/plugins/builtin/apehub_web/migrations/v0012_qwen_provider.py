"""Add AI provider selector and Qwen (DashScope) config columns to the site config table."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def upgrade_add_qwen_provider(connection: AsyncConnection) -> None:
    """Add ai_provider / qwen_* columns to apehub_web_site_config."""
    table = "apehub_web_site_config"

    def _column_names(sync_connection) -> set[str]:
        return {column["name"] for column in inspect(sync_connection).get_columns(table)}

    existing = await connection.run_sync(_column_names)
    additions = {
        "ai_provider": "VARCHAR(16) NOT NULL DEFAULT 'deepseek'",
        "qwen_api_key": "TEXT NOT NULL DEFAULT ''",
        "qwen_base_url": "VARCHAR(255) NOT NULL DEFAULT 'https://dashscope.aliyuncs.com/compatible-mode/v1'",
        "qwen_model": "VARCHAR(64) NOT NULL DEFAULT 'qwen3.7-plus'",
    }
    for column, definition in additions.items():
        if column not in existing:
            await connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))