"""Hermes 插件 REST API。

提供引擎状态、会话操作（创建/恢复/列表）的便捷接口，供前端在建立 WS
长连接前先探测状态、初始化会话。核心对话走 WS 桥接（流式），REST 只做轻量操作。
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from src.core.deps import get_current_user
from src.core.deps import require_permission as _require_perm
from src.core.exceptions import success_response
from src.models import User
from src.plugins.builtin.hermes.plugin import get_hermes_plugin

router = APIRouter(prefix="/hermes", tags=["Hermes AI 助手"])


@router.get("/status")
async def hermes_status(
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("hermes:chat"))],
):
    """查询 hermes 引擎运行状态。"""
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    return success_response(data={
        "running": status.get("running", False),
        "pid": status.get("pid"),
        "port": status.get("port"),
        "token": status.get("token", ""),
    })


@router.post("/sessions")
async def hermes_create_session(
    body: dict[str, Any],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("hermes:chat"))],
):
    """通过 hermes 网关创建一个会话（REST 便捷封装，核心流程仍走 WS）。

    请求体: {"title": str?, "model": str?, "provider": str?}
    """
    # 完整会话创建走 WS（session.create）。REST 层这里仅校验引擎在线。
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    if not status.get("running"):
        raise HTTPException(status_code=503, detail="hermes 引擎未启动")
    return success_response(data={"session_id": None, "hint": "会话通过 WS 桥接创建"})


@router.get("/ws-url")
async def hermes_ws_url(
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("hermes:chat"))],
):
    """返回 WS 桥接地址（前端用本地 ApeAdmin JWT 连接）。

    实际连接在 WS 端点完成鉴权（query 携带 ApeAdmin JWT）。
    这里仅给出 URL 路径，便于前端拼接。
    """
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    if not status.get("running"):
        raise HTTPException(status_code=503, detail="hermes 引擎未启动")
    return success_response(data={
        "ws_url": "/api/v1/hermes/ws",
    })