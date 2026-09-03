"""MCP 工具注册——让 AI 助手能调用插件功能。

.. important:: MCP 工具注册模式
   - 在 ``plugin.py`` 的 ``register_mcp_tools()`` 中调用
   - 使用 ``mcp_manager.register_tool()`` 注册
   - **必须传** ``plugin_name=self.name``，卸载时自动清理
   - 工具函数用 ``@function_tool`` 装饰器声明参数类型
"""
import json

from loguru import logger

from src.db import SessionLocal
from src.mcp import mcp_manager


async def _list_notes() -> str:
    """列出所有备忘录。"""
    from sqlalchemy import select
    from src.plugins.builtin.dev_example.models import DevExampleNote

    async with SessionLocal() as db:
        result = await db.execute(
            select(DevExampleNote)
            .where(DevExampleNote.is_deleted == False)  # noqa: E712
            .order_by(DevExampleNote.priority.desc())
        )
        notes = result.scalars().all()
        items = [
            {"id": n.id, "title": n.title, "priority": n.priority, "completed": n.completed}
            for n in notes
        ]
    return json.dumps({"total": len(items), "items": items}, ensure_ascii=False)


async def _create_note(title: str, content: str = "", priority: int = 0) -> str:
    """创建一条备忘录。

    Args:
        title: 标题
        content: 内容（可选）
        priority: 优先级 0=普通 1=重要 2=紧急
    """
    from src.plugins.builtin.dev_example.models import DevExampleNote

    async with SessionLocal() as db:
        note = DevExampleNote(title=title, content=content, priority=priority)
        db.add(note)
        await db.commit()
        await db.refresh(note)
    return json.dumps({"id": note.id, "title": note.title, "msg": "创建成功"}, ensure_ascii=False)


def register_dev_example_mcp_tools() -> None:
    """注册 MCP 工具。在 ``plugin.py`` 的 ``register_mcp_tools()`` 中调用。"""
    mcp_manager.register_tool(
        name="dev_example_list_notes",
        description="列出所有插件开发示例的备忘录",
        handler=_list_notes,
        plugin_name="dev_example",
    )
    mcp_manager.register_tool(
        name="dev_example_create_note",
        description="创建一条插件开发示例的备忘录",
        handler=_create_note,
        plugin_name="dev_example",
    )
    logger.info("Registered 2 dev_example MCP tools")
