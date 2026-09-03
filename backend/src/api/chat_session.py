"""AI chat session routes: conversation persistence (list/create/rename/delete/messages)."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.core.exceptions import AppException, NotFoundException, success_response
from src.crud.ai import crud_chat_session
from src.db import get_db
from src.models import User
from src.schemas.ai import (
    SessionAppendMessage,
    SessionCreate,
    SessionMessageOut,
    SessionOut,
    SessionRename,
)

router = APIRouter(prefix="/ai/sessions", tags=["AI 全能助手"])


def _session_out(s) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "provider_id": s.provider_id,
        "model": s.model,
        "message_count": s.message_count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _message_out(m) -> dict:
    tool_events = None
    if m.tool_events:
        try:
            tool_events = json.loads(m.tool_events)
        except (json.JSONDecodeError, TypeError):
            tool_events = None
    return {
        "id": m.id,
        "session_id": m.session_id,
        "role": m.role,
        "content": m.content,
        "tool_events": tool_events,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


async def _get_owned_session(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    session = await crud_chat_session.get_owned(db, session_id, user.id)
    if session is None:
        raise NotFoundException("会话不存在")
    return session


@router.get("")
async def list_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """List current user's chat sessions, newest first."""
    sessions = await crud_chat_session.list_by_user(db, user.id)
    items = [_session_out(s) for s in sessions]
    return success_response(data={"total": len(items), "items": items})


@router.post("")
async def create_session(
    body: SessionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Create a new chat session."""
    from src.models.ai import ChatSession

    session = ChatSession(
        user_id=user.id,
        title=(body.title or "新对话").strip()[:200] or "新对话",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return success_response(data=_session_out(session), msg="会话已创建")


@router.get("/{session_id}")
async def get_session_messages(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Get all messages of a session (chronological)."""
    session = await _get_owned_session(session_id, db, user)
    messages = await crud_chat_session.list_messages(db, session.id)
    items = [_message_out(m) for m in messages]
    return success_response(data={"session": _session_out(session), "messages": items})


@router.put("/{session_id}")
async def rename_session(
    session_id: int,
    body: SessionRename,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Rename a session."""
    session = await _get_owned_session(session_id, db, user)
    session.title = body.title.strip()[:200]
    await db.commit()
    await db.refresh(session)
    return success_response(data=_session_out(session), msg="会话已重命名")


@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Delete a session and its messages."""
    ok = await crud_chat_session.delete_owned(db, session_id, user.id)
    if not ok:
        raise NotFoundException("会话不存在")
    await db.commit()
    return success_response(msg="会话已删除")


@router.post("/{session_id}/messages")
async def append_message(
    session_id: int,
    body: SessionAppendMessage,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Append a message to a session (frontend calls after user send / assistant done)."""
    session = await _get_owned_session(session_id, db, user)
    msg = await crud_chat_session.append_message(
        db,
        session,
        role=body.role,
        content=body.content,
        tool_events=body.tool_events,
    )
    await db.commit()
    return success_response(data=_message_out(msg), msg="消息已保存")
