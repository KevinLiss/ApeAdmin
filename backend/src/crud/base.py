"""Generic async CRUD base class.

Provides common create/read/update/delete operations that work with any
SQLAlchemy 2.0 model. Subclass this and pass the model class to __init_subclass__
or simply instantiate with a model.

Inspired by FastAdmin's CRUD traits pattern.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import delete as sa_delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Base

ModelT = TypeVar("ModelT", bound=Base)


class CRUDBase(Generic[ModelT]):
    """Generic CRUD operations for a given SQLAlchemy model."""

    def __init__(self, model: type[ModelT]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelT | None:
        """Get a single record by ID (excludes soft-deleted records)."""
        stmt = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: list | None = None,
        order_by: Any = None,
    ) -> tuple[list[ModelT], int]:
        """Get paginated list with optional filters and total count."""
        stmt = select(self.model)

        # Apply soft-delete filter if model supports it
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        # Apply filters
        if filters:
            for f in filters:
                stmt = stmt.where(f)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Order
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.id.desc())

        # Paginate
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelT:
        """Create a new record from a dict."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, id: int, obj_in: dict[str, Any]) -> ModelT | None:
        """Update a record by ID with a dict of fields."""
        # Filter out None values to avoid overwriting with null
        update_data = {k: v for k, v in obj_in.items() if v is not None}
        if not update_data:
            return await self.get(db, id)

        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        return await self.get(db, id)

    async def delete(self, db: AsyncSession, id: int, soft: bool = True) -> bool:
        """Delete a record. If soft=True and model supports soft-delete, set deleted_at."""
        if soft and hasattr(self.model, "deleted_at"):
            from datetime import datetime, timezone

            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(deleted_at=datetime.now(timezone.utc))
            )
            await db.execute(stmt)
            await db.commit()
        else:
            stmt = sa_delete(self.model).where(self.model.id == id)
            await db.execute(stmt)
            await db.commit()
        return True

    async def exists(self, db: AsyncSession, **kwargs: Any) -> bool:
        """Check if a record matching the given field values exists."""
        stmt = select(func.count()).select_from(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        result = await db.execute(stmt)
        return (result.scalar() or 0) > 0
