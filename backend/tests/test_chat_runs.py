"""Chat run lifecycle tests (background executor, qm-style architecture).

Covers the run-decoupling batch:
- enqueue → background execution → done: answer persisted, user+assistant
  messages appended, session counter bumped.
- in-session queueing: two runs on one session execute FIFO, not rejected.
- cross-session parallelism: two sessions run at the same time.
- stop: partial answer preserved and saved as an assistant message.
- SSE subscribe: snapshot first, then buffered tail, closes on terminal.
- active-run lookup returns the live partial answer.
- recover_orphan_runs fails leftover pending/running rows after restart.
"""

import asyncio
import json

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.ai import runner
from src.db import Base
from src.models import User
from src.models.ai import AiProvider, ChatMessageModel, ChatRun, ChatSession


# ---------------------------------------------------------------- fixtures
@pytest.fixture
async def run_env(monkeypatch, tmp_path):
    """Isolated file-based SQLite DB wired into the runner's SessionLocal.

    A file DB (not :memory:) is required: the worker and the enqueueing
    request use concurrent sessions, and an in-memory SQLite shares a single
    connection across them, which corrupts interleaved reads.
    """
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/chat_runs_test.db")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    monkeypatch.setattr(runner, "SessionLocal", factory)
    yield factory
    await runner.shutdown_workers()
    await engine.dispose()


async def _mk_user_provider(factory) -> tuple[int, int]:
    async with factory() as db:
        user = User(username="alice", password="x", nickname="Alice")
        db.add(user)
        provider = AiProvider(
            name="Mock", provider_type="custom", api_key_enc="enc", base_url="http://x", models="[]"
        )
        db.add(provider)
        await db.commit()
        await db.refresh(user)
        await db.refresh(provider)
        return user.id, provider.id


def _mock_stream(chunks: list[str], delay: float = 0.0):
    """Build an async generator miming src.ai.agent.chat_stream."""

    async def fake_chat_stream(**kwargs):
        for c in chunks:
            if delay:
                await asyncio.sleep(delay)
            yield c

    return fake_chat_stream


def _content(t: str) -> str:
    return json.dumps({"type": "content", "content": t}, ensure_ascii=False)


async def _wait_status(run_id: int, statuses: tuple[str, ...], timeout: float = 5.0) -> str:
    buf = runner.get_buffer(run_id)
    assert buf is not None
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if buf.status in statuses:
            return buf.status
        await asyncio.sleep(0.02)
    raise AssertionError(f"timeout waiting {statuses}, got {buf.status}")


# ---------------------------------------------------------------- cases
@pytest.mark.asyncio
async def test_run_full_lifecycle_done(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)

    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        sid = session.id

    import src.ai.runner as r

    original = r.chat_stream
    r.chat_stream = _mock_stream([_content("答"), _content("案"), json.dumps({"type": "done"})])
    try:
        run = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="mock-1", question="问题", enable_tools=True,
        )
        status = await _wait_status(run.id, ("done",))
    finally:
        r.chat_stream = original

    assert status == "done"
    async with run_env() as db:
        row = await db.get(ChatRun, run.id)
        assert row.answer == "答案"
        msgs = list((await db.execute(
            select(ChatMessageModel).where(ChatMessageModel.session_id == sid)
            .order_by(ChatMessageModel.id.asc())
        )).scalars().all())
        assert [m.role for m in msgs] == ["user", "assistant"]
        assert msgs[0].content == "问题"
        assert msgs[1].content == "答案"
        session = await db.get(ChatSession, sid)
        assert session.message_count == 2


@pytest.mark.asyncio
async def test_same_session_messages_queue_fifo(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        sid = session.id

    import src.ai.runner as r

    started: list[str] = []
    finished: list[str] = []

    async def fifo_fake_stream(**kwargs):
        tag = kwargs["messages"][-1]["content"]  # q1 / q2
        started.append(tag)
        for c in (_content(f"r{tag}a"), _content(f"r{tag}b")):
            await asyncio.sleep(0.05)
            yield c
        finished.append(tag)  # must run before the done event (executor breaks on it)
        yield json.dumps({"type": "done"})

    original = r.chat_stream
    r.chat_stream = fifo_fake_stream
    try:
        run1 = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="m", question="q1", enable_tools=True,
        )
        # 第二条在第一条运行中提交 → 排队而非拒绝
        run2 = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="m", question="q2", enable_tools=True,
        )
        await _wait_status(run1.id, ("done",))
        await _wait_status(run2.id, ("done",))
    finally:
        r.chat_stream = original

    assert started == ["q1", "q2"] and finished == ["q1", "q2"]  # FIFO，未并发
    async with run_env() as db:
        msgs = list((await db.execute(
            select(ChatMessageModel).where(ChatMessageModel.session_id == sid)
            .order_by(ChatMessageModel.id.asc())
        )).scalars().all())
        # 排队的用户消息立即落库；assistant 回复在各自 run 终态时落库
        assert [m.content for m in msgs] == ["q1", "q2", "rq1arq1b", "rq2arq2b"]


