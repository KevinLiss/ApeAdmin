"""System settings model: key-value store for runtime-configurable settings."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin


class Setting(IDMixin, TimestampMixin, Base):
    """System-wide settings stored as key-value pairs.

    Public settings (is_public=True) are readable without auth (e.g. site_name,
    logo_url, primary_color) so the login page and layout can use them.
    Private settings (is_public=False) require admin auth (e.g. admin_path).
    """

    __tablename__ = "sys_setting"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="设置键名")
    value: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="设置值")
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="描述")
    is_public: Mapped[bool] = mapped_column(default=False, comment="是否公开(无需登录可读)")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general", comment="分类")

    def __repr__(self) -> str:
        return f"<Setting {self.key}={self.value[:30]}>"
