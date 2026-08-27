"""A small captcha plugin used to exercise runtime hot-plug behavior."""

import secrets
import time
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from src.core.config import settings
from src.plugins import Event, PluginInterface, event_bus


class CaptchaVerifyRequest(BaseModel):
    captcha_id: str = Field(..., min_length=8, max_length=64)
    code: str = Field(..., min_length=4, max_length=8)


class LoginCaptchaPlugin(PluginInterface):
    """Generate short-lived numeric captchas and expose a test page."""

    name = "login_captcha"
    display_name = "登录验证码"
    description = "用于验证插件热拔插的登录验证码示例插件"
    version = "1.0.0"
    author = "ApeAdmin"

    def __init__(self) -> None:
        self._captchas: dict[str, tuple[str, float]] = {}

    def on_load(self) -> None:
        logger.info("LoginCaptchaPlugin loaded into memory")

    async def install(self) -> None:
        logger.info("LoginCaptchaPlugin installed")

    async def uninstall(self) -> None:
        self._captchas.clear()
        logger.info("LoginCaptchaPlugin uninstalled")

    async def before_login(self, payload: dict[str, Any]) -> None:
        captcha_id = payload.get("captcha_id")
        captcha_code = payload.get("captcha_code")
        if not captcha_id or not captcha_code:
            raise HTTPException(status_code=422, detail="请输入验证码")
        self._purge_expired()
        stored = self._captchas.pop(captcha_id, None)
        if not stored or not secrets.compare_digest(stored[0], str(captcha_code)):
            raise HTTPException(status_code=422, detail="验证码错误或已过期")

    def register(self, app: FastAPI) -> None:
        router = APIRouter(prefix="/login-captcha", tags=["登录验证码"])

        @router.get("/captcha")
        async def create_captcha() -> dict[str, Any]:
            self._purge_expired()
            captcha_id = secrets.token_urlsafe(12)
            code = f"{secrets.randbelow(10000):04d}"
            self._captchas[captcha_id] = (code, time.time() + 120)
            return {"code": 200, "msg": "success", "data": {"captcha_id": captcha_id, "code": code, "expires_in": 120}}

        @router.post("/verify")
        async def verify_captcha(body: CaptchaVerifyRequest) -> dict[str, Any]:
            self._purge_expired()
            stored = self._captchas.pop(body.captcha_id, None)
            valid = bool(stored and secrets.compare_digest(stored[0], body.code))
            return {"code": 200, "msg": "success", "data": {"valid": valid}}

        app.include_router(router, prefix=settings.API_PREFIX)
        event_bus.on(Event.USER_LOGIN, self._on_user_login, plugin_name=self.name)

    async def _on_user_login(self, *args, **kwargs) -> None:
        logger.info("[LoginCaptchaPlugin] observed user login: {}", kwargs.get("user_id", "unknown"))

    def _purge_expired(self) -> None:
        now = time.time()
        self._captchas = {key: value for key, value in self._captchas.items() if value[1] > now}

    def on_unload(self) -> None:
        self._captchas.clear()
        logger.info("LoginCaptchaPlugin unloaded")
