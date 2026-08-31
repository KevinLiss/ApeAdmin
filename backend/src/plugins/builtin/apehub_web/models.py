"""ApeHub official website ORM models.

Tables (all prefixed ``apehub_web_``, linking back to ApeAdmin's ``sys_user``):

- apehub_web_profile          user extension (developer flag, balance, withdrawals)
- apehub_web_site_config      site configuration (logo/SEO/email/LemPay/entry)
- apehub_web_site_content     editable site content blocks (hero, features, footer)
- apehub_web_doc_category     documentation categories
- apehub_web_doc              technical documents (markdown body)
- apehub_web_plugin           plugin marketplace catalog
- apehub_web_plugin_file      plugin package / doc files
- apehub_web_plugin_demo      demo entries (H5 QR, mini-program QR, admin http link)
- apehub_web_order            purchase/payment orders
- apehub_web_income           revenue share records (developer/platform split)
- apehub_web_withdrawal       withdrawal requests
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, relationship

from src.db.engine import Base


class ApehubWebBase(DeclarativeBase):
    """Plugin-local mapper registry with ApeAdmin's shared table metadata.

    The shared metadata lets the plugin declare foreign keys to host tables.
    The separate registry makes a disable/re-enable import independent from
    earlier plugin mapper classes left alive by application sessions.
    """

    registry = registry(metadata=Base.metadata)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PluginStatus(str, enum.Enum):
    PENDING = "pending"          # 待审核
    APPROVED = "approved"        # 已通过（展示在官网）
    REJECTED = "rejected"        # 已驳回
    OFFLINE = "offline"          # 已下架


class OrderStatus(str, enum.Enum):
    PENDING = "pending"          # 待支付
    PAID = "paid"                # 已支付
    CANCELLED = "cancelled"      # 已取消
    REFUNDED = "refunded"        # 已退款


class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"          # 待审核
    APPROVED = "approved"        # 已通过（待打款）
    REJECTED = "rejected"        # 已驳回
    DONE = "done"                # 已完成


class PluginVersionStatus(str, enum.Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    ANALYSIS_FAILED = "analysis_failed"
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DemoType(str, enum.Enum):
    H5 = "h5"                    # H5 演示（二维码）
    MINIPROGRAM = "miniprogram"  # 小程序（二维码）
    ADMIN = "admin"              # 管理后台（http 链接）
    PC = "pc"
    API = "api"
    MCP = "mcp"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ApehubWebProfile(ApehubWebBase):
    """官网用户扩展（1:1 关联 ApeAdmin sys_user）。"""

    __tablename__ = "apehub_web_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(64), default="")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    is_developer: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    frozen_balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    total_income: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    total_withdrawn: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", name="uq_apehub_web_profile_user"),)


class ApehubWebSiteConfig(ApehubWebBase):
    """官网配置（单行）：站点名/Logo/SEO/邮箱/LemPay/入口。"""

    __tablename__ = "apehub_web_site_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_name: Mapped[str] = mapped_column(String(64), default="Apehub_web")
    site_logo: Mapped[str] = mapped_column(
        String(255), default="/apehub-web/assets/logo.png"
    )  # logo URL/路径
    site_icon: Mapped[str] = mapped_column(
        String(255), default="/apehub-web/assets/logo.png"
    )  # 浏览器图标 URL/路径
    site_domain: Mapped[str] = mapped_column(String(255), default="")    # 独立域名（可选）
    site_prefix: Mapped[str] = mapped_column(String(32), default="/apehub-web")  # 入口前缀
    seo_title: Mapped[str] = mapped_column(String(255), default="")
    seo_description: Mapped[str] = mapped_column(String(500), default="")
    seo_keywords: Mapped[str] = mapped_column(String(500), default="")
    # Email (SMTP)
    mail_user: Mapped[str] = mapped_column(String(255), default="")
    mail_code_enc: Mapped[str] = mapped_column("mail_code", Text, default="")
    mail_host: Mapped[str] = mapped_column(String(128), default="smtp.qq.com")
    mail_port: Mapped[int] = mapped_column(Integer, default=465)
    # LemPay
    lempay_pid: Mapped[int] = mapped_column(Integer, default=0)
    lempay_key_enc: Mapped[str] = mapped_column("lempay_key", Text, default="")
    lempay_api_url: Mapped[str] = mapped_column(String(255), default="")
    lempay_submit_url: Mapped[str] = mapped_column(String(255), default="")
    lempay_notify_url: Mapped[str] = mapped_column(String(255), default="")
    lempay_return_url: Mapped[str] = mapped_column(String(255), default="")
    lempay_payment_type: Mapped[str] = mapped_column(String(16), default="usdt")
    # AI code documentation provider (deepseek / qwen)
    ai_provider: Mapped[str] = mapped_column(String(16), default="deepseek")
    # DeepSeek code analysis
    deepseek_api_key_enc: Mapped[str] = mapped_column("deepseek_api_key", Text, default="")
    deepseek_base_url: Mapped[str] = mapped_column(String(255), default="https://api.deepseek.com")
    deepseek_model: Mapped[str] = mapped_column(String(64), default="deepseek-chat")
    # Qwen (DashScope OpenAI-compatible mode) code analysis
    qwen_api_key_enc: Mapped[str] = mapped_column("qwen_api_key", Text, default="")
    qwen_base_url: Mapped[str] = mapped_column(String(255), default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    qwen_model: Mapped[str] = mapped_column(String(64), default="qwen3.7-plus")
    # Plugin detail page layout/content configuration (JSON, fully configurable)
    plugin_detail_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Site default theme (light/dark), public site reads this as fallback
    theme_mode: Mapped[str] = mapped_column(String(16), default="light")
    # Service fee (platform cut, percent)
    service_fee_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("30"))
    currency: Mapped[str] = mapped_column(String(8), default="USDT")
    settlement_days: Mapped[int] = mapped_column(Integer, default=7)
    refund_days: Mapped[int] = mapped_column(Integer, default=7)
    min_withdrawal: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("100"))
    withdrawal_fee_type: Mapped[str] = mapped_column(String(16), default="fixed")
    withdrawal_fee_value: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApehubWebEmailVerification(ApehubWebBase):
    """One-time email verification state for public account registration."""

    __tablename__ = "apehub_web_email_verification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    purpose: Mapped[str] = mapped_column(String(32), default="register")
    code_hash: Mapped[str] = mapped_column(String(128))
    request_ip: Mapped[str] = mapped_column(String(64), default="")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("email", "purpose", name="uq_apehub_web_email_verification"),)


class ApehubWebNavigationItem(ApehubWebBase):
    """Configurable public website navigation item."""

    __tablename__ = "apehub_web_navigation_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    link: Mapped[str] = mapped_column(String(255))
    icon_url: Mapped[str] = mapped_column(String(255), default="")
    open_mode: Mapped[str] = mapped_column(String(16), default="same")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApehubWebSiteContent(ApehubWebBase):
    """官网内容区块（hero/features/footer 等，key-value 结构）。"""

    __tablename__ = "apehub_web_site_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    block_key: Mapped[str] = mapped_column(String(64), index=True)   # hero / features / footer ...
    title: Mapped[str] = mapped_column(String(255), default="")
    subtitle: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 扩展字段（CTA 链接等）
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("block_key", "sort", name="uq_apehub_web_content_block"),)


class ApehubWebDocCategory(ApehubWebBase):
    """文档分类。"""

    __tablename__ = "apehub_web_doc_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApehubWebDoc(ApehubWebBase):
    """技术文档。"""

    __tablename__ = "apehub_web_doc"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_doc_category.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    summary: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")          # Markdown
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    author: Mapped[str] = mapped_column(String(64), default="")
    published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped["ApehubWebDocCategory | None"] = relationship(lazy="selectin")


class ApehubWebPlugin(ApehubWebBase):
    """插件市场目录（官网展示 + 上架审核）。"""

    __tablename__ = "apehub_web_plugin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    developer_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(32), default="工具")   # 工具/电商/AI/仪表盘/系统增强
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    tags: Mapped[str] = mapped_column(String(255), default="")          # 逗号分隔
    icon: Mapped[str] = mapped_column(String(255), default="")
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    service_fee_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("30"))
    status: Mapped[PluginStatus] = mapped_column(Enum(PluginStatus), default=PluginStatus.PENDING, index=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    install_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_avg: Mapped[float] = mapped_column(Float, default=5.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    reject_reason: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    files: Mapped[list["ApehubWebPluginFile"]] = relationship(back_populates="plugin", cascade="all, delete-orphan", lazy="selectin")
    demos: Mapped[list["ApehubWebPluginDemo"]] = relationship(back_populates="plugin", cascade="all, delete-orphan", lazy="selectin")
    versions: Mapped[list["ApehubWebPluginVersion"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="ApehubWebPluginVersion.created_at.desc()"
    )
    media: Mapped[list["ApehubWebPluginMedia"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="ApehubWebPluginMedia.sort"
    )


class ApehubWebPluginFile(ApehubWebBase):
    """插件文件（代码包 / 文档文件）。"""

    __tablename__ = "apehub_web_plugin_file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    version_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_plugin_version.id"), nullable=True, index=True)
    file_type: Mapped[str] = mapped_column(String(16), default="package")  # package / doc / screenshot
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))   # 服务器存储路径
    size: Mapped[int] = mapped_column(Integer, default=0)
    md5: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plugin: Mapped["ApehubWebPlugin"] = relationship(back_populates="files")
    version: Mapped["ApehubWebPluginVersion | None"] = relationship(back_populates="files")


class ApehubWebPluginVersion(ApehubWebBase):
    """A reviewable and publishable release belonging to a marketplace plugin."""

    __tablename__ = "apehub_web_plugin_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[PluginVersionStatus] = mapped_column(
        Enum(PluginVersionStatus), default=PluginVersionStatus.DRAFT, index=True
    )
    compatibility: Mapped[str] = mapped_column(String(255), default="")
    changelog: Mapped[str] = mapped_column(Text, default="")
    documentation: Mapped[str] = mapped_column(Text, default="")
    analysis_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reject_reason: Mapped[str] = mapped_column(String(500), default="")
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("plugin_id", "version", name="uq_apehub_web_plugin_version"),
    )

    files: Mapped[list["ApehubWebPluginFile"]] = relationship(back_populates="version", lazy="selectin")


class ApehubWebPluginMedia(ApehubWebBase):
    """Plugin logo and ordered marketplace carousel images."""

    __tablename__ = "apehub_web_plugin_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    media_type: Mapped[str] = mapped_column(String(16), default="carousel")
    url: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApehubWebAnalysisJob(ApehubWebBase):
    """Durable DeepSeek analysis state for an uploaded plugin version."""

    __tablename__ = "apehub_web_analysis_job"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin_version.id"), index=True)
    status: Mapped[AnalysisStatus] = mapped_column(Enum(AnalysisStatus), default=AnalysisStatus.QUEUED, index=True)
    stage: Mapped[str] = mapped_column(String(64), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    model: Mapped[str] = mapped_column(String(64), default="")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ApehubWebPluginReview(ApehubWebBase):
    """Immutable review/publish audit history."""

    __tablename__ = "apehub_web_plugin_review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    version_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_plugin_version.id"), nullable=True, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    action: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(Text, default="")
    service_fee_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApehubWebPurchaseEntitlement(ApehubWebBase):
    """Permanent access to all published versions of a purchased plugin."""

    __tablename__ = "apehub_web_purchase_entitlement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_order.id"), nullable=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "plugin_id", name="uq_apehub_web_entitlement_user_plugin"),
    )


class ApehubWebPluginInstallation(ApehubWebBase):
    """One row per user and plugin, used for reliable installation statistics."""

    __tablename__ = "apehub_web_plugin_installation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    download_count: Mapped[int] = mapped_column(Integer, default=1)
    first_installed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("plugin_id", "user_id", name="uq_apehub_web_installation_user_plugin"),
    )


class ApehubWebPluginDemo(ApehubWebBase):
    """插件 demo 示例（H5 二维码 / 小程序二维码 / 管理后台链接）。"""

    __tablename__ = "apehub_web_plugin_demo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    demo_type: Mapped[DemoType] = mapped_column(Enum(DemoType))
    title: Mapped[str] = mapped_column(String(128), default="")
    url: Mapped[str] = mapped_column(String(500), default="")        # APP 类型为链接
    qr_image: Mapped[str] = mapped_column(String(255), default="")     # H5/小程序二维码图片
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plugin: Mapped["ApehubWebPlugin"] = relationship(back_populates="demos")


class ApehubWebOrder(ApehubWebBase):
    """购买订单。"""

    __tablename__ = "apehub_web_order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    service_fee: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    developer_income: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(8), default="USDT")
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    lepay_trade_no: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refund_reason: Mapped[str] = mapped_column(String(500), default="")


class ApehubWebIncome(ApehubWebBase):
    """收入分成记录。"""

    __tablename__ = "apehub_web_income"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_order.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)   # 开发者
    plugin_id: Mapped[int] = mapped_column(ForeignKey("apehub_web_plugin.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("30"))
    available_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApehubWebWithdrawal(ApehubWebBase):
    """提现申请。"""

    __tablename__ = "apehub_web_withdrawal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    net_amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    method: Mapped[str] = mapped_column(String(16), default="trc20")
    network: Mapped[str] = mapped_column(String(16), default="TRC20")
    account: Mapped[str] = mapped_column(String(255))
    status: Mapped[WithdrawalStatus] = mapped_column(Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING)
    remark: Mapped[str] = mapped_column(String(500), default="")
    tx_hash: Mapped[str] = mapped_column(String(128), default="")
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApehubWebWallet(ApehubWebBase):
    """Multiple USDT-TRC20 payout wallets per website user."""

    __tablename__ = "apehub_web_wallet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    network: Mapped[str] = mapped_column(String(16), default="TRC20")
    address: Mapped[str] = mapped_column(String(128))
    label: Mapped[str] = mapped_column(String(64), default="")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApehubWebPaymentEvent(ApehubWebBase):
    """Idempotent raw payment/refund callback record."""

    __tablename__ = "apehub_web_payment_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_order.id"), nullable=True, index=True)
    provider_event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(32), default="payment")
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ApehubWebLedgerEntry(ApehubWebBase):
    """Append-only USDT developer balance ledger."""

    __tablename__ = "apehub_web_ledger_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_order.id"), nullable=True, index=True)
    withdrawal_id: Mapped[int | None] = mapped_column(ForeignKey("apehub_web_withdrawal.id"), nullable=True, index=True)
    entry_type: Mapped[str] = mapped_column(String(32), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    status: Mapped[str] = mapped_column(String(16), default="available", index=True)
    available_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("order_id", "entry_type", name="uq_apehub_web_ledger_order_type"),
    )
