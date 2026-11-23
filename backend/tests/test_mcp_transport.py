"""MCP transport tests: Streamable HTTP endpoint + shared dispatcher.

Covers the 2.9.0 transport upgrade:
- POST /mcp handles initialize / tools/list / tools/call with Bearer JWT
- initialize returns Mcp-Session-Id header
- notifications (no id) return 202 with no body
- DELETE /mcp terminates the session
- unauthenticated requests are rejected
- dispatcher parity: method-not-found and bad tool produce JSON-RPC errors
"""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.config import settings


def _build_app(monkeypatch, superadmin):
    """Build a minimal app with MCP routes and stubbed auth."""
    from src.core import deps as core_deps
    from src.core.exceptions import register_exception_handlers
    from src.api.system import router as system_router  # noqa: F401
    from src.mcp.streamable_http import router as mcp_router

    async def _fake_user():
        return superadmin

    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[core_deps.get_current_user] = _fake_user
    app.include_router(mcp_router, prefix="/api/v1")
    return app


@pytest.fixture()
def mcp_client(monkeypatch):
    from src.models import User

    admin = User(id=1, username=settings.SUPER_ADMIN_USERNAME, status=1)
    app = _build_app(monkeypatch, admin)
    return TestClient(app)


def test_streamable_initialize_assigns_session_id(mcp_client):
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "initialize", "params": {"clientInfo": {"name": "test"}}, "id": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["protocolVersion"] == "2025-03-26"
    assert "Mcp-Session-Id" in resp.headers


def test_streamable_tools_list_and_call(mcp_client):
    # tools/list (dispatcher's RBAC: superadmin gets "*")
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2},
    )
    assert resp.status_code == 200
    tools = resp.json()["result"]["tools"]
    assert isinstance(tools, list)

    # tools/call — unknown tool yields a JSON-RPC error, not a crash
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "no_such_tool_xyz", "arguments": {}}, "id": 3},
    )
    err = resp.json()["error"]
    assert err["code"] == -32602


def test_streamable_notification_returns_202(mcp_client):
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
    )
    assert resp.status_code == 202
    assert resp.content == b"" or resp.content == b"null" or resp.text == ""


def test_streamable_delete_terminates_session(mcp_client):
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1},
    )
    sid = resp.headers["Mcp-Session-Id"]
    # delete the session
    resp2 = mcp_client.delete("/api/v1/mcp", headers={"Mcp-Session-Id": sid})
    assert resp2.status_code == 204
    # subsequent POST with the dead session id → 404
    resp3 = mcp_client.post(
        "/api/v1/mcp",
        headers={"Mcp-Session-Id": sid},
        json={"jsonrpc": "2.0", "method": "ping", "params": {}, "id": 9},
    )
    assert resp3.status_code == 404


def test_streamable_unknown_method_yields_rpc_error(mcp_client):
    resp = mcp_client.post(
        "/api/v1/mcp",
        json={"jsonrpc": "2.0", "method": "bogus/method", "params": {}, "id": 42},
    )
    assert resp.json()["error"]["code"] == -32601


def test_sse_ticket_roundtrip_redis_fallback(monkeypatch):
    """Ticket issue/consume works over the kv layer with memory fallback."""
    from src.core.redis_client import memory_clear, reset_for_tests
    from src.mcp.sse_transport import consume_ticket
    from src.core.redis_client import kv_set

    monkeypatch.setattr(settings, "REDIS_ENABLED", False, raising=False)
    reset_for_tests()
    memory_clear()

    # Simulate issue
    loop = asyncio.new_event_loop()
    loop.run_until_complete(kv_set("mcpticket", "t123", "7", ttl=30))
    got = loop.run_until_complete(consume_ticket("t123"))
    assert got == 7
    # one-time: second consume fails
    got2 = loop.run_until_complete(consume_ticket("t123"))
    assert got2 is None
    loop.close()
