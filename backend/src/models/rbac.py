"""RBAC domain models: User, Role, Dept (department), Menu, and association tables.

Design inspired by:
- FastAdmin (PHP): User-Role-Menu-Dept with data_scope
- FastApiAdmin: async SQLAlchemy models
- FBA: clean model separation with typed Mapped columns
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Column,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.models.mixins import IDMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Association tables (many-to-many)
# ---------------------------------------------------------------------------

# User <-> Role
user_role = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True),
)

# Role <-> Menu (permission mapping)
role_menu = Table(
    "sys_role_menu",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("sys_menu.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Department (tree structure)
# ---------------------------------------------------------------------------

class Dept(IDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "sys_dept"

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    parent_id: Mapped[int] = mapped_column(
        Integer, default=0, comment="父级ID, 0=顶级"
    )
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    leader: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="负责人")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="联系电话")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 0=禁用 1=启用")

    # Self-referential relationship removed; tree built in application layer
    # (parent_id=0 means root, no FK constraint for flexibility)

    def __repr__(self) -> str:
        return f"<Dept {self.name}>"


# ---------------------------------------------------------------------------
# Menu (tree structure - directories, menus, buttons)
# ---------------------------------------------------------------------------

class Menu(IDMixin, TimestampMixin, Base):
    __tablename__ = "sys_menu"

    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="菜单名称")
    parent_id: Mapped[int] = mapped_column(Integer, default=0, comment="父级ID, 0=顶级")
    type: Mapped[str] = mapped_column(
        String(20), default="M", comment="类型: M=目录 C=菜单 F=按钮"
    )
    path: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="路由地址")
    component: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="组件路径")
    permission: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="权限标识 e.g. system:user:add"
    )
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="图标")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    visible: Mapped[int] = mapped_column(Integer, default=1, comment="是否可见: 0=隐藏 1=显示")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 0=禁用 1=启用")

    # Self-referential relationship removed; tree built in application layer
    roles: Mapped[list["Role"]] = relationship(secondary=role_menu, back_populates="menus")

    def __repr__(self) -> str:
        return f"<Menu {self.name} ({self.type})>"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

class Role(IDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "sys_role"

    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色编码")
    data_scope: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="数据范围: 1=本人 2=本部门及以下 3=本部门 4=全部",
    )
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 0=禁用 1=启用")
    remark: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="备注")

    menus: Mapped[list["Menu"]] = relationship(
        secondary=role_menu, back_populates="roles", lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship(secondary=user_role, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role {self.name} ({self.code})>"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(IDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "sys_user"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, default="", comment="昵称")
    password: Mapped[str] = mapped_column(String(200), nullable=False, comment="密码hash")
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="头像URL")
    dept_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sys_dept.id"), nullable=True, comment="部门ID"
    )
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 0=禁用 1=启用")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="最后登录时间"
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="最后登录IP"
    )

    dept: Mapped[Optional["Dept"]] = relationship("Dept", lazy="selectin")
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_role, back_populates="users", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
