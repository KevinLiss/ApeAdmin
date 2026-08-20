"""CRUD re-exports."""

from src.crud.base import CRUDBase
from src.crud.rbac import crud_dept, crud_menu, crud_role, crud_user

__all__ = [
    "CRUDBase",
    "crud_user",
    "crud_role",
    "crud_menu",
    "crud_dept",
]
