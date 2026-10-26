"""In-place plugin upgrade tests (插件二次更新).

Covers the upgrade flow of ``install_plugin_from_zip``:
- Upgrading an ACTIVE plugin swaps versions without a manual disable
  step; the plugin ends up active on the new version, menus restored.
- Downgrades are rejected (allow_downgrade opt-out exists).
- Same-version re-install is allowed (repair scenario).
- A failing install() rolls back: previous files restored, previous
  runtime registration re-activated, error is actionable.
- Version backups are stashed for manual rollback (latest 2 kept).

``_discover_one`` is faked: real discovery needs importlib to import the
package, which the sandbox tests cannot do. The fake reads the version
from the extracted plugin.json on disk and returns a plugin double.
"""

import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI

from src.plugins.base import PluginInfo
from src.plugins.manager import PluginManager


# ---------------------------------------------------------------- doubles

class _DummyPlugin:
    """Configurable plugin double: version + optional install failure."""

    name = "upgplug"
    display_name = "升级测试插件"
    description = "plugin double for upgrade tests"
    version = "1.0.0"
    author = "test"

    def __init__(self, version: str = "1.0.0", fail: bool = False):
        self.version = version
        self.fail = fail

    async def install(self):
        if self.fail:
            raise RuntimeError("migration exploded")

    async def uninstall(self):
        pass

    def on_load(self):
        pass

    def on_unload(self):
        pass

    def register(self, app):
        pass

    def register_mcp_tools(self):
        pass


def _make_manager(tmp_path: Path) -> PluginManager:
    manager = PluginManager()
    manager._builtin_dir = tmp_path / "builtin"
    manager._builtin_dir.mkdir(parents=True, exist_ok=True)
    return manager


def _make_fake_discover(manager: PluginManager, fail_versions: set[str] | None = None):
    fail_versions = fail_versions or set()

    def fake_discover(name: str) -> PluginInfo:
        manifest = json.loads((manager._builtin_dir / name / "plugin.json").read_text())
        version = str(manifest.get("version", "0.0.0"))
        info = PluginInfo(
            name=name,
            display_name=manifest.get("display_name", name),
            description=manifest.get("description", ""),
            version=version,
            author=manifest.get("author", ""),
            module_path=f"src.plugins.builtin.{name}",
            enabled=False,
            instance=_DummyPlugin(version=version, fail=version in fail_versions),
            dependencies=[],
        )
        manager._plugins[name] = info
        return info

    return fake_discover


def _patch_lifecycle(monkeypatch, manager: PluginManager, registered: list | None = None):
    """Stub out runtime registration/menus/persistence for sandboxed tests."""

    def fake_register(name, info, application):
        if registered is not None:
            registered.append(info.version)
        return {"routes": 0, "mcp_tools": 0, "events": 0}

    async def fake_menus(*a, **k):
        return 0

    async def fake_persist(*a, **k):
        return True

    monkeypatch.setattr(manager, "_register_runtime", fake_register)
    monkeypatch.setattr(manager, "_set_plugin_menus_enabled", fake_menus)
    monkeypatch.setattr(manager, "_persist_enabled", fake_persist)


