"""Lightweight, idempotent schema patches for existing installs.

``init_db()`` runs ``create_all`` which only creates missing *tables*; it
never adds columns to existing ones. A deploy-package update that ships
new model columns would therefore crash every query touching those
columns on upgraded installs (e.g. ``Unknown column 'i18n_key' in
sys_menu`` after upgrading to 2.4.0, taking down login/menu APIs).

This module applies a curated list of additive DDL patches at startup.
Each patch inspects the live schema first, so running on every boot is
safe: fresh installs already have the column and are skipped, and the
check itself is a no-op when the table does not exist yet.

Rules for adding a patch here:
- Additive columns only (ADD COLUMN with a NULLable default-safe type).
- Never destructive; data migrations belong to Alembic, not here.
- Every entry must match the SQLAlchemy model exactly, so new installs
  (create_all) and patched installs converge on the same schema.
"""

import sqlite3  # noqa: F401  (documented below)

from loguru import logger
from sqlalchemy import inspect

from src.db.engine import engine

# (table, column, ALTER DDL) — additive columns only.
# DDL must be valid on both MySQL and SQLite (both support ADD COLUMN).
SCHEMA_PATCHES: list[tuple[str, str, str]] = [
    # 2.4.0: menu i18n keys for the zh-CN/en-US switch.
    ("sys_menu", "i18n_key", "ALTER TABLE sys_menu ADD COLUMN i18n_key VARCHAR(100) NULL"),
]


async def ensure_schema_patches() -> list[str]:
    """Apply missing additive columns; return applied ``table.column`` names."""
    applied: list[str] = []

    async with engine.begin() as conn:
        def _do(sync_conn) -> list[str]:
            insp = inspect(sync_conn)
            out: list[str] = []
            for table, column, ddl in SCHEMA_PATCHES:
                if not insp.has_table(table):
                    # Fresh install: create_all owns the table with the
                    # column already present.
                    continue
                cols = {c["name"] for c in insp.get_columns(table)}
                if column in cols:
                    continue
                sync_conn.exec_driver_sql(ddl)
                out.append(f"{table}.{column}")
            return out

        applied = await conn.run_sync(_do)

    if applied:
        logger.info(f"Schema patches applied: {applied}")
    return applied
