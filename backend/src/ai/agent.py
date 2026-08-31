"""AI chat agent: orchestrates LLM calls, tool execution, and streaming.

Flow:
1. User message → LLM (with system tools as function definitions)
2. LLM responds with tool_calls → execute tools → feed results back
3. LLM generates final natural-language response
4. Stream the response to client via SSE
"""

import json
from typing import Any, AsyncGenerator

import httpx
from loguru import logger

from src.ai.tools import build_tools_for_llm, execute_tool
from src.core.crypto import decrypt_api_key
from src.core.deps import get_user_permissions
from src.db import SessionLocal
from src.models import User
from src.models.ai import AiProvider

# Provider default base URLs and model mappings
PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "deepseek": {"base_url": "https://api.deepseek.com", "default_model": "deepseek-chat"},
    "qwen": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "default_model": "qwen-plus"},
    "glm": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "default_model": "glm-4-flash"},
    "openai": {"base_url": "https://api.openai.com/v1", "default_model": "gpt-4o-mini"},
    "custom": {"base_url": "", "default_model": ""},
}

SYSTEM_PROMPT = """你是 ApeAdmin 智能管理助手，可以帮助用户通过自然语言操作后台管理系统。

你的能力：
1. 用户管理：查询用户列表、查看用户详情、创建用户、更新用户信息、删除用户
2. 角色管理：查询角色列表、创建角色、更新角色、删除角色
3. 部门管理：查询部门树、创建部门、更新部门、删除部门
4. 菜单管理：查询菜单树、创建菜单项、更新菜单、删除菜单
5. 系统工具：系统健康检查、查看已安装插件列表、系统统计信息
6. 插件市场：搜索市场插件、查看插件详情、查询开发者信息、市场统计

使用规则：
- 当用户的请求涉及系统操作时，调用对应的工具完成任务
- 工具调用后，用简洁的中文总结执行结果
- 如果权限不足，告知用户并说明需要什么权限
- 对于普通对话，直接友好地回答
- 创建/更新操作时，如果用户未提供必填参数，先询问用户
"""


def _get_provider_config(provider: AiProvider) -> dict[str, str]:
    """Get base_url and default model for a provider."""
    defaults = PROVIDER_DEFAULTS.get(provider.provider_type, PROVIDER_DEFAULTS["custom"])
    base_url = provider.base_url or defaults["base_url"]
    return {"base_url": base_url, "default_model": defaults["default_model"]}


def _build_tools_for_llm(tools_enabled: bool) -> list[dict[str, Any]]:
    """Return the tools list for LLM function calling."""
    return build_tools_for_llm(tools_enabled)


async def _call_llm(
    messages: list[dict[str, Any]],
    api_key: str,
    base_url: str,
    model: str,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    tools: list[dict[str, Any]] | None = None,
    stream: bool = False,
) -> dict[str, Any]:
    """Call LLM API (OpenAI-compatible format). Returns full response JSON."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    url = f"{base_url.rstrip('/')}/chat/completions"
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()


async def _call_llm_stream(
    messages: list[dict[str, Any]],
    api_key: str,
    base_url: str,
    model: str,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    tools: list[dict[str, Any]] | None = None,
) -> AsyncGenerator[str, None]:
    """Call LLM API in streaming mode, yield SSE data chunks."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    url = f"{base_url.rstrip('/')}/chat/completions"
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, headers=headers, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk.strip() == "[DONE]":
                        yield "[DONE]"
                        return
                    yield chunk


