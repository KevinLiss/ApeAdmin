"""CRUD for SysLog."""

from src.crud.base import CRUDBase
from src.models.log import SysLog

crud_log = CRUDBase(SysLog)
