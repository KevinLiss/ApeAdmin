"""CRUD re-exports."""

from src.crud.base import CRUDBase
from src.crud.rbac import crud_dept, crud_menu, crud_role, crud_user
from src.crud.ai import crud_ai_provider
from src.crud.plugin import crud_plugin
from src.crud.log import crud_log

__all__ = [
    "CRUDBase",
    "crud_user",
    "crud_role",
    "crud_menu",
    "crud_dept",
    "crud_ai_provider",
    "crud_plugin",
    "crud_log",
]
