"""API router aggregation."""

import os

from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.dept import router as dept_router
from src.api.menu import router as menu_router
from src.api.role import router as role_router
from src.api.user import router as user_router
from src.api.ai_provider import router as ai_provider_router
from src.api.chat import router as chat_router
from src.api.plugin import router as plugin_router
from src.api.dashboard import router as dashboard_router
from src.api.log import router as log_router
from src.api.files import router as files_router
from src.api.setting import router as setting_router
from src.core.config import settings
from src.core.exceptions import success_response

api_router = APIRouter()


@api_router.get("/health", tags=["系统"])
async def api_health():
    """Unauthenticated health endpoint used while the frontend waits for a restart."""
    return success_response(data={
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "pid": os.getpid(),
    })


api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(menu_router)
api_router.include_router(dept_router)
api_router.include_router(ai_provider_router)
api_router.include_router(chat_router)
api_router.include_router(plugin_router)
api_router.include_router(dashboard_router)
api_router.include_router(log_router)
api_router.include_router(files_router)
api_router.include_router(setting_router)

__all__ = ["api_router"]
