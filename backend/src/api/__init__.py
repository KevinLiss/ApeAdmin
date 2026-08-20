"""API router aggregation."""

from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.dept import router as dept_router
from src.api.menu import router as menu_router
from src.api.role import router as role_router
from src.api.user import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(menu_router)
api_router.include_router(dept_router)

__all__ = ["api_router"]