def _zip_bytes(version: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        # Standard bundle layout: single root dir wrapping plugin.json and
        # the plugin package directory (name must match manifest.name).
        z.writestr(
            "bundle/plugin.json",
            json.dumps({
                "name": "upgplug",
                "display_name": "升级测试插件",
                "version": version,
                "author": "test",
                "description": "double",
            }),
        )
        z.writestr("bundle/upgplug/__init__.py", "")
        z.writestr("bundle/upgplug/plugin.py", f"# v{version}\n")
        z.writestr("bundle/upgplug/manifest.flag", f"v{version}")
    return buf.getvalue()


def _write_zip(tmp_path: Path, version: str) -> Path:
    path = tmp_path / f"upgplug-{version}.zip"
    path.write_bytes(_zip_bytes(version))
    return path


def _manifest_version(manager: PluginManager) -> str:
    return json.loads(
        (manager._builtin_dir / "upgplug" / "plugin.json").read_text()
    )["version"]


# ---------------------------------------------------------------- tests

@pytest.mark.asyncio
async def test_upgrade_active_plugin_in_place(tmp_path, monkeypatch):
    """An ACTIVE plugin upgrades in one step: no manual disable required."""
    app = FastAPI()
    manager = _make_manager(tmp_path)
    registered: list[str] = []
    _patch_lifecycle(monkeypatch, manager, registered)
    manager._discover_one = _make_fake_discover(manager)

    # Fresh install v1.0.0
    result = await manager.install_plugin_from_zip(_write_zip(tmp_path, "1.0.0"), app)
    assert result["status"] == "active"
    assert result.get("upgraded") is None  # fresh install, not an upgrade

    # Upgrade to 1.1.0 while ACTIVE — the core secondary-update scenario.
    result2 = await manager.install_plugin_from_zip(_write_zip(tmp_path, "1.1.0"), app)
    assert result2["upgraded"] is True
    assert result2["from_version"] == "1.0.0"
    assert result2["version"] == "1.1.0"
    assert result2["status"] == "active"
    assert _manifest_version(manager) == "1.1.0"
    # Both install and upgrade (re)registered the runtime.
    assert registered == ["1.0.0", "1.1.0"]

    # Same-version re-install (repair) is allowed and not flagged as upgrade.
    result3 = await manager.install_plugin_from_zip(_write_zip(tmp_path, "1.1.0"), app)
    assert "upgraded" not in result3  # repair, not a version transition
    assert result3["version"] == "1.1.0"


@pytest.mark.asyncio
async def test_downgrade_rejected(tmp_path, monkeypatch):
    app = FastAPI()
    manager = _make_manager(tmp_path)
    _patch_lifecycle(monkeypatch, manager)
    manager._discover_one = _make_fake_discover(manager)

    await manager.install_plugin_from_zip(_write_zip(tmp_path, "2.0.0"), app)
    lower = _write_zip(tmp_path, "1.0.0")

    with pytest.raises(ValueError, match="低于当前版本"):
        await manager.install_plugin_from_zip(lower, app)
    # Current version untouched by the rejected attempt.
    assert _manifest_version(manager) == "2.0.0"

    # allow_downgrade bypasses the guard.
    result = await manager.install_plugin_from_zip(lower, app, allow_downgrade=True)
    assert result["version"] == "1.0.0"
    assert result["upgraded"] is True  # still a version transition


@pytest.mark.asyncio
async def test_failed_install_rolls_back_and_reactivates(tmp_path, monkeypatch):
    """install() failure restores previous files + re-registers the old version."""
    app = FastAPI()
    manager = _make_manager(tmp_path)
    registered: list[str] = []
    _patch_lifecycle(monkeypatch, manager, registered)
    manager._discover_one = _make_fake_discover(manager, fail_versions={"1.2.0"})

    # Active v1.0.0 on disk.
    await manager.install_plugin_from_zip(_write_zip(tmp_path, "1.0.0"), app)

    # Upgrade to the failing 1.2.0.
    with pytest.raises(ValueError, match="安装失败"):
        await manager.install_plugin_from_zip(_write_zip(tmp_path, "1.2.0"), app)

    # Old version files restored; plugin re-registered and active again.
    assert _manifest_version(manager) == "1.0.0"
    assert manager._plugins["upgplug"].runtime_state == "active"
    assert registered == ["1.0.0", "1.0.0"], "old version must be re-registered after rollback"


@pytest.mark.asyncio
async def test_version_backup_stashed_with_retention(tmp_path, monkeypatch):
    app = FastAPI()
    manager = _make_manager(tmp_path)
    _patch_lifecycle(monkeypatch, manager)
    manager._discover_one = _make_fake_discover(manager)

    for version in ("1.0.0", "1.1.0", "1.2.0"):
        await manager.install_plugin_from_zip(_write_zip(tmp_path, version), app)

    backups_root = manager._builtin_dir.parent / "_backups" / "upgplug"
    kept = {p.name.split("-")[0] for p in backups_root.iterdir()}
    # Retention keeps the newest 2 pre-upgrade versions; the currently live
    # version itself is never in the stash.
    assert len(kept) <= 2
    assert "1.2.0" not in kept
    assert kept == {"1.0.0", "1.1.0"}
