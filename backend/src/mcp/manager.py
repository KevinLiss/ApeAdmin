"""MCP (Model Context Protocol) server integration.

Design inspired by:
- fastapi-mcp: uses httpx.ASGITransport for in-process FastAPI calls
- MCP protocol spec: three primitives (Tools, Resources, Prompts)

Architecture:
- McpServer wraps a FastAPI app and exposes it via SSE transport
- Tools: registered by the core or plugins, callable by AI agents
- Resources: read-only data sources (e.g. user list, system status)
- Prompts: pre-defined templates for common AI tasks
- RBAC: tools are filtered based on the requesting user's permissions
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from fastapi import FastAPI


@dataclass
class McpTool:
    """A registered MCP tool."""
    name: str
    description: str
    handler: Callable
    input_schema: dict = field(default_factory=dict)
    required_permissions: list[str] = field(default_factory=list)


@dataclass
class McpResource:
    """A registered MCP resource (read-only data source)."""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
    handler: Callable | None = None
    static_content: str | None = None


@dataclass
class McpPrompt:
    """A registered MCP prompt template."""
    name: str
    description: str
    template: str
    arguments: list[str] = field(default_factory=list)


class McpManager:
    """Manages MCP tools, resources, and prompts registration."""

    def __init__(self):
        self._tools: dict[str, McpTool] = {}
        self._resources: dict[str, McpResource] = {}
        self._prompts: dict[str, McpPrompt] = {}

    # ---- Tools ----

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        required_permissions: list[str] | None = None,
    ) -> None:
        """Register an MCP tool."""
        # Auto-generate input schema from function signature
        input_schema = self._infer_schema(handler)
        self._tools[name] = McpTool(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
            required_permissions=required_permissions or [],
        )
        logger.info(f"MCP tool registered: {name}")

    def unregister_tool(self, name: str) -> None:
        """Remove a registered tool."""
        self._tools.pop(name, None)

    def get_tool(self, name: str) -> McpTool | None:
        return self._tools.get(name)

    def list_tools(self, user_permissions: set[str] | None = None) -> list[McpTool]:
        """List all tools, filtered by user permissions if provided."""
        if user_permissions is None or "*" in user_permissions:
            return list(self._tools.values())

        accessible: list[McpTool] = []
        for tool in self._tools.values():
            if not tool.required_permissions:
                accessible.append(tool)
            elif any(p in user_permissions for p in tool.required_permissions):
                accessible.append(tool)
        return accessible

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute an MCP tool by name with the given arguments."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown MCP tool: {name}")

        result = tool.handler(**arguments)
        if inspect.isawaitable(result):
            result = await result
        return result

    # ---- Resources ----

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        handler: Callable | None = None,
        static_content: str | None = None,
        mime_type: str = "text/plain",
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
    ) -> None:
        """Register an MCP prompt template."""
        self._prompts[name] = McpPrompt(
            name=name,
            description=description,
            template=template,
            arguments=arguments or [],
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
        """Infer a JSON Schema from the function's type hints."""
        sig = inspect.signature(handler)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation in (int, float):
                    param_type = "number"
                elif param.annotation is bool:
                    param_type = "boolean"
                elif param.annotation in (list, dict):
                    param_type = "object"

            properties[param_name] = {"type": param_type}

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema


# Global MCP manager
mcp_manager = McpManager()
