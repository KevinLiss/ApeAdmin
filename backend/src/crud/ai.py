"""CRUD for AI provider and chat sessions."""

import json
from typing import Any

from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.ai import AiProvider, ChatMessageModel, ChatSession


class CrudAiProvider(CRUDBase[AiProvider]):
    """CRUD for AI provider with encrypted API key support."""

    async def get_by_id(self, db: AsyncSession, id: int) -> AiProvider | None:
        return await self.get(db, id)

    async def list_enabled(self, db: AsyncSession) -> list[AiProvider]:
        """List all enabled providers sorted by sort."""
        stmt = (
            select(AiProvider)
            .where(AiProvider.enabled == 1)
            .order_by(AiProvider.sort, AiProvider.id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_first_enabled(self, db: AsyncSession) -> AiProvider | None:
        """Get the first enabled provider (for auto-selection)."""
        stmt = (
            select(AiProvider)
            .where(AiProvider.enabled == 1)
            .order_by(AiProvider.sort, AiProvider.id)
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class CrudChatSession(CRUDBase[ChatSession]):
    """CRUD for chat sessions scoped by user."""

    async def list_by_user(self, db: AsyncSession, user_id: int) -> list[ChatSession]:
        """List a user's sessions, newest first."""
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_owned(self, db: AsyncSession, session_id: int, user_id: int) -> ChatSession | None:
        """Get a session only if it belongs to the user."""
        stmt = select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def append_message(
        self,
        db: AsyncSession,
        session: ChatSession,
        *,
        role: str,
        content: str,
        tool_events: list[dict] | None = None,
    ) -> ChatMessageModel:
        """Append a message and update session counter/title."""
        msg = ChatMessageModel(
            session_id=session.id,
            role=role,
            content=content,
            tool_events=json.dumps(tool_events, ensure_ascii=False) if tool_events else None,
        )
        db.add(msg)
        session.message_count += 1
        # 用首条用户消息作为会话标题
        if role == "user" and session.title == "新对话" and content.strip():
            session.title = content.strip()[:50]
        await db.flush()
        await db.refresh(msg)
        return msg

    async def list_messages(self, db: AsyncSession, session_id: int) -> list[ChatMessageModel]:
        """List messages of a session in chronological order."""
        stmt = (
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.id.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete_owned(self, db: AsyncSession, session_id: int, user_id: int) -> bool:
        """Delete a session and its messages. Returns True if deleted."""
        session = await self.get_owned(db, session_id, user_id)
        if session is None:
            return False
        await db.execute(
            sa_delete(ChatMessageModel).where(ChatMessageModel.session_id == session_id)
        )
        await db.delete(session)
        return True


crud_ai_provider = CrudAiProvider(AiProvider)
crud_chat_session = CrudChatSession(ChatSession)
