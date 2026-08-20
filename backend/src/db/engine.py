"""Database engine, Base, and session management using SQLAlchemy 2.0 async."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


def _create_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine."""
    return create_async_engine(
        settings.database_url,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE if settings.DB_TYPE == "mysql" else 0,
        max_overflow=settings.DB_MAX_OVERFLOW if settings.DB_TYPE == "mysql" else 0,
        poolclass=None if settings.DB_TYPE == "mysql" else None,
    )


engine: AsyncEngine = _create_engine()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an async session and ensure cleanup."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager version for use outside of FastAPI dependency injection."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (for dev / first run). In production, use Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine connection pool on shutdown."""
    await engine.dispose()
