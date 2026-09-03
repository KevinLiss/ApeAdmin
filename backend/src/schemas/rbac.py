"""Pydantic schemas (serializers / DTOs) for RBAC models."""

from datetime import datetime
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------

class PageResponse(BaseModel):
    """Generic paginated response envelope."""
    total: int = 0
    page: int = 1
    page_size: int = 20
    items: list[Any] = Field(default_factory=list)


# Allow arbitrary types for ORM
ORMConfig = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class LoginSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    captcha_id: str | None = Field(default=None, max_length=64)
    captcha_code: str | None = Field(default=None, max_length=8)
    # Login origin marker: "admin" (管理后台, default) or "site" (官网/前端门户).
    source: str | None = Field(default=None, max_length=20)


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    nickname: str = Field(default="", max_length=50)
    email: str | None = None
    phone: str | None = None
    dept_id: int | None = None
    status: int = 1


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role_ids: list[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    nickname: str | None = None
    email: str | None = None
    phone: str | None = None
    dept_id: int | None = None
    status: int | None = None
    role_ids: list[int] | None = None


class UserOut(UserBase):
    model_config = ORMConfig
    id: int
    avatar: str | None = None
    created_at: datetime
    roles: list["RoleOut"] = Field(default_factory=list)
    dept: "DeptOut | None" = None


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=50)
    data_scope: int = Field(default=1, ge=1, le=4)
    sort: int = 0
    status: int = 1
    remark: str | None = None


class RoleCreate(RoleBase):
    menu_ids: list[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    data_scope: int | None = Field(default=None, ge=1, le=4)
    sort: int | None = None
    status: int | None = None
    remark: str | None = None
    menu_ids: list[int] | None = None


class RoleOut(RoleBase):
    model_config = ORMConfig
    id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

class MenuBase(BaseModel):
    name: str = Field(..., max_length=50)
    parent_id: int = Field(default=0, ge=0)
    type: str = "M"
    path: str | None = None
    component: str | None = None
    permission: str | None = None
    icon: str | None = None
    sort: int = 0
    visible: int = 1
    status: int = 1


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = Field(default=None, ge=0)
    type: str | None = None
    path: str | None = None
    component: str | None = None
    permission: str | None = None
    icon: str | None = None
    sort: int | None = None
    visible: int | None = None
    status: int | None = None


class MenuOut(MenuBase):
    model_config = ORMConfig
    id: int
    children: list["MenuOut"] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Dept
# ---------------------------------------------------------------------------

class DeptBase(BaseModel):
    name: str = Field(..., max_length=100)
    parent_id: int = 0
    sort: int = 0
    leader: str | None = None
    phone: str | None = None
    status: int = 1


class DeptCreate(DeptBase):
    pass


class DeptUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    sort: int | None = None
    leader: str | None = None
    phone: str | None = None
    status: int | None = None


class DeptOut(DeptBase):
    model_config = ORMConfig
    id: int
    children: list["DeptOut"] = Field(default_factory=list)


# Forward references
UserOut.model_rebuild()
RoleOut.model_rebuild()
MenuOut.model_rebuild()
DeptOut.model_rebuild()
