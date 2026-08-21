"""CRUD for AI provider."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.ai import AiProvider


class CrudAiProvider(CRUDBase[AiProvider]):
    """CRUD for AI provider with encrypted API key support."""

    async def get_by_id(self, db: AsyncSession, id: int) -> AiProvider | None:
        return await self.get(db, id)

    async def list_enabled(self, db: AsyncSession) -> list[AiProvider]:
        """List all enabled providers sorted by sort."""
        stmt = (
            select(AiProvider)
            .where(AiProvider.enabled == 1)
            .order_by(AiProvider.sort, AiProvider.id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_first_enabled(self, db: AsyncSession) -> AiProvider | None:
        """Get the first enabled provider (for auto-selection)."""
        stmt = (
            select(AiProvider)
            .where(AiProvider.enabled == 1)
            .order_by(AiProvider.sort, AiProvider.id)
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


crud_ai_provider = CrudAiProvider(AiProvider)
