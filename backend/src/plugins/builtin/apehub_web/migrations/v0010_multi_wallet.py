"""Multi-wallet support: drop unique constraint on user_id, add label/is_default."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def _column_names(connection: AsyncConnection, table: str) -> set[str]:
    return await connection.run_sync(
        lambda sync_connection: {
            column["name"] for column in inspect(sync_connection).get_columns(table)
        }
    )


async def _add_columns(
    connection: AsyncConnection,
    table: str,
    definitions: dict[str, str],
) -> None:
    existing = await _column_names(connection, table)
    for name, definition in definitions.items():
        if name not in existing:
            await connection.execute(
                text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
            )


async def upgrade_multi_wallet(connection: AsyncConnection) -> None:
    """Allow multiple wallets per user with optional labels and a default flag."""
    table = "apehub_web_wallet"

    # MySQL: drop the unique index on user_id and add new columns.
    if connection.dialect.name == "mysql":
        # Find and drop unique index on user_id
        indexes = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_indexes(table)
        )
        for idx in indexes:
            if idx.get("unique") and idx.get("column_names") == ["user_id"]:
                await connection.execute(text(f"ALTER TABLE {table} DROP INDEX {idx['name']}"))
                break
        await _add_columns(connection, table, {
            "label": "VARCHAR(64) NOT NULL DEFAULT ''",
            "is_default": "BOOLEAN NOT NULL DEFAULT 0",
        })
        return

    # SQLite: cannot drop unique constraint in-place, so rebuild the table.
    existing = await _column_names(connection, table)
    needs_rebuild = "label" not in existing

    if not needs_rebuild:
        # Columns already exist (e.g. fresh install via create_all) — nothing to do.
        return

    # Preserve existing wallet data, mark the first wallet per user as default.
    await connection.execute(text("CREATE TEMP TABLE _wallet_backup AS SELECT * FROM " + table))
    await connection.execute(text(f"DROP TABLE {table}"))
    # create_all will recreate the table with the new schema on next startup,
    # but since we're inside a migration we create it manually.
    await connection.execute(text(
        f"CREATE TABLE {table} ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER NOT NULL, "
        "network VARCHAR(16) DEFAULT 'TRC20', "
        "address VARCHAR(128) NOT NULL, "
        "label VARCHAR(64) DEFAULT '', "
        "is_default BOOLEAN DEFAULT 0, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "FOREIGN KEY(user_id) REFERENCES sys_user(id))"))
    # Migrate data: first wallet per user becomes default
    await connection.execute(text(
        "INSERT INTO " + table + " (id, user_id, network, address, label, is_default, created_at, updated_at) "
        "SELECT id, user_id, network, address, '', "
        "CASE WHEN id = (SELECT MIN(id) FROM _wallet_backup w2 WHERE w2.user_id = _wallet_backup.user_id) "
        "THEN 1 ELSE 0 END, created_at, updated_at FROM _wallet_backup"))
    await connection.execute(text("CREATE INDEX ix_apehub_web_wallet_user_id ON " + table + " (user_id)"))
    await connection.execute(text("DROP TABLE _wallet_backup"))
