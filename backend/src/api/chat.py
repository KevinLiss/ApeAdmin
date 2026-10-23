"""AI chat routes: non-stream and SSE streaming with tool execution."""

import json
import time
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.agent import chat_non_stream, chat_stream
from src.core.config import settings
from src.core.deps import get_current_user
from src.core.exceptions import AppException, success_response
from src.core.i18n import t, get_locale
from src.crud.ai import crud_ai_provider
from src.db import get_db
from src.models import User
from src.schemas.ai import ChatRequest, ChatStreamRequest

router = APIRouter(prefix="/ai/chat", tags=["AI 全能助手"])


# ---------------------------------------------------------------- quota
# Per-user daily call cap for LLM endpoints. In-memory on purpose: the
# admin panel is single-worker, and a restart resetting counters is an
# acceptable trade-off for zero-schema overhead. Stops runaway API
# spend (loop / curious user), not adversarial bypass.
_daily_usage: dict[int, dict[str, int]] = {}  # user_id -> {"date": YYYYMMDD, "count": n}


def _check_chat_quota(user: User) -> None:
    """Raise a 429 AppException once the per-user daily quota is exhausted."""
    limit = settings.AI_DAILY_LIMIT
    if limit <= 0:  # 0 / negative disables the cap
        return
    today = time.strftime("%Y%m%d")
    entry = _daily_usage.setdefault(user.id, {})
    if entry.get("date") != today:
        entry.clear()
        entry["date"] = today
    if entry.get("count", 0) >= limit:
        raise AppException(t("chat.daily_limit_reached", limit=limit), code=429)
    entry["count"] = entry.get("count", 0) + 1


async def _get_provider(db: AsyncSession, provider_id: int | None):
    """Resolve the AI provider to use."""
    if provider_id:
        provider = await crud_ai_provider.get(db, provider_id)
        if not provider:
            raise AppException(t("chat.provider_not_found"), code=404)
        if provider.enabled != 1:
            raise AppException(t("chat.provider_disabled"), code=400)
        return provider

    provider = await crud_ai_provider.get_first_enabled(db)
    if not provider:
        raise AppException(t("chat.no_provider_configured"), code=400)
    return provider


@router.post("")
async def chat(
    body: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Non-streaming chat endpoint."""
    _check_chat_quota(user)
    provider = await _get_provider(db, body.provider_id)
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    result = await chat_non_stream(
        messages=messages,
        provider=provider,
        model=body.model,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        enable_tools=True,
        user=user,
    )
    return success_response(data=result)


@router.post("/stream")
async def chat_stream_endpoint(
    body: ChatStreamRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Streaming chat endpoint (SSE)."""
    _check_chat_quota(user)
    provider = await _get_provider(db, body.provider_id)
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    async def event_generator():
        """Generate SSE events for the streaming chat."""
        try:
            async for chunk in chat_stream(
                messages=messages,
                provider=provider,
                model=body.model,
                max_tokens=body.max_tokens,
                temperature=body.temperature,
                enable_tools=body.enable_tools,
                user=user,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
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
