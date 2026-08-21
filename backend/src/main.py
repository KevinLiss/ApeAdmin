"""FastAPI application factory.

Assembles:
1. Logging + middleware chain
2. Exception handlers
3. Database (auto-create tables on first run)
4. Core API routes (auth, user, role, menu, dept)
5. MCP routes (tools, resources, prompts)
6. Plugin system (discover, install, register)
7. Seed initial data (super admin, default menus)
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import setup_logging
from src.core.middleware import register_middleware
from src.db import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # ---- Startup ----
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # Init database (create tables for dev/first run)
    logger.info("Initializing database...")
    await init_db()

    # Seed initial data
    from src.core.seed import seed_initial_data
    await seed_initial_data()

    # Discover and install plugins
    if settings.PLUGINS_ENABLED:
        from src.plugins import plugin_manager
        logger.info("Discovering plugins...")
        plugin_manager.discover()
        await plugin_manager.discover_async()
        await plugin_manager.install_all()
        plugin_manager.register_all(app)
        logger.info(f"Loaded {len(plugin_manager.list_plugins())} plugins")

    # Register MCP routes
    if settings.MCP_ENABLED:
        from src.mcp import register_mcp_routes
        register_mcp_routes(app)
        # Register built-in MCP resources
        from src.mcp.builtin_resources import register_builtin_resources
        register_builtin_resources()
        logger.info("MCP routes registered")

    # Emit startup event
    from src.plugins import event_bus, Event
    await event_bus.emit(Event.APP_STARTUP)

    logger.info(f"{settings.APP_NAME} started! Docs: http://localhost:8000/docs")

    yield

    # ---- Shutdown ----
    logger.info(f"Shutting down {settings.APP_NAME}...")

    if settings.PLUGINS_ENABLED:
        from src.plugins import plugin_manager
        await plugin_manager.uninstall_all()

    await close_db()
    logger.info("Goodbye!")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Setup logging first
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="FastAPI + Vue3 admin framework with plugin & MCP support",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register middleware
    register_middleware(app)

    # Register exception handlers
    register_exception_handlers(app)

    # Register core API routes
    from src.api import api_router
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Root health check
    @app.get("/health")
    async def health():
        from src.core.exceptions import success_response
        return success_response(data={
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "healthy",
        })

    return app


# Module-level app instance for uvicorn import
app = create_app()
