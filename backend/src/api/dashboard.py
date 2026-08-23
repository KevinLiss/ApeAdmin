"""Dashboard aggregate stats route: one request returns all dashboard statistics.

Provides real system data for the frontend dashboard:
- System scale: user / role / dept / menu / plugin counts
- MCP activity: audit log total, today's count, recent calls
- Trend data: daily audit call counts for charts (last 14 days)
- System monitor: CPU / memory / disk / network / online users / MCP tools
"""

import os
import platform
import time
from datetime import date, datetime, timedelta
from typing import Annotated

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import require_permission
from src.core.exceptions import success_response
from src.db import get_db
from src.mcp.manager import mcp_manager
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


# ---- System monitor (psutil) ----
# Cache boot time to calculate uptime
_boot_time = psutil.boot_time()

# Cache last network counters for rate calculation
_last_net = psutil.net_io_counters()
_last_net_ts = time.time()


def _collect_system_info() -> dict:
    """Collect real-time system metrics via psutil."""
    global _last_net, _last_net_ts

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_cores = psutil.cpu_count(logical=True) or 0
    cpu_physical = psutil.cpu_count(logical=False) or 0
    load_avg = list(os.getloadavg()) if hasattr(os, "getloadavg") else [0, 0, 0]

    # Memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk
    disk = psutil.disk_usage("/")
    disk_io = psutil.disk_io_counters()

    # Network
    net = psutil.net_io_counters()
    now = time.time()
    elapsed = now - _last_net_ts
    if elapsed > 0:
        sent_rate = (net.bytes_sent - _last_net.bytes_sent) / elapsed
        recv_rate = (net.bytes_recv - _last_net.bytes_recv) / elapsed
    else:
        sent_rate = 0
        recv_rate = 0
    _last_net = net
    _last_net_ts = now

    # System info
    uptime_seconds = int(now - _boot_time)
    hostname = platform.node()
    os_name = f"{platform.system()} {platform.release()}"
    process_count = len(psutil.pids())

    return {
        "cpu": {
            "percent": round(cpu_percent, 1),
            "cores_logical": cpu_cores,
            "cores_physical": cpu_physical,
            "load_avg": [round(x, 2) for x in load_avg],
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": round(mem.percent, 1),
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": round(swap.percent, 1),
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": round(disk.percent, 1),
            "read_count": disk_io.read_count if disk_io else 0,
            "write_count": disk_io.write_count if disk_io else 0,
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "sent_rate": round(sent_rate, 1),
            "recv_rate": round(recv_rate, 1),
        },
        "system": {
            "hostname": hostname,
            "os": os_name,
            "uptime_seconds": uptime_seconds,
            "process_count": process_count,
        },
    }


def _format_bytes(n: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


@router.get("/system")
async def dashboard_system(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("dashboard:view"))],
):
    """Return real-time system monitor data: CPU, memory, disk, network, MCP tools, online users."""
    # System metrics via psutil
    sys_info = _collect_system_info()

    # MCP tools list
    tools = mcp_manager.list_tools()
    mcp_tools = [
        {
            "name": t.name,
            "description": t.description,
            "required_permissions": t.required_permissions,
        }
        for t in tools
    ]

    # Online users: last login within 24 hours
    cutoff = datetime.now() - timedelta(hours=24)
    online_rows = (
        await db.execute(
            select(User)
            .where(User.last_login_at.isnot(None))
            .where(User.last_login_at >= cutoff)
            .order_by(User.last_login_at.desc())
            .limit(20)
        )
    ).scalars().all()
    online_users = [
        {
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "last_login_at": u.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if u.last_login_at else None,
            "last_login_ip": u.last_login_ip,
        }
        for u in online_rows
    ]

    # Plugins (reuse from stats but simpler)
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
            **sys_info,
            "mcp_tools": mcp_tools,
            "online_users": online_users,
            "plugins": plugins,
        }
    )