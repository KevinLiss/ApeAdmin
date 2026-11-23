"""Plugin scaffolding: generate a new plugin skeleton.

Usage:
    python -m src.plugins.scaffold my_plugin "My Plugin" "A description"

Generates a ready-to-use plugin package under ``src/plugins/builtin/``
with:
- plugin.json manifest
- __init__.py exporting the Plugin class
- plugin.py with lifecycle hooks (install/uninstall/register/register_mcp_tools)
- models.py with isolated table pattern
- api.py with a sample router
- seed.py for menu/permission registration
- mcp_tools.py with a sample MCP tool using @mcp_tool decorator
"""

import re
import sys
from pathlib import Path
from textwrap import dedent

from src.core.config import settings

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

PLUGIN_JSON = """\
{{
  "name": "{pkg_name}",
  "display_name": "{display_name}",
  "version": "1.0.0",
  "description": "{description}",
  "author": "ApeAdmin",
  "dependencies": ["core>=0.1.0"]
}}
"""

INIT_PY = """\
from .plugin import {class_name}

__all__ = ["{class_name}"]
"""

PLUGIN_PY = '''\
"""{display_name} plugin entry point."""

from fastapi import FastAPI
from loguru import logger

from src.plugins import PluginInterface


class {class_name}(PluginInterface):
    """{display_name} plugin."""

    name = "{pkg_name}"
    display_name = "{display_name}"
    description = "{description}"
    version = "1.0.0"
    author = "ApeAdmin"

    async def install(self) -> None:
        """Create plugin tables and seed initial data.

        The plugin's isolated MetaData (see models.py) creates only this
        plugin's tables; system tables and other plugins are untouched.
        """
        from src.db import engine
        from . import models  # noqa: F401 — registers ORM metadata
        from .models import PluginBase
        from .seed import seed_data

        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: PluginBase.metadata.create_all(sync_conn)
            )
        await seed_data()
        logger.info("{display_name} installed")

    async def uninstall(self) -> None:
        """Drop all plugin-owned tables.

        The isolated MetaData makes this precise: only tables defined in
        models.py are dropped — no hand-maintained table list needed.
        """
        from src.db import engine
        from .models import PluginBase

        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: PluginBase.metadata.drop_all(sync_conn)
            )
        logger.info("{display_name} uninstalled")

    def register(self, app: FastAPI) -> None:
        """Register API routes and static files."""
        from src.core.config import settings
        from .api import router

        app.include_router(router, prefix=settings.API_PREFIX)
        logger.info("{display_name} routes registered")

    def register_mcp_tools(self) -> None:
        """Register MCP tools for AI agents.

        Uses the @mcp_tool decorator for declarative registration.
        Remove this method if the plugin doesn't expose MCP tools.
        """
        from src.mcp.decorators import register_decorated_tools

        register_decorated_tools(self, plugin_name=self.name)
'''

MODELS_PY = '''\
"""{display_name} ORM models.

Models inherit from the plugin's isolated DeclarativeBase
(``make_plugin_base``): install()/uninstall() operate only on this
plugin's tables, and the shared application metadata is never touched.
Table names are still prefixed with ``{pkg_name}_`` for readability.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.mixins import IDMixin, TimestampMixin
from src.plugins.base import make_plugin_base

# Plugin-local declarative base with its own MetaData (L1 isolation).
PluginBase = make_plugin_base("{pkg_name}")


class Sample(IDMixin, TimestampMixin, PluginBase):
    """Sample model — replace with your own."""

    __tablename__ = "{pkg_name}_sample"

    name: Mapped[str] = mapped_column(String(64), index=True)
    note: Mapped[str] = mapped_column(String(255), default="")
'''

API_PY = """\
\"\"\"{display_name} API routes.\"\"\"

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.core.exceptions import success_response
from src.db import get_db
from src.models import User

router = APIRouter(prefix="/{url_prefix}", tags=["{display_name}"])


@router.get("/hello")
async def hello(
    user: Annotated[User, Depends(get_current_user)],
):
    \"\"\"Sample endpoint.\"\"\"
    return success_response(data={{"message": "Hello from {display_name}!"}})
"""

SEED_PY = """\
\"\"\"Seed initial data for {display_name}.\"\"\"

from loguru import logger
from sqlalchemy import select

from src.db import SessionLocal


async def seed_data() -> None:
    \"\"\"Create tables and seed menus/permissions.\"\"\"
    from src.db.engine import Base
    from .{pkg_name} import models  # noqa: F401

    async with SessionLocal() as db:
        # Create tables (checkfirst=True is idempotent)
        async with db.bind.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn,
                    tables=[
                        t for n, t in Base.metadata.tables.items()
                        if n.startswith("{pkg_name}_")
                    ],
                    checkfirst=True,
                )
            )

        # Register admin menus (commented out — uncomment and adjust)
        # from src.models import Menu
        # ... add menu entries with permission = "{pkg_name}:module:action"

    logger.info("{display_name} seed data ensured")
"""

