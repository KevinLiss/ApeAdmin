"""System file and folder models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin


class FileFolder(IDMixin, TimestampMixin, Base):
    __tablename__ = "sys_file_folder"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SystemFile(IDMixin, TimestampMixin, Base):
    __tablename__ = "sys_file"

    folder_id: Mapped[int] = mapped_column(ForeignKey("sys_file_folder.id"), default=0, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    extension: Mapped[str] = mapped_column(String(30), default="")
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, default=0)
    md5: Mapped[str] = mapped_column(String(32), default="", index=True)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

