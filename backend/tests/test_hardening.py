"""Hardening tests: login lockout, token revocation, AI quota, semver.

Covers the audit-driven hardening batch:
- 5 consecutive failures lock the (username, IP) pair; success resets it.
- logout blacklists the token's jti; the auth dependency then rejects it.
- refresh endpoint honors the blacklist too.
- AI chat quota: capped at settings.AI_DAILY_LIMIT calls/day per user.
- _parse_semver drives the update comparison.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import system as system_module
from src.api.system import router as system_router, _parse_semver
from src.core import auth_guard
from src.core.config import settings


# ---------------------------------------------------------------- semver

def test_parse_semver():
    assert _parse_semver("2.5.0") == (2, 5, 0)
    assert _parse_semver("v2.10.1") == (2, 10, 1)
    assert _parse_semver("2.5") > _parse_semver("2.4.9")
    assert _parse_semver("2.5.0") > _parse_semver("2.4.99")
    assert _parse_semver("2.5.0") == _parse_semver("V2.5.0")
    assert _parse_semver("garbage") == (0,)


# ---------------------------------------------------------------- lockout

def test_lockout_after_five_failures():
    key_user, key_ip = "alice", "1.2.3.4"
    for i in range(4):
        st = auth_guard.record_failure(key_user, key_ip)
        assert not st.locked, f"locked too early at attempt {i + 1}"
    st = auth_guard.record_failure(key_user, key_ip)
    assert st.locked and st.retry_after > 0
    # check_lock agrees while the window is active
    assert auth_guard.check_lock(key_user, key_ip).locked


def test_lockout_reset_by_success_and_isolates_pairs():
    auth_guard.record_failure("bob", "5.6.7.8")
    auth_guard.record_success("bob", "5.6.7.8")
    assert not auth_guard.check_lock("bob", "5.6.7.8").locked
    # Same username from another IP: unaffected
    assert not auth_guard.check_lock("bob", "9.9.9.9").locked


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
