"""Apehub_web MCP tools: expose marketplace data to AI agents.

These tools let the AI assistant query the plugin marketplace, look up
plugin details, and search developers — all through the standard MCP
tool calling pipeline.

Registered via ``ApehubWebPlugin.register_mcp_tools()`` and automatically
tracked/untracked by PluginManager on enable/disable.
"""

import json

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from src.db import SessionLocal
from src.mcp.manager import mcp_manager

PLUGIN_NAME = "apehub_web"


def register_mcp_tools() -> None:
    """Register all apehub_web MCP tools."""

    # ---- Tool 1: market_search ----
    mcp_manager.register_tool(
        name="market_search",
        description="搜索 ApeHub 插件市场的插件。支持按关键词、分类、价格范围筛选，返回插件基本信息。",
        handler=_market_search,
        required_permissions=[],  # 公开工具，任何人可调用
        plugin_name=PLUGIN_NAME,
        category=PLUGIN_NAME,
    )

    # ---- Tool 2: market_plugin_detail ----
    mcp_manager.register_tool(
        name="market_plugin_detail",
        description="获取插件市场某个插件的详细信息，包括版本列表、Demo 入口、文件列表、评分等。",
        handler=_market_plugin_detail,
        required_permissions=[],
        plugin_name=PLUGIN_NAME,
        category=PLUGIN_NAME,
    )

    # ---- Tool 3: market_developer_info ----
    mcp_manager.register_tool(
        name="market_developer_info",
        description="查询插件市场某开发者的信息，包括其发布的插件列表和收益概况。",
        handler=_market_developer_info,
        required_permissions=["apehub_web:plugins:review"],  # 管理员才能查看开发者信息
        plugin_name=PLUGIN_NAME,
        category=PLUGIN_NAME,
    )

    # ---- Tool 4: market_stats ----
    mcp_manager.register_tool(
        name="market_stats",
        description="获取插件市场整体统计：插件总数、已上架数、开发者数、总下载量等。",
        handler=_market_stats,
        required_permissions=[],
        plugin_name=PLUGIN_NAME,
        category=PLUGIN_NAME,
    )


# ===========================================================================
# Tool handlers
# ===========================================================================

async def _market_search(
    keyword: str = "",
    category: str = "",
    free_only: bool = False,
    page: int = 1,
    page_size: int = 10,
) -> str:
    """搜索插件市场的插件。

    Args:
        keyword: 搜索关键词（匹配插件名称、描述、标签）。
        category: 分类筛选（工具/AI/电商/仪表盘/系统增强），留空则不限。
        free_only: 设为 true 仅返回免费插件。
        page: 页码，默认1。
        page_size: 每页数量，默认10，最大50。
    """
    page = max(1, page)
    page_size = min(50, max(1, page_size))

    async with SessionLocal() as db:
        from src.plugins.builtin.apehub_web.models import ApehubWebPlugin, PluginStatus

        stmt = select(ApehubWebPlugin).where(
            ApehubWebPlugin.status == PluginStatus.APPROVED
        )
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    ApehubWebPlugin.name.ilike(kw),
                    ApehubWebPlugin.display_name.ilike(kw),
                    ApehubWebPlugin.description.ilike(kw),
                    ApehubWebPlugin.tags.ilike(kw),
                )
            )
        if category:
            stmt = stmt.where(ApehubWebPlugin.category == category)
        if free_only:
            stmt = stmt.where(ApehubWebPlugin.price == 0)

        # Count
        count_stmt = select(ApehubWebPlugin).where(
            ApehubWebPlugin.status == PluginStatus.APPROVED
        )
        if keyword:
            kw = f"%{keyword}%"
            count_stmt = count_stmt.where(
                or_(
                    ApehubWebPlugin.name.ilike(kw),
                    ApehubWebPlugin.display_name.ilike(kw),
                    ApehubWebPlugin.description.ilike(kw),
                    ApehubWebPlugin.tags.ilike(kw),
                )
            )
        if category:
            count_stmt = count_stmt.where(ApehubWebPlugin.category == category)
        if free_only:
            count_stmt = count_stmt.where(ApehubWebPlugin.price == 0)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size).order_by(
            ApehubWebPlugin.download_count.desc()
        )
        result = await db.execute(stmt)
        plugins = result.scalars().all()

    items = [
        {
            "id": p.id,
            "name": p.name,
            "display_name": p.display_name,
            "slug": p.slug,
            "description": p.description[:200] if p.description else "",
            "category": p.category,
            "version": p.version,
            "price": f"{p.price} USDT",
            "tags": p.tags.split(",") if p.tags else [],
            "download_count": p.download_count,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
        }
        for p in plugins
    ]
    return json.dumps({"total": total, "page": page, "page_size": page_size, "items": items}, ensure_ascii=False)


