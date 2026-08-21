"""Plugin management model: stores discovered plugins and their enable/config state."""

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin


class Plugin(IDMixin, TimestampMixin, Base):
    """Plugin registry: one row per discovered plugin package."""

    __tablename__ = "sys_plugin"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="插件标识名")
    display_name: Mapped[str] = mapped_column(String(200), nullable=False, default="", comment="显示名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="插件描述")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0", comment="版本号")
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="", comment="作者")
    module_path: Mapped[str] = mapped_column(String(300), nullable=False, comment="Python 模块路径")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="是否启用")
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None, comment="插件配置(JSON字符串)")

    def __repr__(self) -> str:
        return f"<Plugin {self.name} v{self.version} enabled={self.enabled}>"
