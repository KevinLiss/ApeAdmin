"""插件 API 路由。

.. pattern:: 路由注册模式
   :tags: 插件名 / 资源名

   - 路由前缀：``/dev-example``（插件名下划线转连字符）
   - 权限标识：``dev_example:notes:list`` / ``dev_example:notes:create`` 等
   - 依赖注入：``get_db`` 获取数据库会话，``get_current_user`` 获取当前用户
   - 权限检查：``require_permission(user, "dev_example:notes:list")``

.. important::
   - ``router`` 在此定义，在 ``plugin.py`` 的 ``register()`` 中挂载到 app。
   - 路由前缀拼接规则：``app.include_router(router, prefix=settings.API_PREFIX)``
     最终路径为 ``/api/v1/dev-example/notes``。
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.core.deps import require_permission as _require_perm
from src.core.exceptions import success_response
from src.db import get_db
from src.models import User
from src.plugins.builtin.dev_example.models import DevExampleNote
from src.plugins.builtin.dev_example.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/dev-example", tags=["插件开发示例"])


@router.get("/notes")
async def list_notes(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("dev_example:notes:list"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """分页查询备忘录列表。

    需要 ``dev_example:notes:list`` 权限。
    """
    stmt = (
        select(DevExampleNote)
        .where(DevExampleNote.is_deleted == False)  # noqa: E712
        .order_by(DevExampleNote.priority.desc(), DevExampleNote.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    # 总数
    count_stmt = select(DevExampleNote).where(DevExampleNote.is_deleted == False)  # noqa: E712
    total = len((await db.execute(count_stmt)).scalars().all())

    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [NoteOut.model_validate(item) for item in items],
    })


@router.get("/notes/{note_id}")
async def get_note(
    note_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("dev_example:notes:list"))],
):
    """查询单条备忘录。"""
    note = await db.get(DevExampleNote, note_id)
    if not note or note.is_deleted:
        raise HTTPException(status_code=404, detail="备忘录不存在")
    return success_response(data=NoteOut.model_validate(note).model_dump())


@router.post("/notes")
async def create_note(
    body: NoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("dev_example:notes:create"))],
):
    """创建备忘录。"""
    note = DevExampleNote(
        title=body.title,
        content=body.content,
        priority=body.priority,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return success_response(data=NoteOut.model_validate(note).model_dump(), msg="创建成功")


@router.put("/notes/{note_id}")
async def update_note(
    note_id: int,
    body: NoteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("dev_example:notes:edit"))],
):
    """更新备忘录。"""
    note = await db.get(DevExampleNote, note_id)
    if not note or note.is_deleted:
        raise HTTPException(status_code=404, detail="备忘录不存在")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)
    return success_response(data=NoteOut.model_validate(note).model_dump(), msg="更新成功")


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("dev_example:notes:delete"))],
):
    """删除备忘录（软删除）。"""
    note = await db.get(DevExampleNote, note_id)
    if not note or note.is_deleted:
        raise HTTPException(status_code=404, detail="备忘录不存在")

    note.is_deleted = True
    await db.commit()
    return success_response(msg="删除成功")
