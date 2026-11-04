"""AI chat run routes: enqueue / SSE subscribe / active-run / stop.

The run executes in a background task (src/ai/runner.py) and outlives the
HTTP request: closing the page or navigating away never kills a generation.
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai import runner
from src.api.chat import _check_chat_quota, _get_provider
from src.core.deps import get_current_user
from src.core.exceptions import NotFoundException, success_response
from src.core.i18n import t
from src.crud.ai import crud_chat_session
from src.db import get_db
from src.models import User
from src.models.ai import ChatRun
from src.schemas.ai import RunCreate

router = APIRouter(prefix="/ai/chat/runs", tags=["AI 全能助手"])


async def _get_owned_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> ChatRun:
    """Fetch a run only if it belongs to the current user."""
    run = await db.get(ChatRun, run_id)
    if run is None or run.user_id != user.id:
        raise NotFoundException(t("chat_session.not_found"))
    return run


def _run_state(run: ChatRun) -> dict:
    """Serialize run state, preferring the live buffer when present."""
    buf = runner.get_buffer(run.id)
    if buf is not None:
        return {
            "run_id": run.id,
            "session_id": run.session_id,
            "status": buf.status,
            "answer": buf.answer,
            "tool_events": buf.tool_events,
            "error": buf.error,
        }
    tool_events: list = []
    if run.tool_events:
        try:
            tool_events = json.loads(run.tool_events)
        except (json.JSONDecodeError, TypeError):
            tool_events = []
    return {
        "run_id": run.id,
        "session_id": run.session_id,
        "status": run.status,
        "answer": run.answer,
        "tool_events": tool_events,
        "error": run.error,
    }


@router.post("")
async def create_run(
    body: RunCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Enqueue a chat run. Returns immediately with run_id + session_id.

    If the session already has a pending/running run, the new question is
    queued behind it (FIFO) instead of being rejected.
    """
    _check_chat_quota(user)

    # Resolve/create the session (server-side ownership check).
    if body.session_id is not None:
        session = await crud_chat_session.get_owned(db, body.session_id, user.id)
        if session is None:
            raise NotFoundException(t("chat_session.not_found"))
        session_id = session.id
    else:
        from src.models.ai import ChatSession

        session = ChatSession(user_id=user.id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # Provider: explicit id > first enabled.
    provider = await _get_provider(db, body.provider_id)
    model = body.model or None

    run = await runner.enqueue_run(
        user_id=user.id,
        session_id=session_id,
        provider_id=provider.id,
        model=model,
        question=body.question.strip(),
        enable_tools=body.enable_tools,
    )
    return success_response(data={
        "run_id": run.id,
        "session_id": session_id,
        "status": run.status,
        "provider_id": provider.id,
        "model": model or "",
        "title": session.title,
    }, msg="已提交")


@router.get("/{run_id}/events")
async def run_events(
    run: Annotated[ChatRun, Depends(_get_owned_run)],
    db: Annotated[AsyncSession, Depends(get_db)],
    seen_events: int = Query(default=0, ge=0, description="客户端已处理的事件数"),
):
    """SSE stream of run events (snapshot + increments + terminal state).

    The generation continues regardless of this connection; reconnect with
    ``seen_events`` (or without it for a fresh snapshot) to resume.
    """

    async def event_generator():
        try:
            async for payload in runner.stream_run_events(db, run, seen_events):
                yield f"data: {payload}\n\n"
        except Exception as exc:  # noqa: BLE001
            error = json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False)
            yield f"data: {error}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{run_id}")
async def get_run(
    run: Annotated[ChatRun, Depends(_get_owned_run)],
):
    """Poll a run's current state (fallback when SSE is unavailable)."""
    return success_response(data=_run_state(run))


@router.post("/{run_id}/stop")
async def stop_run(
    run: Annotated[ChatRun, Depends(_get_owned_run)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Stop a pending/running run. Already-generated content is kept."""
    if run.status in ("done", "failed", "stopped"):
        return success_response(data={"run_id": run.id, "status": run.status}, msg="已结束，无需停止")
    updated = await runner.stop_run(db, run)
    return success_response(
        data={"run_id": updated.id, "status": updated.status}, msg="正在停止"
    )


@router.get("/session/{session_id}/active")
async def active_run(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """The pending/running run of a session with its partial answer."""
    session = await crud_chat_session.get_owned(db, session_id, user.id)
    if session is None:
        raise NotFoundException(t("chat_session.not_found"))
    data = await runner.get_active_run(db, session_id, user.id)
    return success_response(data=data)
