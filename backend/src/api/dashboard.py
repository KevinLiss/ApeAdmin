"""Dashboard aggregate stats route: one request returns all dashboard statistics.

Provides real system data for the frontend dashboard:
- System scale: user / role / dept / menu / plugin counts
- MCP activity: audit log total, today's count, recent calls
- Trend data: daily audit call counts for charts (last 14 days)
"""

from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import require_permission
from src.core.exceptions import success_response
from src.db import get_db
from src.models import Dept, McpAuditLog, Menu, Plugin, Role, User

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
async def dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("dashboard:view"))],
):
    """Return aggregated statistics for the dashboard in one request."""
    # ---- System scale counts ----
    user_total = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    role_total = (await db.execute(select(func.count()).select_from(Role))).scalar() or 0
    menu_total = (await db.execute(select(func.count()).select_from(Menu))).scalar() or 0
    dept_total = (await db.execute(select(func.count()).select_from(Dept))).scalar() or 0
    plugin_total = (await db.execute(select(func.count()).select_from(Plugin))).scalar() or 0
    plugin_enabled = (
        await db.execute(
            select(func.count()).select_from(Plugin).where(Plugin.enabled.is_(True))
        )
    ).scalar() or 0

    # ---- MCP audit activity ----
    audit_total = (
        await db.execute(select(func.count()).select_from(McpAuditLog))
    ).scalar() or 0
    today = date.today()
    audit_today = (
        await db.execute(
            select(func.count())
            .select_from(McpAuditLog)
            .where(func.date(McpAuditLog.created_at) == today.isoformat())
        )
    ).scalar() or 0

    # Recent audit calls (latest 5) for the activity feed
    recent_rows = (
        await db.execute(
            select(McpAuditLog)
            .order_by(McpAuditLog.id.desc())
            .limit(5)
        )
    ).scalars().all()
    recent_activities = [
        {
            "id": r.id,
            "action_type": r.action_type,
            "target_name": r.target_name,
            "username": r.username,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
        }
        for r in recent_rows
    ]

    # ---- Last 14 days audit call trend ----
    start = today - timedelta(days=13)
    day_rows = (
        await db.execute(
            select(func.date(McpAuditLog.created_at).label("day"), func.count().label("cnt"))
            .where(func.date(McpAuditLog.created_at) >= start.isoformat())
            .group_by(func.date(McpAuditLog.created_at))
            .order_by(func.date(McpAuditLog.created_at))
        )
    ).all()
    trend_map = {str(day): cnt for day, cnt in day_rows}
    trend_dates: list[str] = []
    trend_counts: list[int] = []
    for i in range(14):
        d = start + timedelta(days=i)
        key = d.isoformat()
        trend_dates.append(d.strftime("%m-%d"))
        trend_counts.append(trend_map.get(key, 0))

    # ---- Plugin list (for the resource table) ----
    plugin_rows = (
        await db.execute(
            select(Plugin).order_by(Plugin.id).limit(8)
        )
    ).scalars().all()
    plugins = [
        {
            "id": p.id,
            "name": p.name,
            "display_name": p.display_name,
            "version": p.version,
            "enabled": p.enabled,
            "created_at": p.created_at.strftime("%Y-%m-%d") if p.created_at else None,
        }
        for p in plugin_rows
    ]

    return success_response(
        data={
            "user": {
                "username": user.username,
                "nickname": user.nickname,
            },
            "stats": {
                "user_total": user_total,
                "role_total": role_total,
                "menu_total": menu_total,
                "dept_total": dept_total,
                "plugin_total": plugin_total,
                "plugin_enabled": plugin_enabled,
            },
            "audit": {
                "total": audit_total,
                "today": audit_today,
                "recent": recent_activities,
            },
            "trend": {
                "dates": trend_dates,
                "counts": trend_counts,
            },
            "plugins": plugins,
        }
    )