"""ApeHub Pydantic schemas for request/response validation."""

from datetime import datetime
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
    service_fee_rate: float | None = None


class SiteConfigOut(ORMModel):
    id: int
    site_name: str
    site_logo: str
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
    service_fee_rate: float
    # 不返回 mail_code / lempay_key（敏感）


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
    price: float = 0.0
    service_fee_rate: float = 30.0
    demos: list[PluginDemoIn] = []


class PluginReviewIn(BaseModel):
    action: str  # approve / reject
    reason: str = ""


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
    price: float
    service_fee_rate: float
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


class OrderOut(ORMModel):
    id: int
    order_no: str
    user_id: int
    plugin_id: int
    amount: float
    service_fee: float
    developer_income: float
    status: OrderStatus
    created_at: datetime
    paid_at: datetime | None


class WithdrawIn(BaseModel):
    amount: float = Field(gt=0)
    method: str = "alipay"
    account: str = Field(min_length=4)


class WithdrawalOut(ORMModel):
    id: int
    user_id: int
    amount: float
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