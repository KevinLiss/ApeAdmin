# Alembic configuration for database migrations.
# Uses the sync_database_url from settings.

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.core.config import settings
from src.db import Base
from src.models import *  # Import all models to register them with Base.metadata
from src.models import (  # noqa: F811
    Dept,
    Menu,
    Role,
    User,
    role_menu,
    user_role,
)

# Ensure all model tables are registered on metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to a file)."""
    url = settings.sync_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB and execute)."""
    config = {
        "sqlalchemy.url": settings.sync_database_url,
        "sqlalchemy.echo": "true" if settings.DB_ECHO else "false",
    }
    connectable = engine_from_config(
        config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# Alembic environment entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
