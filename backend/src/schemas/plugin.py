"""Pydantic schemas for plugin management."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

ORMConfig = ConfigDict(from_attributes=True)


class PluginOut(BaseModel):
    """Plugin info returned to frontend."""

    model_config = ORMConfig
    id: int
    name: str
    display_name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    module_path: str = ""
    enabled: bool = False
    config: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class PluginToggle(BaseModel):
    """Toggle plugin enable/disable."""

    enabled: bool = Field(..., description="true=启用 false=禁用")


class PluginConfigUpdate(BaseModel):
    """Update plugin config JSON."""

    config: dict[str, Any] = Field(default_factory=dict, description="插件配置键值对")
