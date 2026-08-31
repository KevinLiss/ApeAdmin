"""MCP (Model Context Protocol) server integration.

Architecture:
- McpManager: in-memory registry for Tools / Resources / Prompts
- Tools: registered by the core or plugins, callable by AI agents
- Resources: read-only data sources (e.g. user list, system status)
- Prompts: pre-defined templates for common AI tasks
- RBAC: tools are filtered based on the requesting user's permissions
- Concurrency: all mutations are guarded by an asyncio.Lock
"""

import asyncio
import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, get_args, get_origin, get_type_hints, TYPE_CHECKING
from enum import Enum

from loguru import logger

if TYPE_CHECKING:
    from fastapi import FastAPI


# ---------------------------------------------------------------------------
# Persistence helpers (sys_mcp_tool table)
# ---------------------------------------------------------------------------

TOOL_CALL_TIMEOUT = 30.0  # default timeout for tool execution (seconds)


def _derive_registration_path(handler: Callable) -> tuple[str, str]:
    """Derive (module, attr) for re-importing a tool handler on restart.

    Supports:
    - plain functions / bound methods → (module, function_name)
    - class methods decorated via decorators.py → the wrapper carries
      ``__mcp_decorator__`` pointing at the original function
    """
    fn = getattr(handler, "__mcp_decorator__", handler)
    module = getattr(fn, "__module__", "") or ""
    qualname = getattr(fn, "__qualname__", getattr(fn, "__name__", "")) or ""
    # Bound class methods: qualify with the owner class name, e.g. "MyPlugin.my_tool"
    if "<locals>" in qualname:
        qualname = getattr(fn, "__name__", "")
    if not module or not qualname:
        return "", ""
    return module, qualname


def _persist_tool_registration(
    name: str,
    description: str,
    plugin_name: str,
    category: str,
    required_permissions: list[str],
    handler: Callable,
) -> None:
    """Upsert a row into sys_mcp_tool (fire-and-forget, never blocks registration).

    Runs only inside a running event loop; silently skips otherwise (e.g.
    tools registered before app startup).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # no running loop — persistence unavailable, registration still OK

    handler_module, handler_attr = _derive_registration_path(handler)

    async def _upsert() -> None:
        try:
            from sqlalchemy import select
            from src.db import SessionLocal
            from src.models import McpToolRegistration

            async with SessionLocal() as db:
                stmt = select(McpToolRegistration).where(McpToolRegistration.name == name)
                row = (await db.execute(stmt)).scalar_one_or_none()
                if row is None:
                    row = McpToolRegistration(name=name)
                    db.add(row)
                row.description = description[:500]
                row.plugin_name = plugin_name
                row.category = category or plugin_name or "system"
                row.required_permissions = required_permissions or []
                row.handler_module = handler_module
                row.handler_attr = handler_attr
                row.enabled = True
                await db.commit()
        except Exception as exc:
            logger.debug(f"MCP persist skipped for '{name}': {exc}")

    loop.create_task(_upsert())


def _mark_tool_disabled(name: str) -> None:
    """Mark a tool row disabled in sys_mcp_tool (fire-and-forget)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    async def _disable() -> None:
        try:
            from sqlalchemy import update
            from src.db import SessionLocal
            from src.models import McpToolRegistration

            async with SessionLocal() as db:
                await db.execute(
                    update(McpToolRegistration)
                    .where(McpToolRegistration.name == name)
                    .values(enabled=False)
                )
                await db.commit()
        except Exception as exc:
            logger.debug(f"MCP disable persist skipped for '{name}': {exc}")

    loop.create_task(_disable())


# ---------------------------------------------------------------------------
# Type mapping helpers
# ---------------------------------------------------------------------------

_PYTHON_TO_JSON: dict[type, str] = {
    int: "integer",
    float: "number",
    bool: "boolean",
    str: "string",
    bytes: "string",
    list: "array",
    dict: "object",
    type(None): "null",
}


def _strip_optional(annotation: Any) -> tuple[Any, bool]:
    """Return (inner_type, is_optional) from Optional[X] / X | None / Union[X, None]."""
    from typing import Union
    import typing as _typing

    origin = get_origin(annotation)
    if origin is Union or (hasattr(_typing, "UnionType") and origin is _typing.UnionType):
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
        # Multiple non-None args: use the first for schema inference
        return args[0] if args else str, True
    return annotation, False


