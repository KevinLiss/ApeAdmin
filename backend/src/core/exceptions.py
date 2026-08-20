"""Custom exception classes and global exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        msg: str = "Internal Server Error",
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Any = None,
    ):
        self.msg = msg
        self.code = code
        self.data = data
        super().__init__(msg)


class NotFoundException(AppException):
    def __init__(self, msg: str = "Resource not found"):
        super().__init__(msg=msg, code=status.HTTP_404_NOT_FOUND)


class AuthException(AppException):
    def __init__(self, msg: str = "Authentication failed"):
        super().__init__(msg=msg, code=status.HTTP_401_UNAUTHORIZED)


class PermissionException(AppException):
    def __init__(self, msg: str = "Permission denied"):
        super().__init__(msg=msg, code=status.HTTP_403_FORBIDDEN)


class ValidationException(AppException):
    def __init__(self, msg: str = "Validation error"):
        super().__init__(msg=msg, code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ConflictException(AppException):
    def __init__(self, msg: str = "Resource conflict"):
        super().__init__(msg=msg, code=status.HTTP_409_CONFLICT)


def success_response(data: Any = None, msg: str = "success") -> dict[str, Any]:
    """Standard success response envelope."""
    return {"code": 200, "msg": msg, "data": data}


def error_response(msg: str, code: int = 400, data: Any = None) -> dict[str, Any]:
    """Standard error response envelope."""
    return {"code": code, "msg": msg, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.msg} | path={request.url.path}")
        return JSONResponse(
            status_code=exc.code,
            content=error_response(exc.msg, exc.code, exc.data),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal Server Error", 500),
        )
