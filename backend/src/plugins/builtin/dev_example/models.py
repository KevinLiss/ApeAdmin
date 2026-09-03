"""插件私有数据库模型。

.. important::
   - 插件表名**必须**以 ``{插件名}_`` 开头（此处即 ``dev_example_``）。
   - 模型继承 ``Base``，与系统表共用同一个 SQLAlchemy MetaData。
   - ``install()`` 时 ``Base.metadata.create_all`` 会自动建表。
   - ``uninstall()`` 时用 ``Base.metadata.drop_all`` 删表，仅传插件的表。

本示例定义一张「备忘录」表，演示字段类型、时间戳混入、布尔字段。
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class DevExampleNote(IDMixin, TimestampMixin, Base):
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
