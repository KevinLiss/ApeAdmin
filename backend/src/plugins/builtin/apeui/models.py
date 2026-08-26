"""ApeUI ORM models — 11 tables (apeui_ prefix, FK to sys_user)."""

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.engine import Base


# ─── 枚举 ───
class PluginStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    OFFLINE = "offline"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DONE = "done"


class DemoType(str, enum.Enum):
    H5 = "h5"
    PC = "pc"
    API = "api"
    MCP = "mcp"


# ─── 1. apeui_site_config（单行） ───
class ApeUiSiteConfig(Base):
    __tablename__ = "apeui_site_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_name: Mapped[str] = mapped_column(String(100), default="ApeAdmin")
    site_logo: Mapped[str] = mapped_column(String(255), default="")
    site_prefix: Mapped[str] = mapped_column(String(50), default="/apeui")
    seo_title: Mapped[str] = mapped_column(String(200), default="")
    seo_description: Mapped[str] = mapped_column(String(500), default="")
    seo_keywords: Mapped[str] = mapped_column(String(200), default="")
    smtp_host: Mapped[str] = mapped_column(String(100), default="smtp.qq.com")
    smtp_port: Mapped[int] = mapped_column(Integer, default=465)
    smtp_user: Mapped[str] = mapped_column(String(100), default="")
    smtp_pass: Mapped[str] = mapped_column(String(100), default="")
    lempay_pid: Mapped[str] = mapped_column(String(100), default="")
    lempay_key: Mapped[str] = mapped_column(String(200), default="")
    lempay_api: Mapped[str] = mapped_column(String(255), default="")
    service_fee_rate: Mapped[float] = mapped_column(Float, default=30.0)


# ─── 2. apeui_site_content（key-value） ───
class ApeUiSiteContent(Base):
    __tablename__ = "apeui_site_content"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    block_key: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(200), default="")
    subtitle: Mapped[str] = mapped_column(String(300), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)


# ─── 3. apeui_doc_category ───
class ApeUiDocCategory(Base):
    __tablename__ = "apeui_doc_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(200), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)


# ─── 4. apeui_doc ───
class ApeUiDoc(Base):
    __tablename__ = "apeui_doc"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("apeui_doc_category.id"))
    title: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    summary: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    published: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("ApeUiDocCategory", lazy="selectin")


# ─── 5. apeui_profile（1:1 → sys_user） ───
class ApeUiProfile(Base):
    __tablename__ = "apeui_profile"
    __table_args__ = (UniqueConstraint("user_id", name="uq_apeui_profile_user"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"))
    is_developer: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    frozen_balance: Mapped[float] = mapped_column(Float, default=0.0)
    total_income: Mapped[float] = mapped_column(Float, default=0.0)
    total_withdrawn: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─── 6. apeui_plugin ───
class ApeUiPlugin(Base):
    __tablename__ = "apeui_plugin"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    developer_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"))
    name: Mapped[str] = mapped_column(String(100), index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(50), default="dev")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    price: Mapped[float] = mapped_column(Float, default=0.0)
    service_fee_rate: Mapped[float] = mapped_column(Float, default=30.0)
    status: Mapped[PluginStatus] = mapped_column(Enum(PluginStatus), default=PluginStatus.PENDING, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(50), default="")
    tags: Mapped[str] = mapped_column(String(500), default="")
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_avg: Mapped[float] = mapped_column(Float, default=5.0)
    summary: Mapped[str] = mapped_column(String(500), default="")
    changelog: Mapped[str] = mapped_column(Text, default="")
    reject_reason: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    files = relationship("ApeUiPluginFile", back_populates="plugin", cascade="all, delete-orphan", lazy="selectin")
    demos = relationship("ApeUiPluginDemo", back_populates="plugin", cascade="all, delete-orphan", lazy="selectin")


# ─── 7. apeui_plugin_file ───
class ApeUiPluginFile(Base):
    __tablename__ = "apeui_plugin_file"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apeui_plugin.id"))
    file_type: Mapped[str] = mapped_column(String(20), default="package")
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    size: Mapped[int] = mapped_column(Integer, default=0)
    md5: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plugin = relationship("ApeUiPlugin", back_populates="files")


# ─── 8. apeui_plugin_demo ───
class ApeUiPluginDemo(Base):
    __tablename__ = "apeui_plugin_demo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apeui_plugin.id"))
    demo_type: Mapped[DemoType] = mapped_column(Enum(DemoType), default=DemoType.H5)
    title: Mapped[str] = mapped_column(String(200), default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    qr_image: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plugin = relationship("ApeUiPlugin", back_populates="demos")


# ─── 9. apeui_order ───
class ApeUiOrder(Base):
    __tablename__ = "apeui_order"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"))
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apeui_plugin.id"))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    service_fee: Mapped[float] = mapped_column(Float, default=0.0)
    developer_income: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    lepay_trade_no: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


# ─── 10. apeui_income ───
class ApeUiIncome(Base):
    __tablename__ = "apeui_income"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("apeui_order.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"))
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apeui_plugin.id"))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    rate: Mapped[float] = mapped_column(Float, default=30.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─── 11. apeui_withdrawal ───
class ApeUiWithdrawal(Base):
    __tablename__ = "apeui_withdrawal"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"))
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(20), default="alipay")
    account: Mapped[str] = mapped_column(String(200))
    real_name: Mapped[str] = mapped_column(String(50), default="")
    status: Mapped[WithdrawalStatus] = mapped_column(Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING)
    remark: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    handled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
