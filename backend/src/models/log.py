"""System operation log model."""

from datetime import datetime
from typing import Any

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin


class SysLog(IDMixin, Base):
    """Operation log entry — one row per API request."""

    __tablename__ = "sys_log"

    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    method: Mapped[str] = mapped_column(String(10))          # GET / POST / PUT / DELETE
    path: Mapped[str] = mapped_column(String(500))           # request path
    params: Mapped[str | None] = mapped_column(Text, nullable=True)   # query/body summary
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)     # response time
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default="CURRENT_TIMESTAMP",
    )