async def chat_non_stream(
    messages: list[dict[str, str]],
    provider: AiProvider,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    enable_tools: bool = True,
    user: User | None = None,
) -> dict[str, Any]:
    """Non-streaming chat with tool execution loop.

    Returns {"content": str, "tool_calls": list, "usage": dict}
    """
    config = _get_provider_config(provider)
    api_key = decrypt_api_key(provider.api_key_enc)
    model_name = model or config["default_model"]
    tools = _build_tools_for_llm(enable_tools)

    # Build message list with system prompt
    llm_messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]

    # Get user permissions for tool execution
    user_permissions = get_user_permissions(user) if user else set()

    # Tool call loop (max 5 rounds)
    for _ in range(5):
        resp = await _call_llm(
            llm_messages, api_key, config["base_url"], model_name,
            max_tokens, temperature, tools,
        )
        msg = resp["choices"][0]["message"]

        # If no tool_calls, we're done
        if not msg.get("tool_calls"):
            return {
                "content": msg.get("content", ""),
                "tool_calls": [],
                "usage": resp.get("usage", {}),
            }

        # Execute each tool call
        llm_messages.append({
            "role": "assistant",
            "content": msg.get("content", ""),
            "tool_calls": msg["tool_calls"],
        })

        tool_results = []
        for tc in msg["tool_calls"]:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                fn_args = {}

            # Execute tool in a DB session
            async with SessionLocal() as db:
                result = await execute_tool(fn_name, fn_args, db, user_permissions, user)

            tool_results.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })
            logger.info(f"Tool executed: {fn_name} -> {result[:200]}")

        llm_messages.extend(tool_results)

    # Fallback: if we exhausted rounds, return last content
    return {"content": "抱歉，工具调用轮次过多，请简化您的请求。", "tool_calls": [], "usage": {}}


async def chat_stream(
    messages: list[dict[str, str]],
    provider: AiProvider,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    enable_tools: bool = True,
    user: User | None = None,
) -> AsyncGenerator[str, None]:
    """Streaming chat with tool execution. Yields SSE-format data.

    Yields events like:
    - {"type":"content","content":"chunk text"}
    - {"type":"tool_call","name":"get_user_list","arguments":{...}}
    - {"type":"tool_result","name":"get_user_list","result":{...}}
    - {"type":"done"}
    """
    config = _get_provider_config(provider)
    api_key = decrypt_api_key(provider.api_key_enc)
    model_name = model or config["default_model"]
    tools = _build_tools_for_llm(enable_tools)

    llm_messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]

    user_permissions = get_user_permissions(user) if user else set()

    # Tool call loop (max 5 rounds)
    for round_num in range(5):
        # Collect streamed content and detect tool calls
        collected_content = ""
        collected_tool_calls: list[dict[str, Any]] = []
        has_tool_calls = False

        async for chunk_str in _call_llm_stream(
            llm_messages, api_key, config["base_url"], model_name,
            max_tokens, temperature, tools,
        ):
            if chunk_str == "[DONE]":
                break
            try:
                chunk = json.loads(chunk_str)
            except json.JSONDecodeError:
                continue

            delta = chunk.get("choices", [{}])[0].get("delta", {})

            # Content delta
            if delta.get("content"):
                collected_content += delta["content"]
                yield json.dumps({"type": "content", "content": delta["content"]}, ensure_ascii=False)

            # Tool call delta
            if delta.get("tool_calls"):
                has_tool_calls = True
                for tc in delta["tool_calls"]:
                    idx = tc.get("index", 0)
                    while len(collected_tool_calls) <= idx:
                        collected_tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                    if tc.get("id"):
                        collected_tool_calls[idx]["id"] = tc["id"]
                    if tc.get("function", {}).get("name"):
                        collected_tool_calls[idx]["function"]["name"] += tc["function"]["name"]
                    if tc.get("function", {}).get("arguments"):
                        collected_tool_calls[idx]["function"]["arguments"] += tc["function"]["arguments"]

        if not has_tool_calls:
            # No more tool calls, we're done
            yield json.dumps({"type": "done"}, ensure_ascii=False)
            return

        # Execute tool calls
        llm_messages.append({
            "role": "assistant",
            "content": collected_content,
            "tool_calls": collected_tool_calls,
        })

        for tc in collected_tool_calls:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                fn_args = {}

            yield json.dumps({"type": "tool_call", "name": fn_name, "arguments": fn_args}, ensure_ascii=False)

            async with SessionLocal() as db:
                result = await execute_tool(fn_name, fn_args, db, user_permissions, user)

            yield json.dumps({"type": "tool_result", "name": fn_name, "result": json.loads(result)}, ensure_ascii=False)

            llm_messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

        # Continue loop for next round (LLM will summarize tool results)

    yield json.dumps({"type": "done"}, ensure_ascii=False)
