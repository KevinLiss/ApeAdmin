"""插件私有数据库模型。

.. important::
   - 模型继承 ``PluginBase``——由 ``make_plugin_base`` 生成的**插件专属
     MetaData**，与系统表（``src.db.Base``）完全隔离。
   - ``install()`` 时 ``PluginBase.metadata.create_all`` 建表（只建本插件表）。
   - ``uninstall()`` 时 ``PluginBase.metadata.drop_all`` 删表（只删本插件表）。
   - 表名仍建议以 ``{插件名}_`` 开头（可读性），但隔离机制已不再依赖此前缀。

本示例定义一张「备忘录」表，演示字段类型、时间戳混入、布尔字段。
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.plugins.base import make_plugin_base
from src.models.mixins import IDMixin, TimestampMixin

# 插件专属声明基类：独立 MetaData，装卸只影响本插件
PluginBase = make_plugin_base("dev_example")


class DevExampleNote(IDMixin, TimestampMixin, PluginBase):
    """插件开发示例——备忘录表。

    表名约定：``dev_example_notes``
    - ``dev_example`` 是插件名（下划线命名）
    - ``notes`` 是资源名（复数）
    """

    __tablename__ = "dev_example_notes"

    # 业务字段
    title: Mapped[str] = mapped_column(String(200), comment="标题")
    content: Mapped[str] = mapped_column(Text, default="", comment="内容")
    priority: Mapped[int] = mapped_column(Integer, default=0, comment="优先级 0=普通 1=重要 2=紧急")
    completed: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否完成")
    # 软删除标记（可选，演示用）
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")