MCP_TOOLS_PY = """\
\"\"\"{display_name} MCP tools: expose plugin capabilities to AI agents.

These tools are registered via the @mcp_tool decorator and automatically
collected by register_decorated_tools() during plugin startup.
\"\"\"

import json

from src.db import SessionLocal
from src.mcp.decorators import mcp_tool


# Note: methods must be on the Plugin class (plugin.py) to use @mcp_tool.
# This file shows the pattern — move these methods into your Plugin class
# or import and adapt them as needed.

# Example (add to your Plugin class in plugin.py):
#
#     @mcp_tool("{pkg_name}_hello", "Says hello from {display_name}")
#     def mcp_hello(self, name: str = "World") -> str:
#         '''Greet someone.
#
#         Args:
#             name: The person to greet.
#         '''
#         return f"Hello {{name}} from {display_name}!"
"""


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

from string import Formatter


class _SafeDict(dict):
    """Leave unknown placeholders untouched: template literals ({ } braces in
    generated code) pass through .format() without raising KeyError."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"

def to_class_name(pkg_name: str) -> str:
    """Convert 'my_plugin' to 'MyPlugin'."""
    return "".join(part.capitalize() for part in pkg_name.split("_"))


def to_class_prefix(pkg_name: str) -> str:
    """Convert 'my_plugin' to 'MyPlugin' for base class prefix."""
    return to_class_name(pkg_name)


def to_url_prefix(pkg_name: str) -> str:
    """Convert 'my_plugin' to 'my-plugin'."""
    return pkg_name.replace("_", "-")


def generate_plugin(
    pkg_name: str,
    display_name: str,
    description: str,
    output_dir: Path | None = None,
) -> Path:
    """Generate a plugin skeleton and return its path."""
    if not re.match(r"^[a-z][a-z0-9_]*$", pkg_name):
        raise ValueError("Plugin name must be snake_case (lowercase + underscores)")

    output_dir = output_dir or Path(settings.PLUGINS_BUILTIN_DIR)
    plugin_dir = output_dir / pkg_name

    if plugin_dir.exists():
        raise FileExistsError(f"Directory already exists: {plugin_dir}")

    class_name = to_class_name(pkg_name)
    class_prefix = to_class_prefix(pkg_name)
    url_prefix = to_url_prefix(pkg_name)

    # Create directory
    plugin_dir.mkdir(parents=True)

    # Generate files
    files = {
        "plugin.json": PLUGIN_JSON.format_map(_SafeDict(
            pkg_name=pkg_name,
            display_name=display_name,
            description=description,
        )),
        "__init__.py": INIT_PY.format_map(_SafeDict(class_name=class_name)),
        "plugin.py": PLUGIN_PY.format_map(_SafeDict(
            pkg_name=pkg_name,
            display_name=display_name,
            description=description,
            class_name=class_name,
        )),
        "models.py": MODELS_PY.format_map(_SafeDict(
            pkg_name=pkg_name,
            display_name=display_name,
            class_prefix=class_prefix,
        )),
        "api.py": API_PY.format_map(_SafeDict(
            display_name=display_name,
            url_prefix=url_prefix,
        )),
        "seed.py": SEED_PY.format_map(_SafeDict(
            pkg_name=pkg_name,
            display_name=display_name,
        )),
        "mcp_tools.py": MCP_TOOLS_PY.format_map(_SafeDict(
            pkg_name=pkg_name,
            display_name=display_name,
        ))
    }

    for filename, content in files.items():
        (plugin_dir / filename).write_text(content, encoding="utf-8")

    return plugin_dir


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: python -m src.plugins.scaffold <name> <display> <desc>"""
    if len(sys.argv) < 2:
        print("Usage: python -m src.plugins.scaffold <plugin_name> <display_name> <description>")
        print('Example: python -m src.plugins.scaffold my_plugin "My Plugin" "A cool plugin"')
        sys.exit(1)

    pkg_name = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else to_class_name(pkg_name)
    description = sys.argv[3] if len(sys.argv) > 3 else f"{display_name} plugin"

    path = generate_plugin(pkg_name, display_name, description)
    print(f"Plugin scaffold created at: {path}")
    print(f"  name: {pkg_name}")
    print(f"  display_name: {display_name}")
    print(f"  description: {description}")
    print()
    print("Next steps:")
    print(f"  1. Restart the backend to auto-discover '{pkg_name}'")
    print(f"  2. Enable the plugin in the admin panel")
    print(f"  3. Edit {path}/plugin.py to add your logic")


if __name__ == "__main__":
    main()
