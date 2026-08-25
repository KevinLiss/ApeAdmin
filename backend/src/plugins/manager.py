"""Plugin manager: discovery, loading, lifecycle management.

Discovery strategy:
- Scan the builtin plugins directory (src/plugins/builtin/*)
- Each plugin is a Python package with a __init__.py that exports a Plugin class
- The Plugin class must implement PluginInterface
- Plugin state (enabled/disabled/installed) is persisted in DB or config file
"""

import importlib
import inspect
import json
import os
import pkgutil
import shutil
import zipfile
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
        """Discover all available plugins in the builtin directory.

        After scanning, sync plugin metadata to the ``sys_plugin`` DB table
        via :meth:`discover_async` (which must be called separately because
        the DB session is async).  This method only loads plugin classes
        into memory; the ``enabled`` flag is read from DB in
        :meth:`discover_async`.
        """
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
                    enabled=True,  # Default: enabled, overridden by DB in discover_async
                    instance=instance,
                )
                self._plugins[info.name] = info
                logger.info(f"Discovered plugin: {info.name} v{info.version}")

            except Exception as exc:
                logger.error(f"Failed to load plugin '{modname}': {exc}")

    async def discover_async(self) -> None:
        """Sync discovered plugins to DB and read enabled state.

        Call this after :meth:`discover` and after the DB is ready.
        - For each in-memory plugin, upsert its metadata into sys_plugin.
        - Override ``enabled`` from the DB value (so admin toggles persist).
        """
        if not self._plugins:
            return

        from src.crud.plugin import crud_plugin
        from src.db import SessionLocal

        async with SessionLocal() as db:
            for name, info in self._plugins.items():
                record = await crud_plugin.upsert(db, name, {
                    "display_name": info.display_name,
                    "description": info.description,
                    "version": info.version,
                    "author": info.author,
                    "module_path": info.module_path,
                })
                # Read enabled state from DB
                info.enabled = record.enabled

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

    # ------------------------------------------------------------------
    # Plugin package import (upload .zip → extract → install)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_plugin_zip(zip_path: Path) -> dict[str, Any]:
        """Validate a plugin .zip archive and return its manifest.

        Requirements:
        - Must contain a ``plugin.json`` at the top level
        - Must contain a Python package directory (with ``__init__.py``)
        - The package directory name must match ``plugin.json.name``
        """
        if not zip_path.exists() or not zipfile.is_zipfile(zip_path):
            raise ValueError("文件不是有效的 zip 压缩包")

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

            # Find plugin.json (at top level or inside a single root directory)
            json_candidates = [
                n for n in names
                if n.endswith("plugin.json") and n.count("/") <= 1
            ]
            if not json_candidates:
                raise ValueError("压缩包中未找到 plugin.json 清单文件")

            manifest_path = json_candidates[0]
            try:
                manifest = json.loads(zf.read(manifest_path))
            except json.JSONDecodeError:
                raise ValueError("plugin.json 格式错误，无法解析 JSON")

            # Validate required fields
            required = ("name", "display_name", "version")
            for field in required:
                if field not in manifest:
                    raise ValueError(f"plugin.json 缺少必填字段: {field}")

            plugin_name = manifest["name"]

            # Determine the root directory of the zip
            # Files are either at root or under a single top dir
            top_dirs = set()
            for n in names:
                parts = n.split("/")
                if len(parts) > 1:
                    top_dirs.add(parts[0])
            if not top_dirs:
                top_dirs = {""}  # files at root

            # Check for the plugin package directory with __init__.py
            init_found = False
            for n in names:
                if n.endswith("__init__.py") and plugin_name in n:
                    init_found = True
                    break
            if not init_found:
                raise ValueError(
                    f"压缩包中未找到插件包目录 '{plugin_name}/__init__.py'"
                )

            # Validate entry class reference
            entry = manifest.get("entry", "")
            if entry and "." not in entry:
                raise ValueError("plugin.json 的 entry 格式应为 'ModuleName.ClassName'")

            return manifest

    def import_plugin(self, zip_path: str | Path) -> dict[str, Any]:
        """Import a plugin from a .zip archive into the builtin directory.

        Steps:
        1. Validate the zip (manifest + package structure)
        2. Remove any existing plugin with the same name
        3. Extract into ``PLUGINS_BUILTIN_DIR``
        4. Return the manifest for DB upsert

        Raises ValueError on validation failures.
        """
        zip_path = Path(zip_path)
        manifest = self._validate_plugin_zip(zip_path)
        plugin_name = manifest["name"]

        builtin_dir = self._builtin_dir.resolve()
        target_dir = builtin_dir / plugin_name

        # Remove existing plugin directory if present (overwrite / upgrade)
        if target_dir.exists():
            shutil.rmtree(target_dir)
            logger.info(f"Removed existing plugin directory: {target_dir}")

        # Extract
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(builtin_dir)
        logger.info(f"Extracted plugin '{plugin_name}' to {builtin_dir}")

        # Clean up the uploaded zip
        try:
            zip_path.unlink()
        except OSError:
            pass

        # Verify the extracted package has __init__.py
        if not (target_dir / "__init__.py").exists():
            raise ValueError(
                f"解压后未找到 {plugin_name}/__init__.py，插件包结构不正确"
            )

        return manifest

    def remove_plugin_files(self, plugin_name: str) -> bool:
        """Remove a plugin's files from the builtin directory.

        Returns True if files were removed, False if the directory didn't exist.
        """
        builtin_dir = self._builtin_dir.resolve()
        target_dir = builtin_dir / plugin_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
            logger.info(f"Removed plugin files: {target_dir}")
            return True
        return False


# Global plugin manager
plugin_manager = PluginManager()
