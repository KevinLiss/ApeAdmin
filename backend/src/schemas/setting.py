"""Schemas for system settings."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class SettingOut(BaseModel):
    """Setting item for admin list."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    value: str
    description: str
    is_public: bool
    category: str


class SettingUpdate(BaseModel):
    """Single setting update (key-value)."""
    value: str


class SettingsBatchUpdate(BaseModel):
    """Batch update settings: {key: value, ...}"""
    items: dict[str, str]


class PublicSettingsOut(BaseModel):
    """Public settings returned to unauthenticated clients."""
    site_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    admin_path: Optional[str] = None
    footer_text: Optional[str] = None
