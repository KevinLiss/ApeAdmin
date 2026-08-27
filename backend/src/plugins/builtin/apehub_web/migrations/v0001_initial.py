"""Initial isolated schema for the Apehub_web plugin."""

from sqlalchemy import inspect, text

from src.db.engine import Base, engine

SCHEMA_VERSION = 5
VERSION_TABLE = "apehub_web_schema_version"


def _plugin_tables():
    """Return only tables owned by this plugin, never the host schema."""
    return [
        table
        for name, table in Base.metadata.tables.items()
        if name.startswith("apehub_web_") and name != VERSION_TABLE
    ]


async def apply_migrations() -> None:
    """Create, upgrade, and version the plugin schema without touching host tables."""
    async with engine.begin() as connection:
        await connection.execute(
            text(
                f"CREATE TABLE IF NOT EXISTS {VERSION_TABLE} "
                "(version INTEGER PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        result = await connection.execute(text(f"SELECT MAX(version) FROM {VERSION_TABLE}"))
        current = result.scalar_one_or_none() or 0
        if current > SCHEMA_VERSION:
            raise RuntimeError(
                f"Apehub_web schema version {current} is newer than supported version {SCHEMA_VERSION}"
            )
        await connection.run_sync(
            lambda sync_connection: Base.metadata.create_all(
                sync_connection, tables=_plugin_tables(), checkfirst=True
            )
        )
        if current < 1:
            await connection.execute(
                text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (:version)"),
                {"version": 1},
            )
            current = 1
        if current < 2:
            legacy_exists = await connection.run_sync(
                lambda sync_connection: inspect(sync_connection).has_table("apeui_site_config")
            )
            if legacy_exists:
                from .v0002_migrate_apeui import migrate_legacy_apeui_data

                await migrate_legacy_apeui_data(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (2)"))
            current = 2
        if current < 3:
            from .v0003_email_verification import add_email_verification_schema

            await add_email_verification_schema(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (3)"))
            current = 3
        if current < 4:
            from .v0004_default_assets import set_default_assets

            await set_default_assets(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (4)"))
            current = 4
        if current < 5:
            from .v0005_legacy_asset_path import replace_legacy_asset_path

            await replace_legacy_asset_path(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (5)"))
