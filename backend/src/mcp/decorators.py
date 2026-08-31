"""Declarative MCP tool/resource/prompt registration via decorators.

Usage in a plugin's ``register_mcp_tools()`` method::

    from src.mcp.decorators import mcp_tool

    class MyPlugin(PluginInterface):
        def register_mcp_tools(self) -> None:
            register_decorated_tools(self)

        @mcp_tool("my_tool", "Does something useful", permissions=["my:perm"])
        def my_tool(self, query: str, limit: int = 10) -> str:
            '''Search for items.

            Args:
                query: The search keyword.
                limit: Max results (default 10).
            '''
            ...

Or standalone (non-class) functions::

    @mcp_tool("standalone_tool", "A standalone tool")
    def standalone_tool(x: int) -> str:
        ...
"""

from __future__ import annotations

import functools
import inspect
import weakref
from typing import Any, Callable

from src.mcp.manager import mcp_manager


# ---------------------------------------------------------------------------
# Internal registry: stores decorated functions until they are collected
# by register_decorated_tools() during plugin startup.
#
# Weak keys: entries vanish automatically when a plugin module is reloaded
# and the old function objects are garbage-collected, so repeated plugin
# reloads don't leak memory.
# ---------------------------------------------------------------------------

# Key: function -> dict of attributes set by the decorator
_pending: "weakref.WeakKeyDictionary[Callable, dict[str, Any]]" = weakref.WeakKeyDictionary()


def _make_pending():
    return {"type": None, "name": None, "description": "", "permissions": [], "category": ""}


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def mcp_tool(
    name: str,
    description: str,
    permissions: list[str] | None = None,
    category: str = "",
) -> Callable:
    """Decorate a function as an MCP tool.

    The function is **not** registered immediately. Call
    ``register_decorated_tools(plugin_instance)`` inside ``register_mcp_tools()``
    to collect and register all decorated methods.
    """

    def decorator(fn: Callable) -> Callable:
        _pending[fn] = {
            "type": "tool",
            "name": name,
            "description": description,
            "permissions": permissions or [],
            "category": category,
        }

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        # Keep the wrapper referenceable so _pending can find it via the
        # bound method when register_decorated_tools inspects a class.
        wrapper.__mcp_decorator__ = fn  # type: ignore
        return wrapper

    return decorator


def mcp_resource(
    uri: str,
    name: str,
    description: str,
    mime_type: str = "text/plain",
) -> Callable:
    """Decorate a function as an MCP resource (handler-based)."""

    def decorator(fn: Callable) -> Callable:
        _pending[fn] = {
            "type": "resource",
            "uri": uri,
            "name": name,
            "description": description,
            "mime_type": mime_type,
        }

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.__mcp_decorator__ = fn  # type: ignore
        return wrapper

    return decorator


def mcp_prompt(
    name: str,
    description: str,
    template: str,
    arguments: list[str] | None = None,
) -> Callable:
    """Decorate a **method** that returns a prompt template string.

    The method body can return a dynamic template; the return value is
    used as the template string at registration time.
    """

    def decorator(fn: Callable) -> Callable:
        _pending[fn] = {
            "type": "prompt",
            "name": name,
            "description": description,
            "template": template,
            "arguments": arguments or [],
        }

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.__mcp_decorator__ = fn  # type: ignore
        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Collector: called from PluginInterface.register_mcp_tools()
# ---------------------------------------------------------------------------

def get_plugin_mcp_tools(plugin_instance: object) -> list[dict[str, Any]]:
    """Return metadata for all @mcp_tool decorated methods on a plugin instance."""
    result = []
    cls = type(plugin_instance)
    for attr_name in dir(cls):
        try:
            attr = getattr(cls, attr_name)
        except AttributeError:
            continue
        fn = getattr(attr, "__mcp_decorator__", None)
        if fn and fn in _pending:
            meta = _pending[fn]
            result.append({"attr_name": attr_name, **meta})
    return result


def register_decorated_tools(
    plugin_instance: object,
    plugin_name: str = "",
) -> int:
    """Register all @mcp_tool/@mcp_resource/@mcp_prompt decorated methods.

    Call this inside ``PluginInterface.register_mcp_tools()``::

        def register_mcp_tools(self) -> None:
            register_decorated_tools(self, plugin_name=self.name)

    Returns the number of items registered.
    """
    cls = type(plugin_instance)
    plugin_name = plugin_name or getattr(plugin_instance, "name", "")
    count = 0

    for attr_name in dir(cls):
        try:
            attr = getattr(cls, attr_name)
        except AttributeError:
            continue
        fn = getattr(attr, "__mcp_decorator__", None)
        if not fn or fn not in _pending:
            continue

        meta = _pending[fn]
        # Get the bound method so `self` is passed automatically
        bound = getattr(plugin_instance, attr_name)

        if meta["type"] == "tool":
            mcp_manager.register_tool(
                name=meta["name"],
                description=meta["description"],
                handler=bound,
                required_permissions=meta.get("permissions", []),
                plugin_name=plugin_name,
                category=meta.get("category", "") or plugin_name,
            )
            count += 1
        elif meta["type"] == "resource":
            mcp_manager.register_resource(
                uri=meta["uri"],
                name=meta["name"],
                description=meta["description"],
                handler=bound,
                mime_type=meta.get("mime_type", "text/plain"),
                plugin_name=plugin_name,
            )
            count += 1
        elif meta["type"] == "prompt":
            mcp_manager.register_prompt(
                name=meta["name"],
                description=meta["description"],
                template=meta["template"],
                arguments=meta.get("arguments", []),
                plugin_name=plugin_name,
            )
            count += 1

    if count:
        logger.info(f"Plugin '{plugin_name}' registered {count} MCP items via decorators")
    return count


# Late import to avoid circular dependency at module load time
from loguru import logger  # noqa: E402
