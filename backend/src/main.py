"""FastAPI application factory.

Assembles:
1. Logging + middleware chain
2. Exception handlers
3. Database (auto-create tables on first run)
4. Core API routes (auth, user, role, menu, dept)
5. MCP routes (tools, resources, prompts)
6. Plugin system (discover, install, register)
7. Seed initial data (super admin, default menus)

When the app is NOT yet installed (no setup.lock), it runs in
"setup mode": database/plugins/MCP are skipped, and only the
installation wizard (/setup) + minimal health routes are served.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import setup_logging
from src.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # ---- Startup ----
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # ---- Setup mode (un-installed) ----
    from src.setup_wizard import is_installed

    if not is_installed():
        logger.warning(">>> 系统未安装，进入安装向导模式（/setup）<<<")
        _register_setup_routes(app)
        yield
        logger.info("Setup mode shutdown")
        return

    # ---- Normal mode ----
    from src.db import close_db, init_db

    # Init database (create tables for dev/first run)
    logger.info("Initializing database...")
    await init_db()

    # Seed initial data
    from src.core.seed import seed_initial_data
    await seed_initial_data()
    # Load system settings (admin_path, etc.)
    from src.crud.setting import crud_setting
    from src.db import SessionLocal
    async with SessionLocal() as sdb:
        admin_path = await crud_setting.get_value(sdb, "admin_path", "/admin")
    # Normalize: ensure starts with /
    if not admin_path.startswith("/"):
        admin_path = "/" + admin_path
    admin_path = admin_path.rstrip("/")
    if not admin_path:
        admin_path = "/admin"
    app.state.admin_path = admin_path
    logger.info(f"Admin panel path: {admin_path}")

    # Mount admin SPA if built frontend exists
    from pathlib import Path
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend_dist"
    if frontend_dist.exists():
        from fastapi.staticfiles import StaticFiles
        from starlette.staticfiles import StaticFiles as StarletteStaticFiles

        # Custom static files handler: serve real files, fallback to index.html
        # for SPA history-mode routes (e.g. /admin/login, /admin/dashboard)
        class SpaStaticFiles(StarletteStaticFiles):
            async def get_response(self, path: str, scope):
                if path == "" or path == "index.html":
                    return await super().get_response("index.html", scope)
                try:
                    return await super().get_response(path, scope)
                except Exception:
                    # File not found → serve index.html for SPA fallback
                    return await super().get_response("index.html", scope)

        app.mount(admin_path, SpaStaticFiles(directory=str(frontend_dist), html=True), name="admin_spa")
        logger.info(f"Admin SPA mounted at {admin_path} (with SPA fallback)")
    else:
        logger.info("Frontend dist not found, admin SPA not mounted (dev mode: use Vite)")

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
        # Register MCP SSE transport (standard MCP protocol over SSE)
        from src.mcp.sse_transport import register_sse_routes
        register_sse_routes(app)
        logger.info("MCP routes + SSE transport registered")

        # Restore persisted MCP tool registrations from DB
        await _restore_mcp_tools_from_db()

    # Emit startup event
    from src.plugins import event_bus, Event
    await event_bus.emit(Event.APP_STARTUP)

    logger.info(f"{settings.APP_NAME} started! Docs: http://localhost:8000/docs")

    yield

    # ---- Shutdown ----
    logger.info(f"Shutting down {settings.APP_NAME}...")

    if settings.PLUGINS_ENABLED:
        from src.plugins import plugin_manager
        await plugin_manager.uninstall_all(app)

    await close_db()
    logger.info("Goodbye!")


def _register_setup_routes(app: FastAPI) -> None:
    """Mount the installation wizard UI + API (setup mode only).

    The wizard router carries both the page (/setup) and its JSON API
    (/setup/api/*). Health stays available for panel probes.
    """
    from src.setup_wizard.api import router as setup_router

    app.include_router(setup_router)
    logger.info("Setup wizard mounted at /setup (API: /setup/api/*)")


async def _restore_mcp_tools_from_db() -> None:
    """Restore MCP tool registrations persisted in ``sys_mcp_tool`` table.

    Each row stores the tool's handler *function* (``handler_module`` +
    ``handler_attr``) plus its metadata. Restore re-imports the function and
    re-registers it via ``mcp_manager.register_tool`` — the handler is NOT
    called here (calling it would either create a dangling coroutine for
    async tools or raise TypeError for tools with required arguments).

    Tools already registered in memory (e.g. by their owning plugin's
    ``register_mcp_tools`` hook, which runs earlier) are skipped, so DB rows
    only act as a fallback for tools whose owner plugin failed to load.
    """
    try:
        from sqlalchemy import select
        from src.db import SessionLocal
        from src.models import McpToolRegistration
        from src.mcp.manager import mcp_manager

        async with SessionLocal() as db:
            stmt = select(McpToolRegistration).where(McpToolRegistration.enabled == True)
            result = await db.execute(stmt)
            rows = result.scalars().all()

        if not rows:
            return

        import importlib

        restored = 0
        skipped = 0
        for row in rows:
            if not row.handler_module or not row.handler_attr:
                continue
            if mcp_manager.get_tool(row.name) is not None:
                skipped += 1  # already registered by its owning plugin
                continue
            try:
                mod = importlib.import_module(row.handler_module)
                fn = getattr(mod, row.handler_attr, None)
                if fn is None:
                    logger.warning(f"MCP restore: {row.handler_module}.{row.handler_attr} not found")
                    continue
                mcp_manager.register_tool(
                    name=row.name,
                    description=row.description,
                    handler=fn,
                    required_permissions=row.required_permissions or [],
                    plugin_name=row.plugin_name,
                    category=row.category,
                    persist=False,  # avoid re-writing the same row during restore
                )
                restored += 1
            except Exception as exc:
                logger.error(f"MCP restore failed for '{row.name}': {exc}")

        if restored or skipped:
            logger.info(f"MCP restore done: {restored} restored from DB, {skipped} already in memory")
    except Exception as exc:
        logger.warning(f"Could not restore MCP tools from DB (table may not exist yet): {exc}")


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

    # Register core API routes (they only touch the DB per-request via get_db,
    # so mounting them in setup mode is safe — requests will simply fail with
    # 500 until installation finishes, while /setup keeps working)
    from src.api import api_router
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Root health check
    @app.get("/health")
    async def health():
        from src.core.exceptions import success_response
        from src.setup_wizard import is_installed
        return success_response(data={
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "setup" if not is_installed() else "healthy",
        })

    # Root redirect: setup mode → wizard; normal → admin (base) or site (plugin)
    from src.setup_wizard import is_installed

    @app.get("/", include_in_schema=False)
    async def root_redirect():
        if not is_installed():
            return RedirectResponse(url="/setup")
        # apehub_web plugin serves the official site at /apehub-web when present
        from pathlib import Path
        site_dir = Path(__file__).resolve().parent / "plugins" / "builtin" / "apehub_web" / "static"
        if site_dir.exists():
            return RedirectResponse(url="/apehub-web/")
        return RedirectResponse(url=settings.ADMIN_PATH + "/")

    return app


# Module-level app instance for uvicorn import
app = create_app()
