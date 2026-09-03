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


class ChatSession(IDMixin, TimestampMixin, Base):
    """AI chat session: a conversation thread owned by a user."""

    __tablename__ = "chat_session"

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属用户ID")
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, default="新对话", comment="会话标题(取首条用户消息)"
    )
    provider_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="最近使用的供应商ID"
    )
    model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="最近使用的模型名"
    )
    message_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="消息数量"
    )

    def __repr__(self) -> str:
        return f"<ChatSession {self.id} user={self.user_id}>"


class ChatMessageModel(IDMixin, TimestampMixin, Base):
    """AI chat message: single user/assistant message in a session."""

    __tablename__ = "chat_message"

    session_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属会话ID"
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="消息内容")
    tool_events: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="工具调用事件(JSON数组)"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} session={self.session_id} role={self.role}>"