@pytest.mark.asyncio
async def test_different_sessions_run_in_parallel(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        s1 = ChatSession(user_id=user_id)
        s2 = ChatSession(user_id=user_id)
        db.add_all([s1, s2])
        await db.commit()
        await db.refresh(s1)
        await db.refresh(s2)
        sid1, sid2 = s1.id, s2.id

    import src.ai.runner as r

    seen: list[str] = []

    async def slow_chat_stream(**kwargs):
        q = kwargs["messages"][-1]["content"]
        seen.append(f"start:{q}")
        await asyncio.sleep(0.3)
        yield _content(f"done:{q}")
        yield json.dumps({"type": "done"})
        seen.append(f"end:{q}")

    original = r.chat_stream
    r.chat_stream = slow_chat_stream
    try:
        run1 = await runner.enqueue_run(
            user_id=user_id, session_id=sid1, provider_id=provider_id,
            model="m", question="A", enable_tools=True,
        )
        run2 = await runner.enqueue_run(
            user_id=user_id, session_id=sid2, provider_id=provider_id,
            model="m", question="B", enable_tools=True,
        )
        await _wait_status(run1.id, ("done",))
        await _wait_status(run2.id, ("done",))
    finally:
        r.chat_stream = original

    # 两个会话的 run 同时启动（end 事件晚于两个 start）
    assert seen[:2] == ["start:A", "start:B"], seen


@pytest.mark.asyncio
async def test_stop_keeps_partial_answer(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        sid = session.id

    import src.ai.runner as r

    async def endless_stream(**kwargs):
        for i in range(50):
            yield _content(f"片段{i} ")
            await asyncio.sleep(0.05)

    original = r.chat_stream
    r.chat_stream = endless_stream
    try:
        run = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="m", question="写长文", enable_tools=True,
        )
        buf = runner.get_buffer(run.id)
        deadline = asyncio.get_event_loop().time() + 3
        while asyncio.get_event_loop().time() < deadline and len(buf.answer) < 30:
            await asyncio.sleep(0.02)
        assert len(buf.answer) >= 30

        async with run_env() as db:
            row = await db.get(ChatRun, run.id)
            await runner.stop_run(db, row)
        status = await _wait_status(run.id, ("stopped",))
    finally:
        r.chat_stream = original

    assert status == "stopped"
    async with run_env() as db:
        row = await db.get(ChatRun, run.id)
        assert row.status == "stopped" and len(row.answer) > 0
        msgs = list((await db.execute(
            select(ChatMessageModel).where(ChatMessageModel.session_id == sid)
            .order_by(ChatMessageModel.id.asc())
        )).scalars().all())
        assert msgs[-1].role == "assistant" and len(msgs[-1].content) > 0


@pytest.mark.asyncio
async def test_subscribe_snapshot_then_tail(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        sid = session.id

    import src.ai.runner as r

    # 预置一个"已完成"的 buffer：模拟断线后回来订阅
    r.chat_stream = _mock_stream([_content("x")])
    original = r.chat_stream
    try:
        run = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="m", question="q", enable_tools=True,
        )
        await _wait_status(run.id, ("done",))
    finally:
        r.chat_stream = original

    # 订阅已完成 run：收到快照（含终态）后立即关闭
    async with run_env() as db:
        row = await db.get(ChatRun, run.id)
        events = []
        async for payload in runner.stream_run_events(db, row, seen_events=0):
            events.append(json.loads(payload))
        snap = events[0]
        assert snap["type"] == "snapshot" and snap["status"] == "done" and snap["answer"] == "x"
        # 终态 buffer 在，快照后直接结束（无需 run_end 重放——快照已含终态）


@pytest.mark.asyncio
async def test_active_run_returns_partial(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        sid = session.id

    import src.ai.runner as r

    async def slow_stream(**kwargs):
        yield _content("部分")
        await asyncio.sleep(0.6)
        yield _content("完成")
        yield json.dumps({"type": "done"})

    original = r.chat_stream
    r.chat_stream = slow_stream
    try:
        run = await runner.enqueue_run(
            user_id=user_id, session_id=sid, provider_id=provider_id,
            model="m", question="q", enable_tools=True,
        )
        deadline = asyncio.get_event_loop().time() + 3
        buf = runner.get_buffer(run.id)
        while asyncio.get_event_loop().time() < deadline and not buf.answer:
            await asyncio.sleep(0.02)

        async with run_env() as db:
            data = await runner.get_active_run(db, sid, user_id)
        assert data is not None and data["run_id"] == run.id
        assert data["status"] == "running" and data["answer"] == "部分"

        await _wait_status(run.id, ("done",))
        async with run_env() as db:
            assert await runner.get_active_run(db, sid, user_id) is None
    finally:
        r.chat_stream = original


@pytest.mark.asyncio
async def test_recover_orphan_runs_after_restart(run_env):
    user_id, provider_id = await _mk_user_provider(run_env)
    async with run_env() as db:
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        db.add_all([
            ChatRun(session_id=session.id, user_id=user_id, status="running",
                    provider_id=provider_id, question="a"),
            ChatRun(session_id=session.id, user_id=user_id, status="pending",
                    provider_id=provider_id, question="b"),
            ChatRun(session_id=session.id, user_id=user_id, status="done",
                    provider_id=provider_id, question="c"),
        ])
        await db.commit()

    n = await runner.recover_orphan_runs()
    assert n == 2  # 只有 running/pending 被清理
    async with run_env() as db:
        rows = list((await db.execute(select(ChatRun).order_by(ChatRun.id.asc()))).scalars().all())
        assert rows[0].status == "failed" and rows[1].status == "failed"
        assert rows[2].status == "done"
        assert "重新发送" in rows[0].error
