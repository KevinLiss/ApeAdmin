"""Plugin manager: discovery, loading, lifecycle management.

Discovery strategy:
- Scan the builtin plugins directory (src/plugins/builtin/*)
- Each plugin is a Python package with a __init__.py that exports a Plugin class
- The Plugin class must implement PluginInterface
- Plugin state (enabled/disabled/installed) is persisted in DB or config file
"""

import asyncio
import importlib
import inspect
import json
import pkgutil
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, TYPE_CHECKING

from fastapi import FastAPI
from loguru import logger

from src.core.config import settings
from src.plugins.base import PluginInfo, PluginInterface, event_bus

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self):
        self._plugins: dict[str, PluginInfo] = {}
        self._builtin_dir = Path(settings.PLUGINS_BUILTIN_DIR)
        self._operation_lock = asyncio.Lock()
        self._plugin_locks: dict[str, asyncio.Lock] = {}
        # Store route objects, not list indexes: indexes shift when another
        # plugin is enabled or disabled.
        self._plugin_routes: dict[str, list[Any]] = {}
        self._plugin_mcp_tools: dict[str, list[str]] = {}
        self._plugin_events: dict[str, list[tuple[str, Any]]] = {}

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
                    dependencies=self._read_manifest_dependencies(Path(module.__path__[0])),
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
            await self._sync_plugin_menus(db)

    async def _sync_plugin_menus(self, db: "AsyncSession") -> int:
        """Keep plugin-owned menu branches aligned with runtime availability."""
        from sqlalchemy import select
        from src.models.plugin import Plugin
        from src.models.rbac import Menu

        registered = {
            record.name
            for record in (await db.execute(select(Plugin))).scalars().all()
        }
        available = {name for name, info in self._plugins.items() if info.enabled}
        # ``apehub`` was seeded before plugin ownership metadata existed and
        # must remain hidden when its package has been removed from the host.
        known_names = registered | set(self._plugins) | {"apehub"}
        menus = (await db.execute(select(Menu))).scalars().all()
        changed = 0
        for menu in menus:
            permission = menu.permission or ""
            component = menu.component or ""
            path = menu.path or ""
            is_core_dashboard = component == "apeui/dashboard/Monitor"
            owner = next(
                (
                    plugin_name
                    for plugin_name in known_names
                    if not is_core_dashboard and (
                        permission.startswith(f"{plugin_name}:")
                        or component == plugin_name
                        or component.startswith(f"{plugin_name}/")
                    )
                    or any(
                        path == route_prefix or path.startswith(f"{route_prefix}/")
                        for route_prefix in {f"/{plugin_name}", f"/{plugin_name.replace('_', '-')}"}
                    )
                ),
                None,
            )
            if owner is None:
                continue
            target_status = 1 if owner in available else 0
            if menu.status != target_status:
                menu.status = target_status
                changed += 1
        if changed:
            await db.commit()
        return changed

    def _find_plugin_class(self, module: Any) -> type[PluginInterface] | None:
        """Find the first PluginInterface subclass in a module."""
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, PluginInterface) and obj is not PluginInterface:
                return obj
        return None

    @staticmethod
    def _read_manifest_dependencies(package_dir: Path) -> list[str]:
        manifest_path = package_dir / "plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            dependencies = manifest.get("dependencies", [])
            return list(dependencies) if isinstance(dependencies, list) and all(isinstance(item, str) for item in dependencies) else []
        except (OSError, json.JSONDecodeError, TypeError):
            return []

    def _plugin_lock(self, name: str) -> asyncio.Lock:
        return self._plugin_locks.setdefault(name, asyncio.Lock())

    async def _persist_enabled(self, name: str, enabled: bool, db: "AsyncSession | None") -> None:
        if db is None:
            return
        from src.crud.plugin import crud_plugin

        record = await crud_plugin.get_by_name(db, name)
        if record:
            record.enabled = enabled
            await db.commit()
            await db.refresh(record)

    async def _set_plugin_menus_enabled(
        self,
        name: str,
        enabled: bool,
        db: "AsyncSession | None",
    ) -> int:
        """Hide or restore menus owned by a plugin.

        Plugin menus follow the existing convention of using the plugin name
        in their permission/component/path (for example ``apehub:content:list``
        and ``apehub/admin/content``). The parent directory is matched by its
        route path as well, so disabling a plugin removes the whole sidebar
        branch from the next ``/auth/userinfo`` response.
        """
        if db is None:
            return 0
        from sqlalchemy import select
        from src.models.rbac import Menu

        result = await db.execute(select(Menu))
        prefix = f"{name}:"
        route_prefixes = {f"/{name}", f"/{name.replace('_', '-')}"}
        component_prefix = f"{name}/"
        matched = []
        for menu in result.scalars().all():
            permission = menu.permission or ""
            component = menu.component or ""
            path = menu.path or ""
            # ``apeui/dashboard/Monitor`` is the core landing page. Its
            # frontend namespace must not make it disappear when the optional
            # ApeUI website plugin is disabled.
            is_core_dashboard = name == "apeui" and component == "apeui/dashboard/Monitor"
            if (
                (permission.startswith(prefix) and not is_core_dashboard)
                or component == name
                or (component.startswith(component_prefix) and not is_core_dashboard)
                or any(path == route_prefix or path.startswith(f"{route_prefix}/") for route_prefix in route_prefixes)
            ):
                matched.append(menu)
        for menu in matched:
            menu.status = 1 if enabled else 0
        if matched:
            await db.commit()
        return len(matched)

    def _discover_one(self, name: str) -> PluginInfo:
        existing = self._plugins.get(name)
        module_path = existing.module_path if existing else f"src.plugins.builtin.{name}"
        try:
            module = importlib.import_module(module_path)
            plugin_class = self._find_plugin_class(module)
        except ModuleNotFoundError:
            # The public plugin name may differ from its package directory
            # (for example, ``example`` vs ``example_plugin``).
            builtin_pkg = importlib.import_module("src.plugins.builtin")
            module = None
            plugin_class = None
            for _importer, modname, ispkg in pkgutil.iter_modules(builtin_pkg.__path__):
                if not ispkg:
                    continue
                candidate_path = f"src.plugins.builtin.{modname}"
                candidate = importlib.import_module(candidate_path)
                candidate_class = self._find_plugin_class(candidate)
                if candidate_class is not None and getattr(candidate_class, "name", "") == name:
                    module_path = candidate_path
                    module = candidate
                    plugin_class = candidate_class
                    break
        if plugin_class is None:
            raise ValueError(f"插件 '{name}' 未找到 PluginInterface 实现")
        instance = plugin_class()
        package_dir = Path(module.__path__[0]) if getattr(module, "__path__", None) else Path(module.__file__).parent
        info = PluginInfo(
            name=instance.name or name,
            display_name=instance.display_name or name,
            description=instance.description,
            version=instance.version,
            author=instance.author,
            module_path=module_path,
            enabled=False,
            instance=instance,
            dependencies=self._read_manifest_dependencies(package_dir) or list(getattr(instance, "dependencies", []) or []),
        )
        self._plugins[info.name] = info
        return info

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, ...]:
        numbers = re.findall(r"\d+", version)
        return tuple(int(value) for value in numbers) or (0,)

    def _check_dependencies(self, name: str, dependencies: list[str]) -> None:
        requirement = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)(?:\s*(>=|==|<=|>|<)\s*([0-9][A-Za-z0-9_.-]*))?$")
        for raw in dependencies:
            match = requirement.fullmatch(raw.strip()) if isinstance(raw, str) else None
            if not match:
                raise ValueError(f"插件 '{name}' 的依赖声明无效: {raw}")
            dependency, operator, required_version = match.groups()
            if dependency == "core":
                actual_version = settings.APP_VERSION
            else:
                target = self._plugins.get(dependency)
                if target is None or target.runtime_state not in {"active", "installed"}:
                    raise ValueError(f"插件 '{name}' 依赖未满足: {raw}")
                actual_version = target.version
            if operator and required_version:
                left = self._version_tuple(actual_version)
                right = self._version_tuple(required_version)
                checks = {">=": left >= right, "==": left == right, "<=": left <= right, ">": left > right, "<": left < right}
                if not checks[operator]:
                    raise ValueError(f"插件 '{name}' 依赖版本不满足: {raw} (当前 {actual_version})")

    def _check_dependents(self, name: str) -> None:
        for info in self._plugins.values():
            if info.name == name:
                continue
            for raw in info.dependencies:
                dependency = re.split(r"\s*[<>=]", raw, maxsplit=1)[0].strip()
                if dependency == name and info.runtime_state in {"active", "installed"}:
                    raise ValueError(f"插件 '{name}' 仍被 '{info.name}' 依赖，无法卸载")

    def _track_registered_resources(
        self,
        name: str,
        app: FastAPI,
        before_routes: set[int],
        before_tools: set[str],
        before_events: set[tuple[str, int]],
    ) -> dict[str, int]:
        from src.mcp import mcp_manager

        routes = [route for route in app.router.routes if id(route) not in before_routes]
        tools = [tool for tool in mcp_manager._tools if tool not in before_tools]
        events = [
            (event, handler.handler)
            for event, handlers in event_bus._handlers.items()
            for handler in handlers
            if (event, id(handler.handler)) not in before_events
        ]
        self._plugin_routes[name] = routes
        self._plugin_mcp_tools[name] = tools
        self._plugin_events[name] = events
        return {
            "routes_registered": len(routes),
            "mcp_tools_registered": len(tools),
            "events_registered": len(events),
        }

    def _unregister_resources(self, name: str, app: FastAPI) -> dict[str, int]:
        from src.mcp import mcp_manager

        routes = self._plugin_routes.pop(name, [])
        route_ids = {id(route) for route in routes}
        # FastAPI stores ``include_router`` calls as internal wrapper objects
        # in newer Starlette releases.  A repeated enable can leave more than
        # one wrapper around the same underlying APIRouter, so remove every
        # wrapper sharing the tracked router as well as the tracked object.
        router_ids = {
            id(getattr(route, "original_router"))
            for route in routes
            if getattr(route, "original_router", None) is not None
        }
        removed_routes = 0
        if route_ids or router_ids:
            current = app.router.routes
            kept = [
                route for route in current
                if id(route) not in route_ids
                and id(getattr(route, "original_router", None)) not in router_ids
            ]
            removed_routes = len(current) - len(kept)
            current[:] = kept
            app.openapi_schema = None

        tracked_tools = self._plugin_mcp_tools.pop(name, [])
        removed_tools = sum(1 for tool in tracked_tools if mcp_manager.unregister_tool(tool))
        # Also remove tools explicitly tagged by newer plugins.
        removed_tools += len(mcp_manager.unregister_plugin_tools(name))

        tracked_events = self._plugin_events.pop(name, [])
        for event, handler in tracked_events:
            event_bus.off(event, handler)
        removed_events = len(tracked_events)
        removed_events += event_bus.off_plugin(name)
        return {
            "routes_removed": removed_routes,
            "mcp_tools_removed": removed_tools,
            "events_unsubscribed": removed_events,
        }

    async def install_all(self) -> None:
        """Call install() on all enabled plugins."""
        for name, info in self._plugins.items():
            if not info.enabled or not info.instance:
                continue
            try:
                info.instance.on_load()
                await info.instance.install()
                info.installed = True
                info.runtime_state = "installed"
                logger.info(f"Plugin '{name}' installed")
            except Exception as exc:
                logger.error(f"Failed to install plugin '{name}': {exc}")

    def register_all(self, app: FastAPI) -> None:
        """Register all enabled plugins' routes on the app."""
        for name, info in self._plugins.items():
            if not info.enabled or not info.instance:
                continue
            try:
                self._register_runtime(name, info, app)
                # Startup registration makes the plugin live in the current
                # process; keep the runtime state consistent with hot-toggle
                # operations so the first disable removes its resources.
                info.runtime_state = "active"
                logger.info(f"Plugin '{name}' routes registered")
            except Exception as exc:
                self._unregister_resources(name, app)
                logger.error(f"Failed to register plugin '{name}': {exc}")

    async def uninstall_all(self, app: FastAPI | None = None) -> None:
        """Release runtime resources on shutdown without deleting plugin data."""
        for name, info in self._plugins.items():
            if not info.installed or not info.instance:
                continue
            try:
                if app is not None:
                    self._unregister_resources(name, app)
                info.instance.on_unload()
                info.runtime_state = "inactive"
                logger.info(f"Plugin '{name}' released for shutdown")
            except Exception as exc:
                logger.error(f"Failed to uninstall plugin '{name}': {exc}")

    def get_plugin(self, name: str) -> PluginInfo | None:
        """Get info about a specific plugin."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginInfo]:
        """List all discovered plugins."""
        return list(self._plugins.values())

    async def before_login(self, payload: dict[str, Any]) -> None:
        """Let active plugins validate a login attempt without coupling auth to them."""
        for info in self._plugins.values():
            if info.runtime_state == "active" and info.instance:
                await info.instance.before_login(payload)

    def _register_runtime(self, name: str, info: PluginInfo, app: FastAPI) -> dict[str, int]:
        from src.mcp import mcp_manager

        before_routes = {id(route) for route in app.router.routes}
        before_tools = set(mcp_manager._tools)
        before_events = {(event, id(handler.handler)) for event, handlers in event_bus._handlers.items() for handler in handlers}
        info.instance.register(app)
        return self._track_registered_resources(name, app, before_routes, before_tools, before_events)

    async def enable_plugin(self, name: str, app: FastAPI, db: "AsyncSession | None" = None) -> dict[str, Any]:
        """Enable one plugin in the current process."""
        async with self._operation_lock, self._plugin_lock(name):
            info = self._plugins.get(name)
            if info is None:
                info = self._discover_one(name)
            if info.runtime_state == "active":
                await self._set_plugin_menus_enabled(name, True, db)
                return {"name": name, "status": "active", "already_active": True}
            try:
                self._check_dependencies(name, info.dependencies)
                if info.instance is None:
                    self._remove_plugin_metadata(name)
                    info = self._discover_one(name)
                info.instance.on_load()
                if not info.installed:
                    await info.instance.install()
                    info.installed = True
                resources = self._register_runtime(name, info, app)
                info.enabled = True
                info.runtime_state = "active"
                info.last_error = None
                await self._persist_enabled(name, True, db)
                menus_enabled = await self._set_plugin_menus_enabled(name, True, db)
                return {"name": name, "status": "active", **resources, "menus_enabled": menus_enabled}
            except Exception as exc:
                logger.exception(f"Failed to enable plugin '{name}': {exc}")
                self._unregister_resources(name, app)
                info.runtime_state = "failed"
                info.last_error = str(exc)
                raise

    async def disable_plugin(
        self,
        name: str,
        app: FastAPI,
        keep_data: bool = True,
        db: "AsyncSession | None" = None,
    ) -> dict[str, Any]:
        """Disable one plugin while preserving data by default."""
        async with self._operation_lock, self._plugin_lock(name):
            info = self._plugins.get(name)
            if info is None:
                raise ValueError(f"插件 '{name}' 不存在")
            if info.runtime_state != "active":
                info.enabled = False
                info.runtime_state = "inactive"
                await self._persist_enabled(name, False, db)
                menus_disabled = await self._set_plugin_menus_enabled(name, False, db)
                return {"name": name, "status": "inactive", "already_inactive": True, "menus_disabled": menus_disabled}
            try:
                warnings: list[str] = []
                if info.instance:
                    try:
                        info.instance.unregister(app)
                    except Exception as exc:
                        warnings.append(f"unregister hook failed: {exc}")
                        logger.warning(f"Plugin '{name}' unregister hook failed: {exc}")
                resources = self._unregister_resources(name, app)
                if not keep_data and info.instance:
                    await info.instance.uninstall()
                if info.instance:
                    info.instance.on_unload()
                # Update ORM-backed menu rows before unloading plugin modules.
                # Some plugin model mappers may still be resolving while the
                # current request session is alive.
                await self._persist_enabled(name, False, db)
                menus_disabled = await self._set_plugin_menus_enabled(name, False, db)
                self._cleanup_module_cache(info.module_path)
                info.instance = None
                info.installed = False
                info.enabled = False
                info.runtime_state = "inactive"
                info.last_error = None
                result = {"name": name, "status": "inactive", **resources, "menus_disabled": menus_disabled}
                if warnings:
                    result["warnings"] = warnings
                return result
            except Exception as exc:
                logger.exception(f"Failed to disable plugin '{name}': {exc}")
                info.runtime_state = "failed"
                info.last_error = str(exc)
                raise

    async def install_plugin_from_zip(
        self,
        zip_path: str | Path,
        app: FastAPI,
        db: "AsyncSession | None" = None,
    ) -> dict[str, Any]:
        """Import, install and activate a plugin package at runtime."""
        zip_path = Path(zip_path)
        manifest = self._validate_plugin_zip(zip_path)
        name = manifest["name"]
        async with self._operation_lock, self._plugin_lock(name):
            old = self._plugins.get(name)
            if old and old.runtime_state == "active":
                raise ValueError(f"插件 '{name}' 已启用，请先禁用后升级")
            self._check_dependencies(name, manifest.get("dependencies", []))
            backup_root: Path | None = None
            existing_dir = self._builtin_dir.resolve() / name
            if existing_dir.exists():
                backup_root = Path(tempfile.mkdtemp(prefix="apeadmin-plugin-backup-", dir=str(self._builtin_dir.resolve().parent)))
                shutil.move(str(existing_dir), str(backup_root / name))
            try:
                manifest = self.import_plugin(zip_path)
                self._cleanup_module_cache(f"src.plugins.builtin.{name}")
                self._remove_plugin_metadata(name)
                info = self._discover_one(name)
            except Exception:
                target_dir = self._builtin_dir.resolve() / name
                if target_dir.exists():
                    shutil.rmtree(target_dir, ignore_errors=True)
                if backup_root and (backup_root / name).exists():
                    shutil.move(str(backup_root / name), str(target_dir))
                if backup_root:
                    shutil.rmtree(backup_root, ignore_errors=True)
                raise
            try:
                info.instance.on_load()
                await info.instance.install()
                info.installed = True
                info.dependencies = list(manifest.get("dependencies", []))
                resources = self._register_runtime(name, info, app)
                info.enabled = True
                info.runtime_state = "active"
                await self._persist_enabled(name, True, db)
                if backup_root:
                    shutil.rmtree(backup_root, ignore_errors=True)
                return {
                    "name": name,
                    "display_name": info.display_name,
                    "description": info.description,
                    "version": info.version,
                    "author": info.author,
                    "status": "active",
                    **resources,
                }
            except Exception as exc:
                self._unregister_resources(name, app)
                self._cleanup_module_cache(info.module_path)
                self.remove_plugin_files(name)
                if backup_root and (backup_root / name).exists():
                    shutil.move(str(backup_root / name), str(self._builtin_dir.resolve() / name))
                if backup_root:
                    shutil.rmtree(backup_root, ignore_errors=True)
                if old:
                    self._plugins[name] = old
                else:
                    self._plugins.pop(name, None)
                version = manifest.get("version", "未知版本")
                raise ValueError(
                    f"插件 '{name}' {version} 安装失败（install/register）："
                    f"{type(exc).__name__}: {exc}。"
                    "插件文件和本次运行时注册已回滚；已提交的数据库迁移不会自动删除，以保护既有数据。"
                    "请检查插件依赖、迁移脚本和后端日志后重试。"
                ) from exc

    async def uninstall_plugin(
        self,
        name: str,
        app: FastAPI,
        keep_data: bool = True,
        db: "AsyncSession | None" = None,
    ) -> dict[str, Any]:
        """Disable and remove a plugin package, optionally deleting data."""
        async with self._operation_lock, self._plugin_lock(name):
            info = self._plugins.get(name)
            if info is None:
                raise ValueError(f"插件 '{name}' 不存在")
            try:
                self._check_dependents(name)
                warnings: list[str] = []
                if info.runtime_state == "active":
                    if info.instance:
                        try:
                            info.instance.unregister(app)
                        except Exception as exc:
                            warnings.append(f"unregister hook failed: {exc}")
                            logger.warning(f"Plugin '{name}' unregister hook failed: {exc}")
                    resources = self._unregister_resources(name, app)
                    if not keep_data and info.instance:
                        await info.instance.uninstall()
                    if info.instance:
                        info.instance.on_unload()
                else:
                    resources = {"routes_removed": 0, "mcp_tools_removed": 0, "events_unsubscribed": 0}
                await self._set_plugin_menus_enabled(name, False, db)
                self._cleanup_module_cache(info.module_path)
                self.remove_plugin_files(name)
                if db is not None:
                    from src.crud.plugin import crud_plugin

                    record = await crud_plugin.get_by_name(db, name)
                    if record:
                        await db.delete(record)
                        await db.commit()
                self._plugins.pop(name, None)
                result = {"name": name, "status": "removed", "data_preserved": keep_data, **resources}
                if warnings:
                    result["warnings"] = warnings
                return result
            except Exception as exc:
                logger.exception(f"Failed to uninstall plugin '{name}': {exc}")
                raise

    def _cleanup_module_cache(self, module_prefix: str) -> int:
        """Remove a plugin package and its children from ``sys.modules``."""
        keys = [key for key in sys.modules if key == module_prefix or key.startswith(f"{module_prefix}.")]
        for key in keys:
            sys.modules.pop(key, None)
        importlib.invalidate_caches()
        return len(keys)

    @staticmethod
    def _remove_plugin_metadata(name: str) -> int:
        """Remove stale in-memory table definitions before re-importing models.

        SQLAlchemy keeps declarative ``Table`` objects in shared metadata even
        after a plugin module is removed from ``sys.modules``. This cleanup
        does not drop database tables or delete any persisted data.
        """
        from src.db.engine import Base

        prefix = f"{name}_"
        stale = [
            table for table_name, table in Base.metadata.tables.items()
            if table_name.startswith(prefix)
        ]
        for table in stale:
            Base.metadata.remove(table)
        return len(stale)

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
            if not isinstance(plugin_name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,99}", plugin_name):
                raise ValueError("plugin.json 的 name 必须是合法的 Python 包名")
            dependencies = manifest.get("dependencies", [])
            if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
                raise ValueError("plugin.json 的 dependencies 必须是字符串数组")

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
        builtin_dir.mkdir(parents=True, exist_ok=True)
        target_dir = builtin_dir / plugin_name

        # Stage and flatten a single archive root. Validate every destination
        # before writing so a ZIP cannot escape the plugin directory.
        staging = Path(tempfile.mkdtemp(prefix="apeadmin-plugin-", dir=str(builtin_dir.parent)))
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = [name for name in zf.namelist() if name and not name.endswith("/")]
                first_parts = {name.split("/", 1)[0] for name in names}
                has_root = len(first_parts) == 1 and all("/" in name for name in names)
                root = next(iter(first_parts)) + "/" if has_root else ""
                for name in names:
                    relative = name[len(root):] if root and name.startswith(root) else name
                    destination = (staging / relative).resolve()
                    if staging not in destination.parents:
                        raise ValueError("压缩包包含非法路径")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(name) as source, destination.open("wb") as target:
                        shutil.copyfileobj(source, target)
            staged_target = staging / plugin_name
            if not (staged_target / "__init__.py").exists():
                raise ValueError(f"解压后未找到 {plugin_name}/__init__.py，插件包结构不正确")
            if target_dir.exists():
                shutil.rmtree(target_dir)
                logger.info(f"Removed existing plugin directory: {target_dir}")
            shutil.move(str(staged_target), str(target_dir))
            (target_dir / "plugin.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"Extracted plugin '{plugin_name}' to {builtin_dir}")
        finally:
            shutil.rmtree(staging, ignore_errors=True)

        # Clean up the uploaded zip
        try:
            zip_path.unlink()
        except OSError:
            pass

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
