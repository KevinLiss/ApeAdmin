"""CRUD for system settings."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.setting import Setting


class CRUDSetting(CRUDBase[Setting]):
    """CRUD for sys_setting table."""

    async def get_by_key(self, db: AsyncSession, key: str) -> Setting | None:
        """Get a setting by its unique key."""
        stmt = select(Setting).where(Setting.key == key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_value(self, db: AsyncSession, key: str, default: str = "") -> str:
        """Get a setting value by key, return default if not found."""
        setting = await self.get_by_key(db, key)
        return setting.value if setting else default

    async def get_all_public(self, db: AsyncSession) -> dict[str, str]:
        """Get all public settings as a dict."""
        stmt = select(Setting).where(Setting.is_public == True)  # noqa: E712
        result = await db.execute(stmt)
        return {s.key: s.value for s in result.scalars().all()}

    async def get_all_by_category(self, db: AsyncSession, category: str) -> list[Setting]:
        """Get all settings in a category."""
        stmt = select(Setting).where(Setting.category == category).order_by(Setting.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, db: AsyncSession) -> list[Setting]:
        """Get all settings ordered by category then id."""
        stmt = select(Setting).order_by(Setting.category, Setting.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, db: AsyncSession, key: str, value: str, **extra: Any) -> Setting:
        """Insert or update a setting by key."""
        existing = await self.get_by_key(db, key)
        if existing:
            existing.value = value
            for k, v in extra.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            setting = Setting(key=key, value=value, **extra)
            db.add(setting)
            await db.commit()
            await db.refresh(setting)
            return setting

    async def set_many(self, db: AsyncSession, items: dict[str, str]) -> None:
        """Batch upsert settings by key."""
        for key, value in items.items():
            await self.upsert(db, key, value)
        await db.commit()


crud_setting = CRUDSetting(Setting)
