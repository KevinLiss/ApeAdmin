"""Hermes HTTP 代理——把 ApeAdmin 前端请求转发到 hermes dashboard 的 /api/*。

hermes dashboard 有丰富的 HTTP REST API（/api/config、/api/files、/api/skills 等），
ApeAdmin 前端无法直连（端口不同 + 需要认证），通过此代理统一转发：

  前端 → /api/v1/hermes/proxy/{path}  →  http://127.0.0.1:9119/api/{path}

代理自动附加 hermes session token（X-Hermes-Session-Token header）做认证。
支持 GET/POST/PUT/DELETE/PATCH，透传 body、query params、content-type。
文件上传（multipart）也透传。
"""

import json
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from loguru import logger

from src.core.deps import get_current_user
from src.core.exceptions import success_response
from src.plugins.builtin.hermes.plugin import get_hermes_plugin

router = APIRouter(prefix="/hermes", tags=["Hermes AI 助手"])

# 不需要 ApeAdmin 权限校验的 hermes 公开路径
_HERMES_PUBLIC_PATHS = {"status"}

# 路径重写表：hermes 侧部分路由不在 /api/ 前缀下（如 /auth/logout），
# 前端统一经 /api/v1/hermes/proxy/{path} 调用，此处映射到真实 hermes 路径。
_PATH_REWRITES = {
    "auth/logout": "auth/logout",  # 目标不走 /api 前缀，见下方 target 拼接逻辑
}


async def _proxy_to_hermes(
    path: str,
    request: Request,
    user,  # ApeAdmin 用户（已鉴权）
) -> Response:
    """核心代理：转发到 hermes dashboard HTTP API。"""
    plugin = get_hermes_plugin()
    status = plugin.get_status()
    if not status.get("running"):
        return Response(
            content=json.dumps({"detail": "hermes 引擎未启动"}),
            status_code=503,
            media_type="application/json",
        )

    port = status["port"]
    token = status["token"]
    base = f"http://127.0.0.1:{port}/api"

    # 构建目标 URL（保留 query params）
    query_string = request.url.query

    # 路径重写：无 /api 前缀的 hermes 路由
    if path in _PATH_REWRITES:
        # 相对于 hermes dashboard 根（而非 /api）的路径
        rewritten = _PATH_REWRITES[path]
        target = f"http://127.0.0.1:{port}/{rewritten}"
    else:
        target = f"{base}/{path}"

    if query_string:
        target += f"?{query_string}"

    # 构建 headers（附加 hermes 认证）
    headers = {
        "X-Hermes-Session-Token": token,
    }
    # 透传 content-type（文件上传需要 boundary）
    ct = request.headers.get("content-type")
    if ct:
        headers["content-type"] = ct

    # 读取 body
    body = await request.body()

    method = request.method

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.request(
                method,
                target,
                headers=headers,
                content=body if body else None,
            )
    except httpx.ConnectError:
        return Response(
            content=json.dumps({"detail": "hermes 网络连接失败"}),
            status_code=502,
            media_type="application/json",
        )
    except httpx.ReadTimeout:
        return Response(
            content=json.dumps({"detail": "hermes 响应超时"}),
            status_code=504,
            media_type="application/json",
        )

    # 透传响应（保留原始 content-type 和 body）
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
        headers={
            # 允许文件下载的 Content-Disposition 透传
            "Content-Disposition": resp.headers.get("content-disposition", ""),
        } if resp.headers.get("content-disposition") else None,
    )


@router.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def hermes_proxy(path: str, request: Request, user=Depends(get_current_user)):
    """通用 HTTP 代理——转发到 hermes dashboard /api/{path}。"""
    return await _proxy_to_hermes(path, request, user)
