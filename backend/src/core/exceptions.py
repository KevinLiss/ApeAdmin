"""Custom exception classes and global exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
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


_FIELD_NAMES_ZH = {
    "username": "用户名",
    "password": "密码",
    "email": "邮箱",
    "verification_code": "邮箱验证码",
    "nickname": "昵称",
    "old_password": "原密码",
    "new_password": "新密码",
    "code": "验证码",
    "phone": "手机号",
    "amount": "金额",
    "title": "标题",
    "content": "内容",
}


def _humanize_validation_error(exc: RequestValidationError) -> str:
    """将 FastAPI/Pydantic 422 校验错误转换为友好的中文提示。"""
    messages: list[str] = []
    for err in exc.errors()[:3]:
        loc = [p for p in err.get("loc", ()) if p not in ("body", "query", "path")]
        field = _FIELD_NAMES_ZH.get(str(loc[0]) if loc else "", ".".join(str(p) for p in loc)) or "表单"
        err_type = err.get("type", "")
        ctx = err.get("ctx") or {}
        if err_type == "string_pattern_mismatch":
            messages.append(f"{field}格式不正确")
        elif err_type == "string_too_short":
            messages.append(f"{field}长度不足（至少 {ctx.get('min_length', '?')} 个字符）")
        elif err_type == "string_too_long":
            messages.append(f"{field}超出长度限制（最多 {ctx.get('max_length', '?')} 个字符）")
        elif err_type == "missing":
            messages.append(f"请填写{field}")
        elif "email" in err_type or "value_error" in err_type:
            messages.append(f"{field}格式不正确")
        elif err_type == "greater_than_equal":
            messages.append(f"{field}不能小于 {ctx.get('ge', '?')}")
        elif err_type == "less_than_equal":
            messages.append(f"{field}不能大于 {ctx.get('le', '?')}")
        elif err_type == "json_invalid":
            messages.append("请求数据格式错误")
        else:
            msg = err.get("msg", "")
            messages.append(f"{field}{msg}" if msg else f"{field}填写有误，请检查后重试")
    return "；".join(messages) or "请求参数有误，请检查后重试"


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.msg} | path={request.url.path}")
        return JSONResponse(
            status_code=exc.code,
            content=error_response(exc.msg, exc.code, exc.data),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        msg = _humanize_validation_error(exc)
        logger.warning(f"RequestValidationError: {msg} | path={request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(msg, status.HTTP_422_UNPROCESSABLE_ENTITY),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal Server Error", 500),
        )
