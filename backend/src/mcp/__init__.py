"""MCP system re-exports."""

from src.mcp.manager import McpManager, McpPrompt, McpResource, McpTool, mcp_manager
from src.mcp.routes import register_mcp_routes, router as mcp_router
from src.mcp.decorators import mcp_tool, mcp_resource, mcp_prompt, get_plugin_mcp_tools

__all__ = [
    "McpManager",
    "McpTool",
    "McpResource",
    "McpPrompt",
    "mcp_manager",
    "register_mcp_routes",
    "mcp_router",
    "mcp_tool",
    "mcp_resource",
    "mcp_prompt",
    "get_plugin_mcp_tools",
]
