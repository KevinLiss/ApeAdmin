"""Integration tests for the deploy-package update flow (system.py).

Covers the gaps found when auditing "版本更新" end-to-end:
- ZIP deploy packages (ApeHub releases are ZIP-only) are accepted and
  produce the same overwrite result as .tar.gz.
- Plugin / Go-binary packages are rejected with an actionable message.
- tar.gz archives containing symlinks are rejected (path-smuggling).
- A failing ``pip install`` rolls back every replaced path so the
  on-disk code matches the still-running old process.
- Success response carries ``data.message`` (the axios interceptor
  unwraps the envelope, so the UI can only read fields inside data).
"""

import io
import os
import tarfile
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import system as system_module
from src.api.system import router as system_router
from src.core.config import settings
from src.models import User


# ---------------------------------------------------------------- helpers

def _make_fake_project(root: Path) -> None:
    """A minimal deploy-root layout the update endpoint operates on."""
    (root / "src" / "core").mkdir(parents=True)
    (root / "src" / "main.py").write_text("old = 1\n")
    (root / "src" / "core" / "config.py").write_text("old = 1\n")
    # An install-only plugin (imported after deployment, not part of the
    # open-source package) — a version update must NOT wipe it.
    (root / "src" / "plugins" / "builtin" / "myplug").mkdir(parents=True)
    (root / "src" / "plugins" / "builtin" / "myplug" / "__init__.py").write_text("plugin = 1\n")
    (root / "frontend_dist").mkdir()
    (root / "frontend_dist" / "index.html").write_text("<html>old</html>")
    (root / "requirements.txt").write_text("fastapi==0.1.0\n")
    (root / ".env").write_text("DB_TYPE=sqlite\n")


