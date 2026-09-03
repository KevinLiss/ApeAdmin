"""Pydantic 请求/响应模型（Schema）。

.. note::
   - 请求模型继承 ``BaseModel``，用 ``Field`` 做校验。
   - 响应模型加 ``model_config = ConfigDict(from_attributes=True)`` 以支持 ORM 序列化。
   - 所有接口返回统一信封 ``{"code": 200, "msg": "...", "data": ...}``，
     调用 ``success_response(data=...)`` 即可。
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── 请求模型 ──────────────────────────────────────────────

class NoteCreate(BaseModel):
    """创建备忘录。"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(default="", max_length=5000, description="内容")
    priority: int = Field(default=0, ge=0, le=2, description="优先级")


class NoteUpdate(BaseModel):
    """更新备忘录（部分字段可选）。"""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=5000)
    priority: int | None = Field(default=None, ge=0, le=2)
    completed: bool | None = None


# ── 响应模型 ──────────────────────────────────────────────

class NoteOut(BaseModel):
    """备忘录响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    priority: int
    completed: bool
    created_at: datetime
    updated_at: datetime
