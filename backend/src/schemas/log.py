"""Schema for system operation log."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LogOut(BaseModel):
    id: int
    user_id: int | None = None
    username: str | None = None
    method: str
    path: str
    params: str | None = None
    status_code: int
    duration_ms: int
    ip: str | None = None
    user_agent: str | None = None
    error: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