def _zip_deploy(root: Path, mark: str) -> bytes:
    """A valid deploy package as ZIP with a top-level dir."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("apeadmin/src/main.py", f"new = '{mark}'\n")
        z.writestr("apeadmin/frontend_dist/index.html", f"<html>{mark}</html>")
        z.writestr("apeadmin/requirements.txt", "fastapi==9.9.9\n")
    return buf.getvalue()


def _tar_deploy(root: Path, mark: str) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        data = f"new = '{mark}'\n".encode()
        info = tarfile.TarInfo("apeadmin/src/main.py")
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def _zip_plugin() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("myplug/plugin.json", '{"name":"myplug","version":"1.0"}')
        z.writestr("myplug/__init__.py", "x\n")
    return buf.getvalue()


def _tar_with_symlink() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        link = tarfile.TarInfo("apeadmin/src/evil")
        link.type = tarfile.SYMTYPE
        link.linkname = "/etc/passwd"
        t.addfile(link)
    return buf.getvalue()


@pytest.fixture
def fake_env(tmp_path, monkeypatch):
    """Fake deploy root + API client with a super-admin user."""
    project_root = tmp_path / "deploy"
    project_root.mkdir()
    _make_fake_project(project_root)

    monkeypatch.setattr(system_module, "_project_root", lambda: project_root)

    from src.core import deps as core_deps

    superadmin = User(id=1, username=settings.SUPER_ADMIN_USERNAME, status=1)

    async def _fake_get_current_user():
        return superadmin

    app = FastAPI()
    # Same global handlers as the real app (422 envelope for
    # ValidationException, etc.) — without them a raised ValidationException
    # becomes a 500 in the bare test app.
    from src.core.exceptions import register_exception_handlers
    register_exception_handlers(app)
    # require_permission(...) is baked in at route definition time; override
    # the leaf dependency it ultimately resolves the user through.
    app.dependency_overrides[core_deps.get_current_user] = _fake_get_current_user
    app.include_router(system_router, prefix="/api/v1")

    yield {
        "client": TestClient(app, raise_server_exceptions=False),
        "root": project_root,
        "user": superadmin,
    }


def _upload(client: TestClient, filename: str, payload: bytes):
    return client.post(
        "/api/v1/system/update",
        files={"file": (filename, payload)},
    )


# ---------------------------------------------------------------- tests

def test_version_endpoint_reports_runtime(fake_env):
    client = fake_env["client"]
    resp = client.get("/api/v1/system/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["runtime"] == "python"
    assert body["data"]["current_version"] == settings.APP_VERSION


def test_zip_deploy_accepted_and_applied(fake_env, monkeypatch):
    """ZIP packages (ApeHub format) go through the full update flow."""
    client, root = fake_env["client"], fake_env["root"]

    # Mock pip: succeed instantly without touching the environment.
    class _Proc:
        returncode = 0

        async def communicate(self):
            return (b"", b"")

    async def _fake_pip(*args, **kwargs):
        return _Proc()

    monkeypatch.setattr(system_module.asyncio, "create_subprocess_exec", _fake_pip)

    # Mock the restart spawner (no real process, no self-exit).
    async def _fake_restart(project_root, python_bin):
        return {"mode": "test", "log": None, "spawner_pid": 0}

    monkeypatch.setattr("src.core.runtime.spawn_restart", _fake_restart)

    resp = _upload(client, "apeadmin-base-2.4.0.zip", _zip_deploy(root, "zipmark"))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["code"] == 200
    # data.message must exist: the axios interceptor only exposes data.
    assert "message" in body["data"] and body["data"]["message"]
    assert body["data"]["restart_mode"] == "test"

    # New code actually landed on disk.
    assert "zipmark" in (root / "src" / "main.py").read_text()
    assert "zipmark" in (root / "frontend_dist" / "index.html").read_text()
    assert "fastapi==9.9.9" in (root / "requirements.txt").read_text()

    # Install-only plugin survived the full src/ replace.
    assert (root / "src" / "plugins" / "builtin" / "myplug" / "__init__.py").read_text() == "plugin = 1\n"


def test_install_only_plugin_survives_tar_update(fake_env, monkeypatch):
    """Same guarantee for the traditional .tar.gz path."""

    class _Proc:
        returncode = 0

        async def communicate(self):
            return (b"", b"")

    async def _fake_pip(*args, **kwargs):
        return _Proc()

    async def _fake_restart(project_root, python_bin):
        return {"mode": "test", "log": None, "spawner_pid": 0}

    monkeypatch.setattr(system_module.asyncio, "create_subprocess_exec", _fake_pip)
    monkeypatch.setattr("src.core.runtime.spawn_restart", _fake_restart)

    client, root = fake_env["client"], fake_env["root"]
    resp = _upload(client, "apeadmin-base.tar.gz", _tar_deploy(root, "plugmark"))
    assert resp.status_code == 200, resp.text
    assert "plugmark" in (root / "src" / "main.py").read_text()
    assert (root / "src" / "plugins" / "builtin" / "myplug" / "__init__.py").exists()


def test_flat_zip_without_topdir_accepted(fake_env, monkeypatch):
    """ZIP archives whose members sit at the root (no apeadmin/ dir)."""
    client, root = fake_env["client"], fake_env["root"]

    class _Proc:
        returncode = 0

        async def communicate(self):
            return (b"", b"")

    async def _fake_pip(*args, **kwargs):
        return _Proc()

    async def _fake_restart(project_root, python_bin):
        return {"mode": "test", "log": None, "spawner_pid": 0}

    monkeypatch.setattr(system_module.asyncio, "create_subprocess_exec", _fake_pip)
    monkeypatch.setattr("src.core.runtime.spawn_restart", _fake_restart)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("src/main.py", "flat = 1\n")
        z.writestr("frontend_dist/index.html", "<html>flat</html>")

    resp = _upload(client, "apeadmin-flat.zip", buf.getvalue())
    assert resp.status_code == 200, resp.text
    assert "flat = 1" in (root / "src" / "main.py").read_text()


def test_zip_plugin_package_rejected(fake_env):
    resp = _upload(fake_env["client"], "plugin.zip", _zip_plugin())
    assert resp.status_code == 422
    msg = resp.json()["msg"]
    assert "插件包" in msg and "升级包" in msg


def test_tar_with_symlink_rejected(fake_env):
    resp = _upload(fake_env["client"], "evil.tar.gz", _tar_with_symlink())
    assert resp.status_code == 422
    assert "符号链接" in resp.json()["msg"] or "symlink" in resp.json()["msg"]


def test_tar_deploy_still_accepted(fake_env, monkeypatch):
    """Regression: traditional .tar.gz keeps working."""

    class _Proc:
        returncode = 0

        async def communicate(self):
            return (b"", b"")

    async def _fake_pip(*args, **kwargs):
        return _Proc()

    async def _fake_restart(project_root, python_bin):
        return {"mode": "test", "log": None, "spawner_pid": 0}

    monkeypatch.setattr(system_module.asyncio, "create_subprocess_exec", _fake_pip)
    monkeypatch.setattr("src.core.runtime.spawn_restart", _fake_restart)

    client, root = fake_env["client"], fake_env["root"]
    resp = _upload(client, "apeadmin-base.tar.gz", _tar_deploy(root, "tarmark"))
    assert resp.status_code == 200, resp.text
    assert "tarmark" in (root / "src" / "main.py").read_text()


def test_pip_failure_rolls_back(fake_env, monkeypatch):
    """When pip fails, every replaced path must be restored from backup."""

    class _Proc:
        returncode = 1

        async def communicate(self):
            return (b"", b"ERROR: no matching distribution")

    async def _fake_pip(*args, **kwargs):
        return _Proc()

    async def _fake_restart(project_root, python_bin):  # pragma: no cover
        raise AssertionError("must not restart after rollback")

    monkeypatch.setattr(system_module.asyncio, "create_subprocess_exec", _fake_pip)
    monkeypatch.setattr("src.core.runtime.spawn_restart", _fake_restart)

    client, root = fake_env["client"], fake_env["root"]
    old_main = (root / "src" / "main.py").read_text()
    old_index = (root / "frontend_dist" / "index.html").read_text()
    old_req = (root / "requirements.txt").read_text()

    resp = _upload(client, "apeadmin-base-2.4.0.zip", _zip_deploy(root, "broken"))
    assert resp.status_code == 422
    assert "回滚" in resp.json()["msg"]

    # On-disk state matches the still-running old process again.
    assert (root / "src" / "main.py").read_text() == old_main
    assert (root / "frontend_dist" / "index.html").read_text() == old_index
    assert (root / "requirements.txt").read_text() == old_req
