"""Example builtin plugin: demonstrates the full plugin lifecycle.

This plugin adds:
- A /api/v1/example/hello route
- An MCP tool that can be called by AI agents
- An event listener that logs user logins
"""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from loguru import logger

from src.core.deps import get_current_user
from src.db import get_db
from src.models import User
from src.plugins import PluginInterface, event_bus, Event


class ExamplePlugin(PluginInterface):
    """A minimal demo plugin."""

    name = "example"
    display_name = "示例插件"
    description = "Demonstrates the plugin lifecycle: routes, MCP tools, and event listeners."
    version = "1.0.0"
    author = "ApeAdmin"

    def on_load(self) -> None:
        logger.info("ExamplePlugin loaded into memory")

    async def install(self) -> None:
        """No DB tables needed for this demo plugin."""
        logger.info("ExamplePlugin installed (no-op)")

    async def uninstall(self) -> None:
        logger.info("ExamplePlugin uninstalled (no-op)")

    def register(self, app: FastAPI) -> None:
        """Register the plugin's routes under the main API prefix."""
        from src.core.config import settings

        router = APIRouter(prefix="/example", tags=["示例插件"])

        @router.get("/hello")
        async def hello():
            """A simple hello endpoint."""
            return {"code": 200, "msg": "success", "data": {"message": "Hello from ExamplePlugin!"}}

        @router.get("/protected")
        async def protected(user: Annotated[User, Depends(get_current_user)]):
            """An endpoint that requires authentication."""
            return {
                "code": 200,
                "msg": "success",
                "data": {"message": f"Hi {user.username}, you are authenticated!"},
            }

        # Register under the main API router prefix
        app.include_router(router, prefix=settings.API_PREFIX)

        # Register MCP tools (if MCP is enabled)
        try:
            from src.mcp import mcp_manager
            mcp_manager.register_tool(
                name="example_hello",
                description="A demo MCP tool that returns a greeting",
                handler=self._mcp_hello,
                plugin_name=self.name,
            )
        except Exception as exc:
            logger.warning(f"Failed to register MCP tool: {exc}")

        # Subscribe to events
        event_bus.on(Event.USER_LOGIN, self._on_user_login, plugin_name=self.name)

    async def _on_user_login(self, *args, **kwargs) -> None:
        """Event handler: log when a user logs in."""
        user_id = kwargs.get("user_id", "unknown")
        logger.info(f"[ExamplePlugin] User logged in: {user_id}")

    async def _mcp_hello(self, name: str = "World") -> str:
        """MCP tool handler."""
        return f"Hello, {name}! This is from ExamplePlugin."

    def on_unload(self) -> None:
        logger.info("ExamplePlugin unloaded")
