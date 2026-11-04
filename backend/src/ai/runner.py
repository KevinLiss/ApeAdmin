"""Background chat run executor (qm-style run architecture).

Decouples LLM execution from the HTTP request lifecycle:

- ``enqueue_run`` persists a ChatRun (pending) plus the user message, then
  spawns/reuses a per-session worker task and returns immediately.
- The worker claims the oldest pending run of the session (in-session
  messages queue up instead of being rejected; different sessions run in
  parallel), executes it with ``chat_stream`` and persists partial answers
  while streaming, so a browser leaving the page never kills the run.
- Subscribers attach via ``stream_run_events`` (async generator). Events are
  buffered in memory with an absolute index; reconnecting clients pass the
  number of events already seen and get a full snapshot + the tail.
- ``stop_run`` sets a cancel flag; the executor honours it at the next
  event boundary and keeps whatever was already generated.
- On process boot ``recover_orphan_runs`` fails runs left behind by a
  restart (in-memory workers are gone; the user is asked to resend).

Single-worker admin panel: buffers live in this process by design (same
trade-off as the in-memory chat quota in src/api/chat.py).
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from loguru import logger
from sqlalchemy import select

from src.ai.agent import chat_stream
from src.crud.ai import crud_chat_session
from src.db import SessionLocal
from src.models import User
from src.models.ai import AiProvider, ChatMessageModel, ChatRun

# ---------------------------------------------------------------- in-memory state

TERMINAL_STATUSES = ("done", "failed", "stopped")

# How often (seconds) partial answers are flushed to DB while streaming.
_DB_FLUSH_INTERVAL = 0.5
# Max history messages sent to the LLM as context.
_CONTEXT_WINDOW = 40


@dataclass
class RunBuffer:
    """In-memory live state of one run: SSE buffer + subscriber wakeup."""

    run_id: int = 0
    session_id: int = 0
    status: str = "pending"  # pending/running/done/failed/stopped
    answer: str = ""
    tool_events: list[dict] = field(default_factory=list)
    error: str | None = None
    events: list[str] = field(default_factory=list)  # buffered SSE payloads, index = offset
    cond: asyncio.Condition = field(default_factory=asyncio.Condition)
    cancel_requested: bool = False
    last_flush: float = 0.0


_buffers: dict[int, RunBuffer] = {}
_workers: dict[int, asyncio.Task] = {}  # session_id -> worker task


class RunCancelled(Exception):
    """Raised inside the executor when the user requested a stop."""


# ---------------------------------------------------------------- helpers
def _now() -> datetime:
    return datetime.now(timezone.utc)


def _publish(buf: RunBuffer, payload: dict[str, Any]) -> None:
    """Append an event to the buffer and wake up all subscribers."""
    buf.events.append(json.dumps(payload, ensure_ascii=False))


async def _apublish(buf: RunBuffer, payload: dict[str, Any]) -> None:
    buf.events.append(json.dumps(payload, ensure_ascii=False))
    async with buf.cond:
        buf.cond.notify_all()


async def _run_snapshot_payload(db, run: ChatRun, status: str) -> dict[str, Any]:
    tool_events = []
    if run.tool_events:
        try:
            tool_events = json.loads(run.tool_events)
        except (json.JSONDecodeError, TypeError):
            tool_events = []
    return {
        "run_id": run.id,
        "session_id": run.session_id,
        "status": status,
        "answer": run.answer,
        "tool_events": tool_events,
        "error": run.error,
    }


async def _flush_answer(db, run_id: int, buf: RunBuffer) -> None:
    """Persist the partial answer/tool events (throttled)."""
    now = time.monotonic()
    if now - buf.last_flush < _DB_FLUSH_INTERVAL:
        return
    buf.last_flush = now
    run = await db.get(ChatRun, run_id)
    if run is None:
        return
    run.answer = buf.answer
    run.tool_events = json.dumps(buf.tool_events, ensure_ascii=False) if buf.tool_events else None
    await db.commit()


async def _finish_run(
    db,
    run: ChatRun,
    buf: RunBuffer,
    *,
    status: str,
    error: str | None = None,
    save_assistant_message: bool = True,
) -> None:
    """Write the terminal state: run row + assistant chat message."""
    run.status = status
    run.answer = buf.answer
    run.tool_events = json.dumps(buf.tool_events, ensure_ascii=False) if buf.tool_events else None
    run.error = error
    run.finished_at = _now()
    await db.commit()

    if save_assistant_message and (buf.answer.strip() or buf.tool_events):
        session = await crud_chat_session.get_owned(db, run.session_id, run.user_id)
        if session is not None:
            await crud_chat_session.append_message(
                db,
                session,
                role="assistant",
                content=buf.answer,
                tool_events=buf.tool_events or None,
            )
            await db.commit()

    buf.status = status
    buf.error = error
    await _apublish(buf, {"type": "run_end", "status": status, "error": error})
    # Buffer is kept so late subscribers (polling after finish) still see the
    # tail; it is small and bounded per run. Cleanup happens on shutdown.
    logger.info(f"ChatRun {run.id} → {status} (answer {len(buf.answer)} chars)")


async def _build_context(db, session_id: int, question: str) -> list[dict[str, str]]:
    """Assemble LLM context from persisted messages (server-side source of truth)."""
    stmt = (
        select(ChatMessageModel)
        .where(ChatMessageModel.session_id == session_id)
        .order_by(ChatMessageModel.id.desc())
        .limit(_CONTEXT_WINDOW)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    rows.reverse()
    history = [
        {"role": m.role, "content": m.content}
        for m in rows
        if m.content.strip() or m.role == "user"
    ]
    # The just-persisted user message is already the last row; make sure the
    # conversation doesn't end on an assistant bubble.
    while history and history[-1]["role"] == "assistant":
        history.pop()
    if not history or history[-1]["content"] != question:
        history.append({"role": "user", "content": question})
    return history


# ---------------------------------------------------------------- executor
async def _execute_run(run_id: int) -> None:
    """Run one ChatRun to completion (owns its own DB sessions)."""
    buf = _buffers.get(run_id)
    if buf is None:
        return

    async with SessionLocal() as db:
        run = await db.get(ChatRun, run_id)
        if run is None or run.status not in ("pending", "running"):
            _buffers.pop(run_id, None)
            return

        provider = await db.get(AiProvider, run.provider_id) if run.provider_id else None
        if provider is None or provider.enabled != 1:
            await _finish_run(db, run, buf, status="failed", error="模型供应商不可用或已停用")
            return

        run.status = "running"
        run.started_at = _now()
        await db.commit()
        buf.status = "running"
        await _apublish(buf, {"type": "run_start", "status": "running"})

        user = await db.get(User, run.user_id)

        messages = await _build_context(db, run.session_id, run.question)
        try:
            async for chunk_json in chat_stream(
                messages=messages,
                provider=provider,
                model=run.model,
                enable_tools=bool(run.enable_tools),
                user=user,
            ):
                if buf.cancel_requested:
                    raise RunCancelled()
                try:
                    event = json.loads(chunk_json)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type")
                if etype == "content":
                    buf.answer += event.get("content", "")
                    await _apublish(buf, {"type": "content", "content": event.get("content", "")})
                    await _flush_answer(db, run_id, buf)
                elif etype == "tool_call":
                    buf.tool_events.append({
                        "type": "tool_call",
                        "name": event.get("name"),
                        "arguments": event.get("arguments"),
                    })
                    await _apublish(buf, {"type": "tool_call", "name": event.get("name"),
                                          "arguments": event.get("arguments")})
                elif etype == "tool_result":
                    buf.tool_events.append({
                        "type": "tool_result",
                        "name": event.get("name"),
                        "result": event.get("result"),
                    })
                    await _apublish(buf, {"type": "tool_result", "name": event.get("name"),
                                          "result": event.get("result")})
                elif etype == "done":
                    break

            if buf.cancel_requested:
                raise RunCancelled()
            await _finish_run(db, run, buf, status="done")

        except RunCancelled:
            await _finish_run(db, run, buf, status="stopped")
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"ChatRun {run_id} failed: {exc}")
            await _finish_run(db, run, buf, status="failed", error=str(exc))


async def _session_worker(session_id: int) -> None:
    """Serial executor for one session: claims pending runs FIFO (queue mode)."""
    try:
        while True:
            async with SessionLocal() as db:
                stmt = (
                    select(ChatRun)
                    .where(
                        ChatRun.session_id == session_id,
                        ChatRun.status == "pending",
                    )
                    .order_by(ChatRun.id.asc())
                    .limit(1)
                )
                run = (await db.execute(stmt)).scalar_one_or_none()
            if run is None:
                return
            buf = _buffers.get(run.id)
            if buf is None:
                # Enqueue entry was lost (e.g. stopped while pending): mark it.
                async with SessionLocal() as db:
                    r = await db.get(ChatRun, run.id)
                    if r is not None and r.status == "pending":
                        r.status = "stopped"
                        r.error = "任务已取消"
                        r.finished_at = _now()
                        await db.commit()
                continue
            await _execute_run(run.id)
    except asyncio.CancelledError:
        raise
    except Exception:  # noqa: BLE001
        logger.exception(f"Chat worker for session {session_id} crashed")


# ---------------------------------------------------------------- public API
async def enqueue_run(
    *,
    user_id: int,
    session_id: int,
    provider_id: int | None,
    model: str | None,
    question: str,
    enable_tools: bool = True,
) -> ChatRun:
    """Create a pending run + persist the user message; return immediately."""
    run = ChatRun(
        session_id=session_id,
        user_id=user_id,
        status="pending",
        provider_id=provider_id,
        model=model,
        enable_tools=1 if enable_tools else 0,
        question=question,
    )
    buf = RunBuffer(run_id=0, session_id=session_id)

    async with SessionLocal() as db:
        session = await crud_chat_session.get_owned(db, session_id, user_id)
        if session is None:
            raise ValueError(f"session {session_id} not found")
        session.provider_id = provider_id
        session.model = model
        db.add(run)
        await db.flush()
        await crud_chat_session.append_message(db, session, role="user", content=question)
        await db.commit()
        await db.refresh(run)

    buf.run_id = run.id
    _buffers[run.id] = buf

    worker = _workers.get(session_id)
    if worker is None or worker.done():
        _workers[session_id] = asyncio.create_task(
            _session_worker(session_id), name=f"chat-worker-s{session_id}"
        )
    return run


def register_buffer(run_id: int, buf: RunBuffer) -> None:
    _buffers[run_id] = buf


def get_buffer(run_id: int) -> RunBuffer | None:
    return _buffers.get(run_id)


async def stream_run_events(
    db,
    run: ChatRun,
    seen_events: int = 0,
) -> AsyncGenerator[str, None]:
    """Subscribe to a run's events.

    Sends a full snapshot first (answer/tool_events as of now), then replays
    buffered events the client has not seen and follows live updates until
    the run reaches a terminal state. Works for runs that already finished
    (snapshot + immediate end) and for runs whose buffer is gone (restart).
    """
    buf = _buffers.get(run.id)

    if buf is None:
        # No live buffer (process restarted / run finished earlier): serve
        # the persisted state and close.
        tool_events = []
        if run.tool_events:
            try:
                tool_events = json.loads(run.tool_events)
            except (json.JSONDecodeError, TypeError):
                tool_events = []
        yield json.dumps({
            "type": "snapshot",
            "run_id": run.id,
            "status": run.status,
            "answer": run.answer,
            "tool_events": tool_events,
            "error": run.error,
        }, ensure_ascii=False)
        return

    # Live buffer: initial snapshot protects already-delivered content.
    yield json.dumps({
        "type": "snapshot",
        "run_id": run.id,
        "status": buf.status,
        "answer": buf.answer,
        "tool_events": buf.tool_events,
        "error": buf.error,
    }, ensure_ascii=False)

    offset = max(0, seen_events)
    while True:
        while offset < len(buf.events):
            yield buf.events[offset]
            offset += 1
        if buf.status in TERMINAL_STATUSES:
            return
        async with buf.cond:
            # Re-check under lock to avoid missing the final notify.
            if buf.status in TERMINAL_STATUSES and offset >= len(buf.events):
                return
            try:
                await asyncio.wait_for(buf.cond.wait(), timeout=20.0)
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"  # SSE comment as heartbeat


async def stop_run(db, run: ChatRun) -> ChatRun:
    """Request cancellation. Generated content is preserved.

    For a still-pending (queued) run the user message was persisted at
    enqueue time but never answered — remove it so the transcript has no
    orphan bubble after a withdraw.
    """
    buf = _buffers.get(run.id)
    if run.status == "pending":
        # Best-effort: drop the unanswered user message (last matching row).
        stmt = (
            select(ChatMessageModel)
            .where(
                ChatMessageModel.session_id == run.session_id,
                ChatMessageModel.role == "user",
                ChatMessageModel.content == run.question,
            )
            .order_by(ChatMessageModel.id.desc())
            .limit(1)
        )
        orphan = (await db.execute(stmt)).scalar_one_or_none()
        if orphan is not None:
            await db.delete(orphan)
            session = await crud_chat_session.get_owned(db, run.session_id, run.user_id)
            if session is not None and session.message_count > 0:
                session.message_count -= 1
        run.status = "stopped"
        run.error = "任务已取消"
        run.finished_at = _now()
        await db.commit()
        if buf is not None:
            buf.status = "stopped"
            buf.cancel_requested = True
            await _apublish(buf, {"type": "run_end", "status": "stopped", "error": "任务已取消"})
        return run
    if run.status == "running" and buf is not None:
        buf.cancel_requested = True
    return run


async def get_active_run(db, session_id: int, user_id: int) -> dict[str, Any] | None:
    """The pending/running run of a session with its partial answer."""
    stmt = (
        select(ChatRun)
        .where(
            ChatRun.session_id == session_id,
            ChatRun.user_id == user_id,
            ChatRun.status.in_(("pending", "running")),
        )
        .order_by(ChatRun.id.desc())
    )
    runs = list((await db.execute(stmt)).scalars().all())
    if not runs:
        return None
    active = runs[0]
    buf = _buffers.get(active.id)
    tool_events: list[dict] = []
    queued = 0
    for r in runs:
        if r.id != active.id and r.status == "pending":
            queued += 1
    if buf is not None:
        status = buf.status
        answer = buf.answer
        tool_events = list(buf.tool_events)
    else:
        status = active.status
        answer = active.answer
        if active.tool_events:
            try:
                tool_events = json.loads(active.tool_events)
            except (json.JSONDecodeError, TypeError):
                tool_events = []
    return {
        "run_id": active.id,
        "session_id": session_id,
        "status": status,
        "answer": answer,
        "tool_events": tool_events,
        "error": active.error,
        "question": active.question,
        "queued": queued,
    }


async def recover_orphan_runs() -> int:
    """Fail runs left behind by a process restart (workers are gone)."""
    n = 0
    async with SessionLocal() as db:
        stmt = select(ChatRun).where(ChatRun.status.in_(("pending", "running")))
        for run in (await db.execute(stmt)).scalars().all():
            was_running = run.status == "running"
            run.status = "failed"
            run.error = "服务重启，本轮生成中断，请重新发送" if was_running else "服务重启，请重新发送"
            run.finished_at = _now()
            n += 1
        await db.commit()
    if n:
        logger.info(f"Recovered {n} orphan chat run(s) after restart")
    return n


async def shutdown_workers() -> None:
    """Cancel all per-session worker tasks on app shutdown."""
    tasks = list(_workers.values())
    for t in tasks:
        t.cancel()
    for t in tasks:
        try:
            await t
        except asyncio.CancelledError:
            pass
    _workers.clear()
    _buffers.clear()
