"""AI chat routes: non-stream and SSE streaming with tool execution."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.agent import chat_non_stream, chat_stream
from src.core.deps import get_current_user
from src.core.exceptions import AppException, success_response
from src.crud.ai import crud_ai_provider
from src.db import get_db
from src.models import User
from src.schemas.ai import ChatRequest, ChatStreamRequest

router = APIRouter(prefix="/ai/chat", tags=["AI 对话"])


async def _get_provider(db: AsyncSession, provider_id: int | None):
    """Resolve the AI provider to use."""
    if provider_id:
        provider = await crud_ai_provider.get(db, provider_id)
        if not provider:
            raise AppException("指定的模型供应商不存在", code=404)
        if provider.enabled != 1:
            raise AppException("该模型供应商已被禁用", code=400)
        return provider

    provider = await crud_ai_provider.get_first_enabled(db)
    if not provider:
        raise AppException("未配置任何可用的模型供应商，请先在「模型密钥管理」中添加", code=400)
    return provider


@router.post("")
async def chat(
    body: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Non-streaming chat endpoint."""
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
