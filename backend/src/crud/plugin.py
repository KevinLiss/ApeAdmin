"""CRUD for plugin registry."""

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.plugin import Plugin


class CRUDPlugin(CRUDBase[Plugin]):
    """CRUD for sys_plugin table."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Plugin | None:
        """Get a plugin by its unique name."""
        stmt = select(Plugin).where(Plugin.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_enabled(self, db: AsyncSession) -> list[Plugin]:
        """Get all enabled plugins."""
        stmt = select(Plugin).where(Plugin.enabled.is_(True)).order_by(Plugin.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self, db: AsyncSession, name: str, data: dict[str, Any]
    ) -> Plugin:
        """Insert or update a plugin record by name.

        If the plugin exists, update mutable fields (display_name, description,
        version, author, module_path). The `enabled` and `config` fields are
        NOT overwritten so admin settings persist across restarts.
        """
        existing = await self.get_by_name(db, name)
        if existing:
            # Update metadata only, preserve enabled + config
            for key in ("display_name", "description", "version", "author", "module_path"):
                if key in data:
                    setattr(existing, key, data[key])
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # New plugin: default enabled=False
            db_obj = Plugin(name=name, **data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

    async def set_config(self, db: AsyncSession, plugin_id: int, config: dict[str, Any]) -> Plugin | None:
        """Update plugin config JSON."""
        import json as _json

        plugin = await self.get(db, plugin_id)
        if not plugin:
            return None
        plugin.config = _json.dumps(config, ensure_ascii=False)
        await db.commit()
        await db.refresh(plugin)
        return plugin


crud_plugin = CRUDPlugin(Plugin)
