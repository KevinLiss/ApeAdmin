"""CRUD operations for RBAC models."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.security import hash_password, verify_password
from src.crud.base import CRUDBase
from src.models import Dept, Menu, Role, User


class CRUDUser(CRUDBase[User]):
    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Find user by username (bypass soft-delete to allow login check)."""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> User | None:
        """Verify username + password and return user if valid."""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if user.status != 1:
            return None
        return user

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> User:
        """Create a new user, hashing the password."""
        if "password" in obj_in:
            obj_in = {**obj_in, "password": hash_password(obj_in["password"])}
        return await super().create(db, obj_in)

    async def update_password(self, db: AsyncSession, user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        from sqlalchemy import update
        stmt = update(User).where(User.id == user_id).values(password=hash_password(new_password))
        await db.execute(stmt)
        await db.commit()
        return True

    async def assign_roles(self, db: AsyncSession, user_id: int, role_ids: list[int]) -> bool:
        """Assign roles to a user."""
        user = await self.get(db, user_id)
        if not user:
            return False
        roles = await db.execute(select(Role).where(Role.id.in_(role_ids)))
        user.roles = list(roles.scalars().all())
        await db.commit()
        return True


class CRUDRole(CRUDBase[Role]):
    async def get_by_code(self, db: AsyncSession, code: str) -> Role | None:
        """Find role by code."""
        result = await db.execute(select(Role).where(Role.code == code))
        return result.scalar_one_or_none()

    async def assign_menus(self, db: AsyncSession, role_id: int, menu_ids: list[int]) -> bool:
        """Assign menu permissions to a role."""
        role = await self.get(db, role_id)
        if not role:
            return False
        menus = await db.execute(select(Menu).where(Menu.id.in_(menu_ids)))
        role.menus = list(menus.scalars().all())
        await db.commit()
        return True


class CRUDMenu(CRUDBase[Menu]):
    async def get_tree(self, db: AsyncSession) -> list[Menu]:
        """Get all menus as a flat list (excludes soft-deleted, build tree on the caller side)."""
        stmt = select(Menu).order_by(Menu.sort, Menu.id)
        if hasattr(Menu, "deleted_at"):
            stmt = stmt.where(Menu.deleted_at.is_(None))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, id: int, obj_in: dict[str, Any]) -> Menu | None:
        """Update a menu while preserving explicit nulls for nullable columns."""
        if not obj_in:
            return await self.get(db, id)
        from sqlalchemy import update
        await db.execute(update(Menu).where(Menu.id == id).values(**obj_in))
        await db.commit()
        return await self.get(db, id)


class CRUDDept(CRUDBase[Dept]):
    async def get_tree(self, db: AsyncSession) -> list[Dept]:
        """Get all departments as a flat list (excludes soft-deleted)."""
        stmt = select(Dept).order_by(Dept.sort, Dept.id)
        if hasattr(Dept, "deleted_at"):
            stmt = stmt.where(Dept.deleted_at.is_(None))
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Singletons
crud_user = CRUDUser(User)
crud_role = CRUDRole(Role)
crud_menu = CRUDMenu(Menu)
crud_dept = CRUDDept(Dept)
