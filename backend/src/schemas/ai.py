"""Pydantic schemas for AI provider and chat."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# AI Provider
# ---------------------------------------------------------------------------

ORMConfig = ConfigDict(from_attributes=True)


class ProviderBase(BaseModel):
    name: str = Field(..., max_length=100)
    provider_type: str = Field(..., max_length=50, description="deepseek/qwen/glm/openai/custom")
    base_url: str = ""
    models: list[str] = Field(default_factory=list)
    enabled: int = 1
    sort: int = 0
    remark: str | None = None


class ProviderCreate(ProviderBase):
    api_key: str = Field(..., min_length=1, description="明文API Key，后端加密存储")


class ProviderUpdate(BaseModel):
    name: str | None = None
    provider_type: str | None = None
    base_url: str | None = None
    models: list[str] | None = None
    api_key: str | None = None  # 可选，不传则不修改
    enabled: int | None = None
    sort: int | None = None
    remark: str | None = None


class ProviderOut(BaseModel):
    model_config = ORMConfig
    id: int
    name: str
    provider_type: str
    base_url: str
    models: list[str] = Field(default_factory=list)
    enabled: int
    sort: int
    remark: str | None = None
    api_key_masked: str = ""  # 脱敏显示
    created_at: datetime


# ---------------------------------------------------------------------------
# AI Chat
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="user/assistant/system/tool")
    content: str = ""


class ChatRequest(BaseModel):
    """Non-stream chat request."""
    messages: list[ChatMessage]
    provider_id: int | None = None  # 指定供应商，None=自动选启用的第一个
    model: str | None = None  # 覆盖模型名
    max_tokens: int = 2000
    temperature: float = 0.7


class ChatStreamRequest(BaseModel):
    """Streaming chat request (SSE)."""
    messages: list[ChatMessage]
    provider_id: int | None = None
    model: str | None = None
    max_tokens: int = 2000
    temperature: float = 0.7
    enable_tools: bool = True  # 是否启用系统工具调用
