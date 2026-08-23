"""System operation log routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import require_permission
from src.core.exceptions import NotFoundException, success_response
from src.crud import crud_log
from src.db import get_db
from src.models import User

router = APIRouter(prefix="/logs", tags=["系统日志"])


@router.get("")
async def list_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:log:list"))],
    page: int = 1,
    page_size: int = 20,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
):
    """Paginated log list with optional filters."""
    filters = []
    if method:
        filters.append(crud_log.model.method == method)
    if path:
        filters.append(crud_log.model.path.like(f"%{path}%"))
    if status_code:
        filters.append(crud_log.model.status_code == status_code)

    items, total = await crud_log.get_multi(
        db, page=page, page_size=page_size, filters=filters or None
    )
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "username": log.username,
                    "method": log.method,
                    "path": log.path,
                    "params": log.params,
                    "status_code": log.status_code,
                    "duration_ms": log.duration_ms,
                    "ip": log.ip,
                    "user_agent": log.user_agent,
                    "error": log.error,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in items
            ],
        }
    )


@router.get("/{log_id}")
async def get_log(
    log_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:log:list"))],
):
    """Get a single log entry."""
    log = await crud_log.get(db, log_id)
    if not log:
        raise NotFoundException("日志不存在")
    return success_response(
        data={
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "method": log.method,
            "path": log.path,
            "params": log.params,
            "status_code": log.status_code,
            "duration_ms": log.duration_ms,
            "ip": log.ip,
            "user_agent": log.user_agent,
            "error": log.error,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
    )


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:log:delete"))],
):
    """Delete a single log entry (hard delete)."""
    ok = await crud_log.delete(db, log_id, soft=False)
    if not ok:
        raise NotFoundException("日志不存在")
    return success_response(msg="删除成功")


@router.delete("")
async def clear_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("system:log:delete"))],
):
    """Clear all log entries."""
    stmt = sa_delete(crud_log.model)
    await db.execute(stmt)
    await db.commit()
    return success_response(msg="已清空所有日志")
