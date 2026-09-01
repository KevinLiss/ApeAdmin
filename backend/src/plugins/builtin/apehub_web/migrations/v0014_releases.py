"""Add apehub_web_release table for ApeAdmin base release downloads."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def upgrade_add_releases(connection: AsyncConnection) -> None:
    """Create the release table if it does not exist (idempotent)."""
    table = "apehub_web_release"

    def _has_table(sync_connection) -> bool:
        return inspect(sync_connection).has_table(table)

    exists = await connection.run_sync(_has_table)
    if exists:
        return
    await connection.execute(
        text(
            f"""
            CREATE TABLE {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(32) NOT NULL UNIQUE,
                title VARCHAR(128) NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                changelog TEXT NOT NULL DEFAULT '',
                file_name VARCHAR(255) NOT NULL DEFAULT '',
                file_size INTEGER NOT NULL DEFAULT 0,
                file_path VARCHAR(500) NOT NULL DEFAULT '',
                file_md5 VARCHAR(64) NOT NULL DEFAULT '',
                is_latest BOOLEAN NOT NULL DEFAULT 0,
                enabled BOOLEAN NOT NULL DEFAULT 1,
                download_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    await connection.execute(text(f"CREATE INDEX ix_{table}_version ON {table} (version)"))