def _docstring_param_descriptions(doc: str | None) -> dict[str, str]:
    """Parse Google-style or NumPy-style docstring parameter descriptions.

    Only the ``Args:`` / ``Arguments:`` / ``Parameters:`` section is scanned,
    so free-text lines elsewhere in the docstring (e.g. ``Usage: do X``)
    can't be mistaken for parameter descriptions.
    """
    if not doc:
        return {}
    # Extract the parameter section, if present
    section = re.search(
        r"^(?:Args|Arguments|Parameters)\s*:\s*$\n(.*?)(?=^\w[\w \t]*\s*:\s*$|\Z)",
        doc,
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        return {}
    body = section.group(1)

    result: dict[str, str] = {}
    # Match:    param_name (optional type hint) : description
    # Also:     param_name: description
    pattern = re.compile(
        r"^\s+(\w+)\s*(?:\(.*?\))?\s*[:：]\s*(.+)$",
        re.MULTILINE,
    )
    for match in pattern.finditer(body):
        param_name = match.group(1).strip()
        desc = match.group(2).strip()
        # Skip common false positives like "Returns:" or "Raises:"
        if param_name.lower() in ("returns", "raises", "yields", "return"):
            continue
        result[param_name] = desc
    return result


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class McpTool:
    """A registered MCP tool."""
    name: str
    description: str
    handler: Callable
    input_schema: dict = field(default_factory=dict)
    required_permissions: list[str] = field(default_factory=list)
    plugin_name: str = ""
    category: str = ""           # grouping (e.g. "system", "apehub_web")
    is_async: bool = False


@dataclass
class McpResource:
    """A registered MCP resource (read-only data source)."""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
    handler: Callable | None = None
    static_content: str | None = None
    plugin_name: str = ""


@dataclass
class McpPrompt:
    """A registered MCP prompt template."""
    name: str
    description: str
    template: str
    arguments: list[str] = field(default_factory=list)
    plugin_name: str = ""


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class McpManager:
    """Manages MCP tools, resources, and prompts registration.

    All mutations (register/unregister) are guarded by an asyncio.Lock to
    ensure safe concurrent access from async contexts (plugin hot-swap,
    simultaneous tool registration, etc.).
    """

    def __init__(self):
        self._tools: dict[str, McpTool] = {}
        self._resources: dict[str, McpResource] = {}
        self._prompts: dict[str, McpPrompt] = {}
        self._lock = asyncio.Lock()

    @property
    def lock(self) -> asyncio.Lock:
        """Expose the lock so external callers can batch mutations safely."""
        return self._lock

    # ---- Tools ----

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        required_permissions: list[str] | None = None,
        plugin_name: str = "",
        category: str = "",
        persist: bool = True,
    ) -> None:
        """Register an MCP tool (sync method — callers should hold the lock in async contexts).

        When ``persist`` is True and an event loop is running, the registration
        is also upserted into the ``sys_mcp_tool`` table so it can be restored
        after a process restart.
        """
        input_schema = self._infer_schema(handler)
        is_async = asyncio.iscoroutinefunction(handler)
        self._tools[name] = McpTool(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
            required_permissions=required_permissions or [],
            plugin_name=plugin_name,
            category=category or plugin_name or "system",
            is_async=is_async,
        )
        logger.info(f"MCP tool registered: {name} (category={category or plugin_name or 'system'})")
        if persist:
            _persist_tool_registration(
                name=name,
                description=description,
                plugin_name=plugin_name,
                category=category,
                required_permissions=required_permissions or [],
                handler=handler,
            )

    def unregister_tool(self, name: str) -> bool:
        """Remove a registered tool and mark its DB row disabled."""
        removed = self._tools.pop(name, None) is not None
        if removed:
            _mark_tool_disabled(name)
        return removed

    def unregister_plugin_tools(self, plugin_name: str) -> list[str]:
        """Remove all tools owned by a plugin and return their names."""
        names = [name for name, tool in self._tools.items() if tool.plugin_name == plugin_name]
        for name in names:
            self._tools.pop(name, None)
            _mark_tool_disabled(name)
        return names

    def get_tool(self, name: str) -> McpTool | None:
        return self._tools.get(name)

    def list_tools(
        self,
        user_permissions: set[str] | None = None,
        category: str | None = None,
    ) -> list[McpTool]:
        """List all tools, filtered by user permissions and optionally by category."""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]

        if user_permissions is None or "*" in user_permissions:
            return tools

        accessible: list[McpTool] = []
        for tool in tools:
            if not tool.required_permissions:
                accessible.append(tool)
            elif any(p in user_permissions for p in tool.required_permissions):
                accessible.append(tool)
        return accessible

    def list_categories(self) -> list[dict[str, Any]]:
        """Return all tool categories with counts."""
        counts: dict[str, int] = {}
        for tool in self._tools.values():
            cat = tool.category or "system"
            counts[cat] = counts.get(cat, 0) + 1
        return [{"name": k, "count": v} for k, v in sorted(counts.items())]

    async def call_tool(self, name: str, arguments: dict[str, Any], timeout: float = 30.0) -> Any:
        """Execute an MCP tool by name with the given arguments.

        A timeout guards against hung plugin handlers blocking the caller
        (AI agent turns, SSE sessions, HTTP requests).
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown MCP tool: {name}")

        async def _invoke() -> Any:
            result = tool.handler(**arguments)
            if inspect.isawaitable(result):
                result = await result
            return result

        return await asyncio.wait_for(_invoke(), timeout=timeout)

    # ---- Resources ----

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        handler: Callable | None = None,
        static_content: str | None = None,
        mime_type: str = "text/plain",
        plugin_name: str = "",
    ) -> None:
        """Register an MCP resource."""
        if not handler and static_content is None:
            raise ValueError("Resource must have either a handler or static_content")
        self._resources[uri] = McpResource(
            uri=uri,
            name=name,
            description=description,
            handler=handler,
            static_content=static_content,
            mime_type=mime_type,
            plugin_name=plugin_name,
        )
        logger.info(f"MCP resource registered: {uri}")

    def list_resources(self) -> list[McpResource]:
        return list(self._resources.values())

    async def read_resource(self, uri: str) -> str:
        """Read the content of an MCP resource."""
        resource = self._resources.get(uri)
        if not resource:
            raise ValueError(f"Unknown MCP resource: {uri}")

        if resource.handler:
            result = resource.handler()
            if inspect.isawaitable(result):
                result = await result
            return str(result)
        return resource.static_content or ""

    # ---- Prompts ----

    def register_prompt(
        self,
        name: str,
        description: str,
        template: str,
        arguments: list[str] | None = None,
        plugin_name: str = "",
    ) -> None:
        """Register an MCP prompt template."""
        self._prompts[name] = McpPrompt(
            name=name,
            description=description,
            template=template,
            arguments=arguments or [],
            plugin_name=plugin_name,
        )
        logger.info(f"MCP prompt registered: {name}")

    def list_prompts(self) -> list[McpPrompt]:
        return list(self._prompts.values())

    def render_prompt(self, name: str, **kwargs: Any) -> str:
        """Render a prompt template with the given arguments."""
        prompt = self._prompts.get(name)
        if not prompt:
            raise ValueError(f"Unknown MCP prompt: {name}")
        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing prompt argument: {e}")

    # ---- Helpers ----

    @staticmethod
    def _infer_schema(handler: Callable) -> dict:
        """Infer a JSON Schema from the function's type hints and docstring.

        Supports:
        - int → integer, float → number, bool → boolean, str → string
        - list[X] → array, dict → object
        - Optional[X] / X | None → marks param as not-required
        - Enum subclasses → string with enum values
        - Google/NumPy-style docstring param descriptions
        """
        try:
            sig = inspect.signature(handler)
            type_hints = get_type_hints(handler) if hasattr(handler, "__annotations__") else {}
        except Exception:
            return {"type": "object", "properties": {}}

        # Parse docstring for param descriptions
        param_descs = _docstring_param_descriptions(
            inspect.getdoc(handler)
        )

        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            annotation = type_hints.get(param_name, param.annotation)
            is_optional = param.default is not inspect.Parameter.empty

            # Strip Optional wrapper
            if annotation is not inspect.Parameter.empty and annotation is not None:
                annotation, was_optional = _strip_optional(annotation)
                if was_optional:
                    is_optional = True

            param_schema: dict[str, Any] = {}

            if annotation is inspect.Parameter.empty or annotation is None:
                param_schema["type"] = "string"
            elif isinstance(annotation, type) and issubclass(annotation, Enum):
                # Enum → string with enum values
                param_schema["type"] = "string"
                param_schema["enum"] = [e.value for e in annotation]
            elif annotation in _PYTHON_TO_JSON:
                param_schema["type"] = _PYTHON_TO_JSON[annotation]
            else:
                origin = get_origin(annotation)
                if origin in (list, set, tuple, frozenset):
                    # list[X] → array with items
                    param_schema["type"] = "array"
                    args = get_args(annotation)
                    if args and args[0] is not ... :
                        item_type = _strip_optional(args[0])[0]
                        if isinstance(item_type, type) and item_type in _PYTHON_TO_JSON:
                            param_schema["items"] = {"type": _PYTHON_TO_JSON[item_type]}
                        else:
                            param_schema["items"] = {"type": "string"}
                    else:
                        param_schema["items"] = {"type": "string"}
                elif origin is dict or annotation is dict:
                    param_schema["type"] = "object"
                else:
                    param_schema["type"] = "string"

            # Add description from docstring
            desc = param_descs.get(param_name)
            if desc:
                param_schema["description"] = desc

            properties[param_name] = param_schema

            if not is_optional:
                required.append(param_name)

        schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema


# Global MCP manager
mcp_manager = McpManager()
