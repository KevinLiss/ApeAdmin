"""Plugin interface and lifecycle management.

Design inspired by:
- FastAdmin addon system
- fastapi-best-architecture plugin pattern

Strategy:
- Plugins are Python packages discovered via importlib
- Plugins can be enabled and disabled at runtime
- Each plugin implements PluginInterface with lifecycle hooks
- An EventBus allows plugins to react to application events
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from fastapi import FastAPI


# ---------------------------------------------------------------------------
# Event Bus
# ---------------------------------------------------------------------------

class Event(str, Enum):
    """Application lifecycle events that plugins can subscribe to."""
    APP_STARTUP = "app_startup"
    APP_SHUTDOWN = "app_shutdown"
    DB_READY = "db_ready"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    BEFORE_REQUEST = "before_request"
    AFTER_REQUEST = "after_request"


@dataclass
class EventHandler:
    """A single event subscription."""
    event: str
    handler: Callable
    priority: int = 0
    plugin_name: str = ""


class EventBus:
    """Simple in-process event bus for plugin communication."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(
        self,
        event: str,
        handler: Callable,
        priority: int = 0,
        plugin_name: str = "",
    ) -> None:
        """Subscribe to an event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(
            EventHandler(
                event=event,
                handler=handler,
                priority=priority,
                plugin_name=plugin_name,
            )
        )
        # Sort by priority (lower runs first)
        self._handlers[event].sort(key=lambda h: h.priority)

    async def emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all subscribers."""
        handlers = self._handlers.get(event, [])
        for h in handlers:
            try:
                result = h.handler(*args, **kwargs)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                logger.error(f"Event handler error for '{event}': {exc}")

    def off(self, event: str, handler: Callable | None = None) -> None:
        """Remove a handler (or all handlers for an event)."""
        if event not in self._handlers:
            return
        if handler is None:
            self._handlers[event] = []
        else:
            self._handlers[event] = [h for h in self._handlers[event] if h.handler != handler]

    def off_plugin(self, plugin_name: str) -> int:
        """Remove all subscriptions owned by a plugin and return the count."""
        removed = 0
        for event, handlers in list(self._handlers.items()):
            kept = [h for h in handlers if h.plugin_name != plugin_name]
            removed += len(handlers) - len(kept)
            if kept:
                self._handlers[event] = kept
            else:
                self._handlers.pop(event, None)
        return removed


# Global event bus
event_bus = EventBus()


# ---------------------------------------------------------------------------
# Per-plugin metadata isolation (L1)
# ---------------------------------------------------------------------------

# Registry: plugin name -> its isolated DeclarativeBase. Filled by
# ``make_plugin_base`` when plugin models are imported; the manager uses it
# on uninstall/reload instead of scanning the shared application metadata.
_plugin_bases: dict[str, "type[Any]"] = {}


def make_plugin_base(plugin_name: str) -> "type[Any]":
    """Create (and register) an isolated DeclarativeBase for one plugin.

    Plugin models should inherit from the returned base instead of the
    application-wide ``src.db.Base``:

        from src.plugins.base import make_plugin_base

        PluginBase = make_plugin_base("my_plugin")

        class MyTable(IDMixin, TimestampMixin, PluginBase):
            __tablename__ = "my_plugin_items"

    Benefits over the shared-metadata pattern:
    - ``install()``/``uninstall()`` operate only on this plugin's tables
      (``PluginBase.metadata.create_all/drop_all``) — no need to enumerate
      tables by hand.
    - Uninstall/reload cannot accidentally touch system or other plugins'
      table definitions; the isolated metadata is dropped together with
      the plugin module and never enters the shared registry.
    - The ``{plugin_name}_`` table-name convention stays recommended for
      clarity, but is no longer required for correct cleanup.

    Re-importing a plugin (upgrade) replaces the registry entry; the old
    base object is garbage-collected with the old module.
    """
    from sqlalchemy.orm import DeclarativeBase

    class_name = "".join(part.capitalize() for part in plugin_name.split("_")) + "Base"

    def _base_factory(ns: dict) -> type:
        cls = type(class_name, (DeclarativeBase,), ns)
        return cls

    base = _base_factory({"metadata": __import__("sqlalchemy").MetaData()})
    _plugin_bases[plugin_name] = base
    logger.debug(f"Plugin base registered: {plugin_name} ({class_name})")
    return base


def get_plugin_base(plugin_name: str) -> "type[Any] | None":
    """Return the plugin's isolated base, or None for legacy shared-Base plugins."""
    return _plugin_bases.get(plugin_name)


def pop_plugin_base(plugin_name: str) -> "type[Any] | None":
    """Remove and return the plugin's isolated base (unload/upgrade cleanup)."""
    return _plugin_bases.pop(plugin_name, None)

# ---------------------------------------------------------------------------
# Plugin Interface
# ---------------------------------------------------------------------------

class PluginInterface(ABC):
    """Base interface that all plugins must implement.

    Lifecycle:
    1. load()      — called once when the plugin module is first imported
    2. install()   — called when the admin enables the plugin (creates tables, seeds data)
    3. register(app) — called during app startup to register routes/events
    4. uninstall() — called when the admin disables the plugin (cleanup)
    """

    # Plugin metadata (override in subclass)
    name: str = ""
    display_name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    dependencies: tuple[str, ...] = ()

    @abstractmethod
    async def install(self) -> None:
        """Set up the plugin: create DB tables, seed initial data, etc."""
        ...

    @abstractmethod
    async def uninstall(self) -> None:
        """Tear down the plugin: drop tables, clean data, etc."""
        ...

    @abstractmethod
    def register(self, app: "FastAPI") -> None:
        """Register routes, middleware, MCP tools, etc. on the FastAPI app."""
        ...

    def register_mcp_tools(self) -> None:
        """Register MCP tools owned by this plugin.

        Called by PluginManager after ``register()`` so plugins can declare
        AI-callable tools in a dedicated, lifecycle-aware method.

        Plugins that don't need MCP tools can leave this as a no-op.
        """
        pass

    def unregister(self, app: "FastAPI") -> None:
        """Release plugin-owned runtime resources before it is disabled.

        The default implementation keeps existing plugins source-compatible.
        The manager still removes resources it can track automatically.
        """
        pass

    async def before_login(self, payload: dict[str, Any]) -> None:
        """Optional login guard executed before core credential validation."""
        return None

    def on_load(self) -> None:
        """Optional: called when the plugin is first loaded into memory."""
        pass

    def on_unload(self) -> None:
        """Optional: called when the plugin is being unloaded."""
        pass


@dataclass
class PluginInfo:
    """Metadata about a discovered plugin."""
    name: str
    display_name: str
    description: str
    version: str
    author: str
    module_path: str
    enabled: bool = False
    installed: bool = False
    instance: PluginInterface | None = field(default=None)
    runtime_state: str = "discovered"
    last_error: str | None = None
    dependencies: list[str] = field(default_factory=list)
