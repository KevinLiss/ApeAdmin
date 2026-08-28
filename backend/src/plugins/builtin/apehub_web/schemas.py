"""ApeHub Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.plugins.builtin.apehub_web.models import DemoType, OrderStatus, PluginStatus, WithdrawalStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Site config / content
# ---------------------------------------------------------------------------

class SiteConfigIn(BaseModel):
    site_name: str | None = None
    site_logo: str | None = None
    site_icon: str | None = None
    site_domain: str | None = None
    site_prefix: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: str | None = None
    mail_user: str | None = None
    mail_code: str | None = None
    mail_host: str | None = None
    mail_port: int | None = None
    lempay_pid: int | None = None
    lempay_key: str | None = None
    lempay_api_url: str | None = None
    lempay_submit_url: str | None = None
    lempay_notify_url: str | None = None
    lempay_return_url: str | None = None
    lempay_payment_type: str | None = Field(default=None, pattern="^usdt$")
    deepseek_api_key: str | None = None
    deepseek_base_url: str | None = None
    deepseek_model: str | None = None
    plugin_detail_config: dict[str, Any] | None = None
    service_fee_rate: Decimal | None = Field(default=None, ge=0, le=100)
    settlement_days: int | None = Field(default=None, ge=0, le=365)
    refund_days: int | None = Field(default=None, ge=0, le=365)
    min_withdrawal: Decimal | None = Field(default=None, ge=0)
    withdrawal_fee_type: str | None = Field(default=None, pattern="^(fixed|percent)$")
    withdrawal_fee_value: Decimal | None = Field(default=None, ge=0)


class SiteConfigOut(ORMModel):
    id: int
    site_name: str
    site_logo: str
    site_icon: str
    site_domain: str
    site_prefix: str
    seo_title: str
    seo_description: str
    seo_keywords: str
    mail_user: str
    mail_host: str
    mail_port: int
    lempay_pid: int
    lempay_api_url: str
    lempay_notify_url: str
    lempay_return_url: str
    lempay_payment_type: str
    deepseek_base_url: str
    deepseek_model: str
    service_fee_rate: Decimal
    settlement_days: int
    refund_days: int
    min_withdrawal: Decimal
    withdrawal_fee_type: str
    withdrawal_fee_value: Decimal
    currency: str
    mail_configured: bool
    lempay_configured: bool
    deepseek_configured: bool


class SiteContentIn(BaseModel):
    block_key: str
    title: str = ""
    subtitle: str = ""
    body: str = ""
    image: str = ""
    sort: int = 0
    enabled: bool = True
    extra: dict[str, Any] | None = None


class SiteContentOut(ORMModel):
    id: int
    block_key: str
    title: str
    subtitle: str
    body: str
    image: str
    sort: int
    enabled: bool
    extra: dict[str, Any] | None
    updated_at: datetime


class NavigationItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    link: str = Field(min_length=1, max_length=255)
    icon_url: str = Field(default="", max_length=255)
    open_mode: str = Field(default="same", pattern="^(same|new)$")
    enabled: bool = True
    sort: int = Field(default=0, ge=0, le=9999)


# ---------------------------------------------------------------------------
# Docs
# ---------------------------------------------------------------------------

class DocCategoryIn(BaseModel):
    name: str
    description: str = ""
    sort: int = 0


class DocCategoryOut(ORMModel):
    id: int
    name: str
    description: str
    sort: int


class DocIn(BaseModel):
    category_id: int | None = None
    title: str
    slug: str
    summary: str = ""
    body: str = ""
    version: str = "1.0.0"
    author: str = ""
    published: bool = True
    sort: int = 0


class DocOut(ORMModel):
    id: int
    category_id: int | None
    title: str
    slug: str
    summary: str
    body: str
    version: str
    author: str
    published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Plugin marketplace
# ---------------------------------------------------------------------------

class PluginDemoIn(BaseModel):
    demo_type: DemoType
    title: str = ""
    url: str = ""
    qr_image: str = ""


class PluginSubmitIn(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    display_name: str = Field(min_length=2, max_length=128)
    description: str = ""
    category: str = "工具"
    version: str = "1.0.0"
    tags: str = ""
    price: Decimal = Field(default=Decimal("0"), ge=0)
    icon: str = ""
    demos: list[PluginDemoIn] = []


class PluginReviewIn(BaseModel):
    action: str  # approve / reject
    reason: str = ""
    service_fee_rate: Decimal | None = Field(default=None, ge=0, le=100)


class PluginOut(ORMModel):
    id: int
    developer_id: int
    name: str
    display_name: str
    slug: str
    description: str
    category: str
    version: str
    tags: str
    icon: str
    price: Decimal
    service_fee_rate: Decimal
    status: str
    download_count: int
    rating_avg: float
    rating_count: int
    reject_reason: str
    created_at: datetime
    updated_at: datetime
    # 关联（detail 用）
    demos: list[Any] = []


# ---------------------------------------------------------------------------
# Order / Income / Withdrawal
# ---------------------------------------------------------------------------

class PurchaseIn(BaseModel):
    plugin_id: int


class RefundIn(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class OrderOut(ORMModel):
    id: int
    order_no: str
    user_id: int
    plugin_id: int
    amount: Decimal
    service_fee: Decimal
    developer_income: Decimal
    status: OrderStatus
    created_at: datetime
    paid_at: datetime | None


class WithdrawIn(BaseModel):
    amount: Decimal = Field(gt=0)
    account: str = Field(min_length=34, max_length=34, pattern="^T[1-9A-HJ-NP-Za-km-z]{33}$")


class WithdrawalOut(ORMModel):
    id: int
    user_id: int
    amount: Decimal
    method: str
    account: str
    status: str
    remark: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

class ProfileOut(ORMModel):
    id: int
    user_id: int
    nickname: str
    avatar: str
    bio: str
    is_developer: bool
    balance: float
    frozen_balance: float
    total_income: float
    total_withdrawn: float


class ProfileUpdateIn(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    bio: str | None = None


class WalletIn(BaseModel):
    address: str = Field(min_length=34, max_length=34, pattern="^T[1-9A-HJ-NP-Za-km-z]{33}$")


class PluginVersionCreateIn(BaseModel):
    version: str = Field(min_length=1, max_length=32, pattern=r"^[0-9A-Za-z][0-9A-Za-z._+-]*$")
    compatibility: str = Field(default="", max_length=255)
    changelog: str = ""


class PluginVersionUpdateIn(BaseModel):
    compatibility: str | None = Field(default=None, max_length=255)
    changelog: str | None = None
    documentation: str | None = None


class PluginMediaIn(BaseModel):
    media_type: str = Field(pattern="^(logo|carousel)$")
    url: str = Field(min_length=1, max_length=500)
    alt_text: str = Field(default="", max_length=255)
    sort: int = Field(default=0, ge=0, le=9999)


class VersionReviewIn(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    reason: str = Field(default="", max_length=500)
    service_fee_rate: Decimal | None = Field(default=None, ge=0, le=100)


class WithdrawalHandleIn(BaseModel):
    action: str = Field(pattern="^(approve|reject|done)$")
    remark: str = Field(default="", max_length=500)
    tx_hash: str = Field(default="", max_length=128)
