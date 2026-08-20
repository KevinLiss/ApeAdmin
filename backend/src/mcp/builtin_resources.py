"""Built-in MCP resources: system-level read-only data sources."""

from src.mcp.manager import mcp_manager


def register_builtin_resources() -> None:
    """Register the core MCP resources that the system provides."""

    # System status resource
    mcp_manager.register_resource(
        uri="apeadmin://system/status",
        name="系统状态",
        description="获取系统运行状态信息，包括版本、运行时间等",
        handler=_get_system_status,
    )

    # User count resource
    mcp_manager.register_resource(
        uri="apeadmin://users/count",
        name="用户统计",
        description="获取系统用户总数和活跃用户数",
        handler=_get_user_count,
    )

    # System info resource (static)
    mcp_manager.register_resource(
        uri="apeadmin://system/info",
        name="系统信息",
        description="系统基本信息（静态）",
        static_content=(
            "ApeAdmin v0.1.0\n"
            "FastAPI + Vue3 admin framework with plugin & MCP support\n"
            "Author: ApeAdmin Team"
        ),
    )

    # Built-in MCP tools
    mcp_manager.register_tool(
        name="system_health_check",
        description="检查系统健康状态，返回各服务运行状况",
        handler=_health_check_tool,
    )

    mcp_manager.register_tool(
        name="system_list_plugins",
        description="列出所有已安装的插件及其状态",
        handler=_list_plugins_tool,
    )

    # Built-in MCP prompt
    mcp_manager.register_prompt(
        name="system_summary",
        description="生成系统运行概况摘要",
        template="请基于以下信息生成一份系统运行概况报告：\n系统名称：{system_name}\n版本：{version}\n检查时间：{check_time}",
        arguments=["system_name", "version", "check_time"],
    )


# ---- Resource handlers ----

async def _get_system_status() -> str:
    from src.core.config import settings
    return (
        f"App: {settings.APP_NAME} v{settings.APP_VERSION}\n"
        f"Debug: {settings.DEBUG}\n"
        f"DB: {settings.DB_TYPE}\n"
        f"MCP: {'enabled' if settings.MCP_ENABLED else 'disabled'}\n"
        f"Plugins: {'enabled' if settings.PLUGINS_ENABLED else 'disabled'}"
    )


async def _get_user_count() -> str:
    from sqlalchemy import func, select
    from src.db import SessionLocal
    from src.models import User

    async with SessionLocal() as db:
        result = await db.execute(
            select(func.count()).select_from(User).where(User.deleted_at.is_(None))
        )
        total = result.scalar() or 0
        active_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.deleted_at.is_(None), User.status == 1
            )
        )
        active = active_result.scalar() or 0

    return f"总用户数: {total}\n活跃用户数: {active}"


# ---- Tool handlers ----

async def _health_check_tool() -> str:
    """Health check MCP tool."""
    from src.core.config import settings
    return f"System healthy. {settings.APP_NAME} v{settings.APP_VERSION} is running."


async def _list_plugins_tool() -> str:
    """List plugins MCP tool."""
    from src.plugins import plugin_manager

    plugins = plugin_manager.list_plugins()
    if not plugins:
        return "No plugins installed."

    lines = [f"Installed plugins ({len(plugins)}):"]
    for p in plugins:
        status = "✓" if p.enabled else "✗"
        lines.append(f"  {status} {p.name} v{p.version} - {p.display_name}")
    return "\n".join(lines)
