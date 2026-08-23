"""MCP audit log model: records MCP tool calls / resource reads / prompt renders."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin


class McpAuditLog(IDMixin, Base):
    """One row per MCP primitive invocation (tool/resource/prompt)."""

    __tablename__ = "sys_mcp_audit_log"

    action_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="类型: tool/resource/prompt")
    target_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="工具名/资源URI/提示词名")
    arguments: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="调用参数(JSON字符串)")
    result_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="结果摘要")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success", comment="success/failed")
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="操作用户ID")
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="操作用户名")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="调用时间"
    )

    def __repr__(self) -> str:
        return f"<McpAuditLog {self.action_type}:{self.target_name} by {self.username}>"