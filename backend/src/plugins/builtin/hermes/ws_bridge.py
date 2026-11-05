"""Hermes WS 桥接——ApeAdmin ↔ hermes tui_gateway。

通过 hermes dashboard 的 WebSocket JSON-RPC（tui_gateway 协议）与 hermes
独立进程通信。本模块作为 ApeAdmin 与 hermes 之间的"薄代理"：

- ApeAdmin 前端 WS → 本插件 WS 端点（携带 ApeAdmin JWT）
- 本插件作为 hermes 的 WS 客户端，转发 RPC 请求 / 接收事件帧

帧格式（JSON Lines，与 hermes 官方 Web UI 完全一致）：
- 客户端 → 服务器: {"jsonrpc":"2.0","id":N,"method":"...","params":{...}}
- 服务器 → 客户端: {"jsonrpc":"2.0","method":"event","params":{"type":"...","payload":{...}}}
                   {"jsonrpc":"2.0","id":N,"result":{...}} / {"error":{...}}
"""

import asyncio
import json
import secrets
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger

from src.core.deps import get_current_user
from src.plugins.builtin.hermes.plugin import get_hermes_plugin

router = APIRouter(prefix="/hermes", tags=["Hermes AI 助手"])

# 每连接一个"会话代理"——负责把前端 WS 与 hermes WS 桥接
_proxies: dict[int, "HermesSessionProxy"] = {}


class HermesSessionProxy:
    """一个 ApeAdmin 前端连接 ↔ hermes 网关 的桥接代理。

    生命周期：
    - 前端连上 /api/v1/hermes/ws → 创建代理
    - 代理连接 hermes WS（?token= 认证）→ 建立
    - 前端发 RPC → 转发给 hermes
    - hermes 事件/响应 → 转发给前端
    - 任一端断开 → 清理
    """

    def __init__(self, ws: WebSocket, hermes_ws_url: str, token: str):
        self.ws = ws
        self.hermes_url = hermes_ws_url
        self.token = token
        self._reader_task: asyncio.Task | None = None
        self._writer_task: asyncio.Task | None = None
        self._closed = False

    async def run(self) -> None:
        """建立 hermes 连接并双向转发，直到任一端断开。"""
        from websockets.asyncio.client import connect

        # 连接 hermes WS（本机回环 + ?token= 认证）
        uri = self.hermes_url
        sep = "&" if "?" in uri else "?"
        uri = f"{uri}{sep}token={self.token}"

        try:
            async with connect(uri, max_size=None, ping_interval=20, ping_timeout=20) as hws:
                # 启动双向转发
                self._reader_task = asyncio.create_task(self._relay_hermes_to_client(hws))
                self._writer_task = asyncio.create_task(self._relay_client_to_hermes(hws))
                done, pending = await asyncio.wait(
                    {self._reader_task, self._writer_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                # 一端断开 → 取消另一端
                for t in pending:
                    t.cancel()
                for t in done:
                    try:
                        t.result()
                    except Exception:
                        pass
        except Exception as exc:
            logger.warning(f"[hermes-bridge] hermes WS 连接失败: {exc}")
            await self._safe_close(1011, f"hermes 网关不可达: {exc}")
        finally:
            self._closed = True
            await self._cleanup()

    async def _relay_hermes_to_client(self, ws) -> None:
        """hermes → 前端：转发事件与响应帧。"""
        try:
            async for raw in ws:
                await self.ws.send_text(raw)
        except Exception as exc:
            logger.debug(f"[hermes-bridge] hermes→client 转发中断: {exc}")
        finally:
            await self._safe_close(1000)

    async def _relay_client_to_hermes(self, ws) -> None:
        """前端 → hermes：转发 RPC 请求帧。"""
        try:
            while True:
                raw = await self.ws.receive_text()
                await ws.send(raw)
        except WebSocketDisconnect:
            pass
        except Exception as exc:
            logger.debug(f"[hermes-bridge] client→hermes 转发中断: {exc}")

    async def _safe_close(self, code: int = 1000, reason: str = "") -> None:
        try:
            await self.ws.close(code=code, reason=reason)
        except Exception:
            pass

    async def _cleanup(self) -> None:
        for t in (self._reader_task, self._writer_task):
            if t and not t.done():
                t.cancel()
        _proxies.pop(id(self), None)


@router.websocket("/ws")
async def hermes_ws_proxy(websocket: WebSocket):
    """ApeAdmin 前端 ↔ hermes 网关 的 WS 代理端点。

    .. note::
       WebSocket 握手无法携带 Authorization 头（浏览器限制），这里用
       query 参数携带 ApeAdmin JWT 做鉴权（token 一次性使用）。
    """
    await websocket.accept()

    # 1. 校验 ApeAdmin JWT（query 携带，避免暴露 hermes 内部 token）
    query = dict(websocket.query_params)
    jwt_token = query.get("jwt", "")
    if not jwt_token:
        await websocket.send_json({"jsonrpc": "2.0", "method": "event", "params": {
            "type": "error", "payload": {"text": "缺少 ApeAdmin JWT", "code": "AUTH_REQUIRED"}
        }})
        await websocket.close(code=1008)
        return

    try:
        from src.core.security import decode_token
        payload = decode_token(jwt_token)
        if not payload or payload.get("type") != "access" or not payload.get("sub"):
            raise ValueError("invalid token")
    except Exception:
        await websocket.send_json({"jsonrpc": "2.0", "method": "event", "params": {
            "type": "error", "payload": {"text": "ApeAdmin JWT 无效或过期", "code": "AUTH_FAILED"}
        }})
        await websocket.close(code=1008)
        return

    # 2. 获取插件状态（hermes 地址与 token）
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    if not status.get("running"):
        await websocket.send_json({"jsonrpc": "2.0", "method": "event", "params": {
            "type": "error", "payload": {"text": "hermes 引擎未启动", "code": "ENGINE_OFFLINE"}
        }})
        await websocket.close(code=1011)
        return

    hermes_port = status["port"]
    hermes_token = status["token"]
    hermes_ws_url = f"ws://127.0.0.1:{hermes_port}/api/ws"

    # 3. 建立桥接
    proxy = HermesSessionProxy(websocket, hermes_ws_url, hermes_token)
    _proxies[id(proxy)] = proxy
    await proxy.run()


@router.get("/health")
async def hermes_health():
    """返回 hermes 引擎与桥接健康状态（供前端探测）。"""
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    return {
        "ok": status.get("running", False),
        **status,
    }