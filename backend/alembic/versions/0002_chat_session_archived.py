"""Add archived column to chat_session for one-click archiving.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-24

Archived sessions stay queryable (messages/restore) but disappear from
the default session list in the AI chat sidebar.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add archived column to chat_session (idempotent, see 0001 notes)."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "chat_session" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("chat_session")}
    if "archived" in cols:
        return
    with op.batch_alter_table("chat_session") as batch_op:
        batch_op.add_column(
            sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.text("0"))
        )


def downgrade() -> None:
    """Drop archived column (idempotent)."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "chat_session" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("chat_session")}
    if "archived" not in cols:
        return
    with op.batch_alter_table("chat_session") as batch_op:
        batch_op.drop_column("archived")
