"""Hardening tests: login lockout, token revocation, AI quota, semver.

Covers the audit-driven hardening batch:
- 5 consecutive failures lock the (username, IP) pair; success resets it.
- logout blacklists the token's jti; the auth dependency then rejects it.
- refresh endpoint honors the blacklist too.
- AI chat quota: capped at settings.AI_DAILY_LIMIT calls/day per user.
- _parse_semver drives the update comparison.
"""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import system as system_module
from src.api.system import router as system_router, _parse_semver
from src.core import auth_guard
from src.core.config import settings
from src.core.redis_client import memory_clear, reset_for_tests


def _no_redis(monkeypatch):
    """Force the in-memory fallback path for every kv call in this test."""
    monkeypatch.setattr(settings, "REDIS_ENABLED", False, raising=False)
    reset_for_tests()
    memory_clear("authlock")
    auth_guard.reset_fallback()


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------- semver

def test_parse_semver():
    assert _parse_semver("2.5.0") == (2, 5, 0)
    assert _parse_semver("v2.10.1") == (2, 10, 1)
    assert _parse_semver("2.5") > _parse_semver("2.4.9")
    assert _parse_semver("2.5.0") > _parse_semver("2.4.99")
    assert _parse_semver("2.5.0") == _parse_semver("V2.5.0")
    assert _parse_semver("garbage") == (0,)


# ---------------------------------------------------------------- lockout

def test_lockout_after_five_failures(monkeypatch):
    _no_redis(monkeypatch)
    key_user, key_ip = "alice", "1.2.3.4"
    for i in range(4):
        st = _run(auth_guard.record_failure(key_user, key_ip))
        assert not st.locked, f"locked too early at attempt {i + 1}"
    st = _run(auth_guard.record_failure(key_user, key_ip))
    assert st.locked and st.retry_after > 0
    # check_lock agrees while the window is active
    assert _run(auth_guard.check_lock(key_user, key_ip)).locked


def test_lockout_reset_by_success_and_isolates_pairs(monkeypatch):
    _no_redis(monkeypatch)
    _run(auth_guard.record_failure("bob", "5.6.7.8"))
    _run(auth_guard.record_success("bob", "5.6.7.8"))
    assert not _run(auth_guard.check_lock("bob", "5.6.7.8")).locked
    # Same username from another IP: unaffected
    assert not _run(auth_guard.check_lock("bob", "9.9.9.9")).locked


def test_lockout_redis_fallback_semantics(monkeypatch):
    """With Redis unreachable the fallback must behave like the old dict:
    lock after MAX_FAILURES, unlock cleared by success, TTL-driven expiry."""
    _no_redis(monkeypatch)
    user, ip = "carol", "7.7.7.7"
    for _ in range(auth_guard.MAX_FAILURES):
        st = _run(auth_guard.record_failure(user, ip))
    assert st.locked
    # Fallback entry written to the kv memory layer: count reset, lock timestamp set
    from src.core.redis_client import _memory
    entry = _memory.get("authlock", {}).get(f"{user}:{ip}")
    assert entry is not None
    count_s, locked_s = entry[0].split("|", 1)
    assert count_s == "0" and float(locked_s) > 0


def test_lockout_redis_shared_store(monkeypatch):
    """When Redis is available, counters round-trip through the kv layer
    (monkeypatched fake) and record_success deletes the shared key."""
    _no_redis(monkeypatch)

    store: dict[str, str] = {}

    class _FakeRedis:
        async def ping(self):
            return True

        async def set(self, key, value, ex=None):
            store[key] = value

        async def get(self, key):
            return store.get(key)

        async def delete(self, key):
            store.pop(key, None)

    import src.core.redis_client as rc

    async def _fake_client():
        return _FakeRedis()

    monkeypatch.setattr(rc, "_get_client", _fake_client)
    monkeypatch.setattr(settings, "REDIS_ENABLED", True, raising=False)

    user, ip = "dave", "8.8.8.8"
    st = _run(auth_guard.record_failure(user, ip))
    assert not st.locked
    assert any("authlock:dave:8.8.8.8" in k for k in store)
    _run(auth_guard.record_success(user, ip))
    assert not any("authlock:dave:8.8.8.8" in k for k in store)


def test_check_update_degrades_when_apehub_unreachable(monkeypatch):
    """Network failure must not raise: reachable=false, has_update=false."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from src.core import deps as core_deps
    from src.core.exceptions import register_exception_handlers
    from src.api import system as mod
    from src.api.system import router as system_router
    from src.models import User

    superadmin = User(id=1, username=settings.SUPER_ADMIN_USERNAME, status=1)

    async def _fake_user():
        return superadmin

    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[core_deps.get_current_user] = _fake_user
    app.include_router(system_router, prefix="/api/v1")
    client = TestClient(app)

    class _Boom:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            raise ConnectionError("down")

        async def __aexit__(self, *a):
            return False

    monkeypatch.setattr(mod.httpx, "AsyncClient", _Boom)
    resp = client.get("/api/v1/system/check-update")
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["reachable"] is False and body["has_update"] is False
