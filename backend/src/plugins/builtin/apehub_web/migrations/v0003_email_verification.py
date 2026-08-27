"""Persist one-time registration email verification state."""

from sqlalchemy.ext.asyncio import AsyncConnection

from src.plugins.builtin.apehub_web.models import ApehubWebEmailVerification


async def add_email_verification_schema(connection: AsyncConnection) -> None:
    """Create the verification table without altering host or legacy tables."""
    await connection.run_sync(
        lambda sync_connection: ApehubWebEmailVerification.__table__.create(
            sync_connection, checkfirst=True
        )
    )
