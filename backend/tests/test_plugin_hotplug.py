import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI

from src.mcp import mcp_manager
from src.plugins.base import event_bus
from src.plugins.manager import PluginManager


@pytest.fixture(autouse=True)
def reset_global_resources():
    mcp_manager._tools.clear()
    event_bus._handlers.clear()
    yield
    mcp_manager._tools.clear()
    event_bus._handlers.clear()


@pytest.mark.asyncio
async def test_enable_disable_reenable_tracks_and_removes_resources():
    app = FastAPI()
    manager = PluginManager()
    manager._discover_one("example")

    enabled = await manager.enable_plugin("example", app)
    assert enabled["status"] == "active"
    assert enabled["routes_registered"] == 1
    assert mcp_manager.get_tool("example_hello") is not None

    disabled = await manager.disable_plugin("example", app)
    assert disabled["routes_removed"] == 1
    assert disabled["mcp_tools_removed"] == 1
    assert disabled["events_unsubscribed"] == 1
    assert mcp_manager.get_tool("example_hello") is None

    enabled_again = await manager.enable_plugin("example", app)
    assert enabled_again["status"] == "active"
    assert enabled_again["routes_registered"] == 1
    await manager.disable_plugin("example", app)


def test_plugin_zip_rejects_unsafe_name_and_supports_single_root():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        valid_zip = root / "valid.zip"
        with zipfile.ZipFile(valid_zip, "w") as archive:
            archive.writestr("bundle/plugin.json", '{"name":"demo","display_name":"Demo","version":"1"}')
            archive.writestr("bundle/demo/__init__.py", "")

        manager = PluginManager()
        manager._builtin_dir = root / "builtin"
        manager.import_plugin(valid_zip)
        assert (root / "builtin" / "demo" / "__init__.py").exists()

        unsafe_zip = root / "unsafe.zip"
        with zipfile.ZipFile(unsafe_zip, "w") as archive:
            archive.writestr("plugin.json", '{"name":"../bad","display_name":"Bad","version":"1"}')
            archive.writestr("../outside.txt", "blocked")

        with pytest.raises(ValueError):
            manager._validate_plugin_zip(unsafe_zip)
