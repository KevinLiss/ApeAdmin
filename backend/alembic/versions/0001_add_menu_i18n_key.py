"""Add i18n_key column to sys_menu for menu internationalization.

Revision ID: 0001
Revises:
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add i18n_key column to sys_menu table (idempotent).

    Installs upgraded before Alembic was adopted already carry the column
    (applied by the startup schema-patch whitelist in ``core/dbmigrate.py``),
    so check before altering — every migration here must be safe to run on
    any historical schema state.
    """
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "sys_menu" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("sys_menu")}
    if "i18n_key" in cols:
        return
    # SQLite/MySQL: use batch_alter_table for cross-dialect compatibility
    with op.batch_alter_table("sys_menu") as batch_op:
        batch_op.add_column(
            sa.Column("i18n_key", sa.String(100), nullable=True, comment="国际化键")
        )


def downgrade() -> None:
    """Remove i18n_key column from sys_menu table (idempotent)."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "sys_menu" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("sys_menu")}
    if "i18n_key" not in cols:
        return
    with op.batch_alter_table("sys_menu") as batch_op:
        batch_op.drop_column("i18n_key")
