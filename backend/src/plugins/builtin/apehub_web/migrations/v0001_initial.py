"""Initial isolated schema for the Apehub_web plugin."""

from sqlalchemy import inspect, text

from src.db.engine import Base, engine

SCHEMA_VERSION = 13
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
    # Direct upgrades and tests may call this module without going through
    # plugin.install(), so ensure all plugin tables are registered first.
    from src.models import User as _User  # noqa: F401
    from src.plugins.builtin.apehub_web import models as _models  # noqa: F401

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
            current = 5
        if current < 6:
            from .v0006_navigation_and_installations import add_navigation_and_installation_schema

            await add_navigation_and_installation_schema(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (6)"))
            current = 6
        if current < 7:
            from .v0007_marketplace_foundation import add_marketplace_foundation

            await add_marketplace_foundation(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (7)"))
            current = 7
        if current < 8:
            from .v0008_docs_portal import activate_docs_portal

            await activate_docs_portal(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (8)"))
            current = 8
        if current < 9:
            from .v0009_plugin_detail_config import add_plugin_detail_config

            await add_plugin_detail_config(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (9)"))
            current = 9
        if current < 10:
            from .v0010_multi_wallet import upgrade_multi_wallet

            await upgrade_multi_wallet(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (10)"))
            current = 10
        if current < 11:
            from .v0011_theme_mode import upgrade_add_theme_mode

            await upgrade_add_theme_mode(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (11)"))
            current = 11
        if current < 12:
            from .v0012_qwen_provider import upgrade_add_qwen_provider

            await upgrade_add_qwen_provider(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (12)"))
            current = 12
        if current < 13:
            from .v0013_mcp_tools import upgrade_add_mcp_tools

            await upgrade_add_mcp_tools(connection)
            await connection.execute(text(f"INSERT INTO {VERSION_TABLE} (version) VALUES (13)"))
            current = 13
