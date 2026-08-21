"""AI domain models: AI provider (model key management) and chat session."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class AiProvider(IDMixin, TimestampMixin, Base):
    """AI model provider: stores API key (encrypted) for DeepSeek/Qwen/GLM/OpenAI etc."""

    __tablename__ = "ai_provider"

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="供应商名称")
    provider_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="类型: deepseek/qwen/glm/openai/custom"
    )
    api_key_enc: Mapped[str] = mapped_column(Text, nullable=False, comment="加密后的API Key")
    base_url: Mapped[str] = mapped_column(
        String(500), nullable=False, default="", comment="API基础地址"
    )
    models: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]", comment="支持的模型列表(JSON数组)"
    )
    enabled: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="是否启用: 0=禁用 1=启用"
    )
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    remark: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="备注")

    def __repr__(self) -> str:
        return f"<AiProvider {self.name} ({self.provider_type})>"