async def _market_plugin_detail(slug: str = "", plugin_id: int = 0) -> str:
    """获取插件的详细信息。

    Args:
        slug: 插件的 slug（URL 友好标识），与 plugin_id 二选一。
        plugin_id: 插件ID，与 slug 二选一。
    """
    if not slug and not plugin_id:
        return json.dumps({"error": "请提供 slug 或 plugin_id 参数"}, ensure_ascii=False)

    async with SessionLocal() as db:
        from src.plugins.builtin.apehub_web.models import ApehubWebPlugin

        stmt = select(ApehubWebPlugin).options(
            selectinload(ApehubWebPlugin.versions),
            selectinload(ApehubWebPlugin.demos),
            selectinload(ApehubWebPlugin.files),
        )
        if slug:
            stmt = stmt.where(ApehubWebPlugin.slug == slug)
        else:
            stmt = stmt.where(ApehubWebPlugin.id == plugin_id)
        result = await db.execute(stmt)
        plugin = result.scalar_one_or_none()

    if not plugin:
        return json.dumps({"error": "插件不存在"}, ensure_ascii=False)

    return json.dumps({
        "id": plugin.id,
        "name": plugin.name,
        "display_name": plugin.display_name,
        "slug": plugin.slug,
        "description": plugin.description,
        "category": plugin.category,
        "version": plugin.version,
        "tags": plugin.tags.split(",") if plugin.tags else [],
        "price": f"{plugin.price} USDT",
        "status": plugin.status.value if plugin.status else "unknown",
        "download_count": plugin.download_count,
        "install_count": plugin.install_count,
        "rating_avg": plugin.rating_avg,
        "rating_count": plugin.rating_count,
        "developer_id": plugin.developer_id,
        "created_at": plugin.created_at.strftime("%Y-%m-%d") if plugin.created_at else None,
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "status": v.status.value if v.status else "unknown",
                "compatibility": v.compatibility,
                "changelog": (v.changelog or "")[:500],
            }
            for v in (plugin.versions or [])
        ],
        "demos": [
            {
                "id": d.id,
                "demo_type": d.demo_type,
                "title": d.title,
                "url": d.url,
            }
            for d in (plugin.demos or [])
        ],
        "files": [
            {
                "id": f.id,
                "file_type": f.file_type,
                "filename": f.filename,
                "size": f.size,
            }
            for f in (plugin.files or [])
        ],
    }, ensure_ascii=False, default=str)


async def _market_developer_info(developer_id: int = 0, username: str = "") -> str:
    """查询插件市场开发者的信息。

    Args:
        developer_id: 开发者用户ID，与 username 二选一。
        username: 开发者用户名，与 developer_id 二选一。
    """
    if not developer_id and not username:
        return json.dumps({"error": "请提供 developer_id 或 username 参数"}, ensure_ascii=False)

    async with SessionLocal() as db:
        from src.models import User
        from src.plugins.builtin.apehub_web.models import ApehubWebPlugin, PluginStatus

        # Find user
        user_stmt = select(User).where(User.deleted_at.is_(None))
        if username:
            user_stmt = user_stmt.where(User.username == username)
        else:
            user_stmt = user_stmt.where(User.id == developer_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            return json.dumps({"error": "用户不存在"}, ensure_ascii=False)

        # Get plugins
        plugin_stmt = select(ApehubWebPlugin).where(ApehubWebPlugin.developer_id == user.id)
        plugin_result = await db.execute(plugin_stmt)
        plugins = plugin_result.scalars().all()

    published = [p for p in plugins if p.status == PluginStatus.APPROVED]
    pending = [p for p in plugins if p.status == PluginStatus.PENDING]
    total_downloads = sum(p.download_count for p in plugins)

    return json.dumps({
        "developer": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
        },
        "stats": {
            "total_plugins": len(plugins),
            "published_plugins": len(published),
            "pending_plugins": len(pending),
            "total_downloads": total_downloads,
        },
        "plugins": [
            {
                "id": p.id,
                "name": p.name,
                "display_name": p.display_name,
                "status": p.status.value if p.status else "unknown",
                "version": p.version,
                "price": f"{p.price} USDT",
                "download_count": p.download_count,
            }
            for p in plugins
        ],
    }, ensure_ascii=False, default=str)


async def _market_stats() -> str:
    """获取插件市场整体统计数据。"""
    async with SessionLocal() as db:
        from sqlalchemy import func
        from src.models import User
        from src.plugins.builtin.apehub_web.models import ApehubWebPlugin, PluginStatus

        # Total approved plugins
        total_result = await db.execute(
            select(func.count()).select_from(ApehubWebPlugin).where(
                ApehubWebPlugin.status == PluginStatus.APPROVED
            )
        )
        total_plugins = total_result.scalar() or 0

        # All plugins (any status)
        all_result = await db.execute(
            select(func.count()).select_from(ApehubWebPlugin)
        )
        all_plugins = all_result.scalar() or 0

        # Total downloads
        dl_result = await db.execute(
            select(func.coalesce(func.sum(ApehubWebPlugin.download_count), 0)).select_from(ApehubWebPlugin)
        )
        total_downloads = dl_result.scalar() or 0

        # Developer count (distinct developer_id)
        dev_result = await db.execute(
            select(func.count(func.distinct(ApehubWebPlugin.developer_id))).select_from(ApehubWebPlugin)
        )
        developer_count = dev_result.scalar() or 0

        # Category breakdown
        cat_result = await db.execute(
            select(
                ApehubWebPlugin.category,
                func.count().label("count")
            )
            .where(ApehubWebPlugin.status == PluginStatus.APPROVED)
            .group_by(ApehubWebPlugin.category)
        )
        categories = {row.category: row.count for row in cat_result}

    return json.dumps({
        "total_plugins": all_plugins,
        "published_plugins": total_plugins,
        "total_downloads": total_downloads,
        "developer_count": developer_count,
        "categories": categories,
    }, ensure_ascii=False)
