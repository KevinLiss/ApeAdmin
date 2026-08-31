"""MCP tool registration persistence model.

Allows MCP tool registrations to survive process restarts by storing
tool metadata in the database. On startup, persisted tools with a valid
``handler_module`` / ``handler_attr`` path are re-imported and re-registered.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin


class McpToolRegistration(IDMixin, Base):
    """A persisted MCP tool registration entry."""

    __tablename__ = "sys_mcp_tool"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, comment="工具名称")
    description: Mapped[str] = mapped_column(String(500), default="", comment="工具描述")
    plugin_name: Mapped[str] = mapped_column(String(64), default="", index=True, comment="所属插件")
    category: Mapped[str] = mapped_column(String(64), default="system", comment="分类")
    required_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="所需权限(JSON数组)")
    # For automatic re-registration on restart:
    # handler_module = "src.plugins.builtin.apehub_web.mcp_tools"
    # handler_attr = "register_mcp_tools" (callable that registers tools)
    handler_module: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="处理函数所在模块路径")
    handler_attr: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="处理函数/注册函数名")
    enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<McpToolRegistration {self.name} ({self.plugin_name})>"
