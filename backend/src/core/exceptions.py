"""Custom exception classes and global exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.i18n import t, get_locale


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


# Field name i18n keys — looked up via t() at render time
_FIELD_NAME_KEYS = {
    "username": "validation.field_username",
    "password": "validation.field_password",
    "email": "validation.field_email",
    "verification_code": "validation.field_verification_code",
    "nickname": "validation.field_nickname",
    "old_password": "validation.field_old_password",
    "new_password": "validation.field_new_password",
    "code": "validation.field_code",
    "phone": "validation.field_phone",
    "amount": "validation.field_amount",
    "title": "validation.field_title",
    "content": "validation.field_content",
}


def _humanize_validation_error(exc: RequestValidationError, locale: str = "zh-CN") -> str:
    """Convert FastAPI/Pydantic 422 validation errors to friendly messages."""
    messages: list[str] = []
    for err in exc.errors()[:3]:
        loc = [p for p in err.get("loc", ()) if p not in ("body", "query", "path")]
        field_key = _FIELD_NAME_KEYS.get(str(loc[0]) if loc else "", "")
        field = t(field_key, locale) if field_key else ".".join(str(p) for p in loc)
        err_type = err.get("type", "")
        ctx = err.get("ctx") or {}
        if err_type == "string_pattern_mismatch":
            messages.append(t("validation.format_invalid", locale, field=field))
        elif err_type == "string_too_short":
            messages.append(t("validation.too_short", locale, field=field, min=ctx.get('min_length', '?')))
        elif err_type == "string_too_long":
            messages.append(t("validation.too_long", locale, field=field, max=ctx.get('max_length', '?')))
        elif err_type == "missing":
            messages.append(t("validation.required", locale, field=field))
        elif "email" in err_type or "value_error" in err_type:
            messages.append(t("validation.format_invalid", locale, field=field))
        elif err_type == "greater_than_equal":
            messages.append(t("validation.gte", locale, field=field, min=ctx.get('ge', '?')))
        elif err_type == "less_than_equal":
            messages.append(t("validation.lte", locale, field=field, max=ctx.get('le', '?')))
        elif err_type == "json_invalid":
            messages.append(t("validation.json_invalid", locale))
        else:
            raw_msg = err.get("msg", "")
            if raw_msg:
                messages.append(f"{field}{raw_msg}")
            else:
                messages.append(t("validation.field_invalid", locale, field=field))
    sep = "；" if locale == "zh-CN" else "; "
    return sep.join(messages) or t("validation.params_invalid", locale)


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
        locale = get_locale(request)
        msg = _humanize_validation_error(exc, locale)
        logger.warning(f"RequestValidationError: {msg} | path={request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(msg, status.HTTP_422_UNPROCESSABLE_ENTITY),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        locale = get_locale(request)
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(t("common.internal_error", locale), 500),
        )
