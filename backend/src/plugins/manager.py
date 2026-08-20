"""Plugin manager: discovery, loading, lifecycle management.

Discovery strategy:
- Scan the builtin plugins directory (src/plugins/builtin/*)
- Each plugin is a Python package with a __init__.py that exports a Plugin class
- The Plugin class must implement PluginInterface
- Plugin state (enabled/disabled/installed) is persisted in DB or config file
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from loguru import logger

from src.core.config import settings
from src.plugins.base import PluginInfo, PluginInterface, event_bus, Event


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self):
        self._plugins: dict[str, PluginInfo] = {}
        self._builtin_dir = Path(settings.PLUGINS_BUILTIN_DIR)

    @property
    def plugins(self) -> dict[str, PluginInfo]:
        return self._plugins

    def discover(self) -> None:
        """Discover all available plugins in the builtin directory."""
        if not settings.PLUGINS_ENABLED:
            logger.info("Plugins are disabled, skipping discovery")
            return

        # Import the builtin package to get its path
        try:
            builtin_pkg = importlib.import_module("src.plugins.builtin")
        except ImportError:
            logger.warning("Builtin plugins package not found")
            return

        pkg_path = Path(builtin_pkg.__path__[0])
        logger.info(f"Discovering plugins in {pkg_path}")

        for importer, modname, ispkg in pkgutil.iter_modules(builtin_pkg.__path__):
            if not ispkg:
                continue  # Plugins must be packages (directories)

            try:
                module = importlib.import_module(f"src.plugins.builtin.{modname}")
                plugin_class = self._find_plugin_class(module)
                if plugin_class is None:
                    logger.debug(f"Module {modname} has no Plugin class, skipping")
                    continue

                instance = plugin_class()
                info = PluginInfo(
                    name=instance.name or modname,
                    display_name=instance.display_name or modname,
                    description=instance.description,
                    version=instance.version,
                    author=instance.author,
                    module_path=f"src.plugins.builtin.{modname}",
                    enabled=True,  # Default: enabled (can be overridden by config)
                    instance=instance,
                )
                self._plugins[info.name] = info
                logger.info(f"Discovered plugin: {info.name} v{info.version}")

            except Exception as exc:
                logger.error(f"Failed to load plugin '{modname}': {exc}")

    def _find_plugin_class(self, module: Any) -> type[PluginInterface] | None:
        """Find the first PluginInterface subclass in a module."""
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, PluginInterface) and obj is not PluginInterface:
                return obj
        return None

    async def install_all(self) -> None:
        """Call install() on all enabled plugins."""
        for name, info in self._plugins.items():
            if not info.enabled or not info.instance:
                continue
            try:
                info.instance.on_load()
                await info.instance.install()
                info.installed = True
                logger.info(f"Plugin '{name}' installed")
            except Exception as exc:
                logger.error(f"Failed to install plugin '{name}': {exc}")

    def register_all(self, app: FastAPI) -> None:
        """Register all enabled plugins' routes on the app."""
        for name, info in self._plugins.items():
            if not info.enabled or not info.instance:
                continue
            try:
                info.instance.register(app)
                logger.info(f"Plugin '{name}' routes registered")
            except Exception as exc:
                logger.error(f"Failed to register plugin '{name}': {exc}")

    async def uninstall_all(self) -> None:
        """Call uninstall() on all installed plugins (for shutdown)."""
        for name, info in self._plugins.items():
            if not info.installed or not info.instance:
                continue
            try:
                await info.instance.uninstall()
                info.instance.on_unload()
                logger.info(f"Plugin '{name}' uninstalled")
            except Exception as exc:
                logger.error(f"Failed to uninstall plugin '{name}': {exc}")

    def get_plugin(self, name: str) -> PluginInfo | None:
        """Get info about a specific plugin."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginInfo]:
        """List all discovered plugins."""
        return list(self._plugins.values())


# Global plugin manager
plugin_manager = PluginManager()
