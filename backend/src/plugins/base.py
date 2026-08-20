"""Plugin interface and lifecycle management.

Design inspired by:
- FastAdmin addon system
- fastapi-best-architecture plugin pattern

Strategy:
- Plugins are Python packages discovered via importlib
- No hot-plugging: plugin enable/disable requires restart
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


class EventBus:
    """Simple in-process event bus for plugin communication."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: Callable, priority: int = 0) -> None:
        """Subscribe to an event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(EventHandler(event=event, handler=handler, priority=priority))
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


# Global event bus
event_bus = EventBus()


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
