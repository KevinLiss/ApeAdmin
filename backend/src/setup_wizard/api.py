"""Setup wizard API routes.

All routes are mounted ONLY when the app runs in un-installed mode
(see src.main lifespan). No auth — the wizard itself is the bootstrap.

Key design decision: the wizard only
  1. tests/creates the MySQL database,
  2. writes `.env`,
  3. creates all tables (create_all).
Seeding is deferred to the NEXT restart: seed_initial_data encrypts the
default AI provider key with the Fernet key derived from JWT_SECRET, and
the running process still holds the OLD secret until restarted. Running
seed here would write ciphertext that the new secret cannot decrypt.
"""

from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.exceptions import error_response, success_response
from src.setup_wizard.state import (
    is_installed,
    setup_status,
    write_env,
    write_lock,
)

router = APIRouter(tags=["安装向导"])


# ---------------------------------------------------------------- schemas
class DbConfig(BaseModel):
    db_type: str = Field(default="mysql", pattern="^(mysql|sqlite)$")
    db_host: str = Field(default="127.0.0.1")
    db_port: int = Field(default=3306)
    db_user: str = Field(default="apeadmin")
    db_password: str = ""
    db_name: str = Field(default="apeadmin")


class InstallRequest(BaseModel):
    db: DbConfig
    site_name: str = Field(default="ApeAdmin", max_length=50)
    site_url: str = Field(default="", max_length=200)
    admin_path: str = Field(default="/admin", max_length=64)
    admin_username: str = Field(min_length=3, max_length=32)
    admin_password: str = Field(min_length=6, max_length=64)
    cors_origins: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------- helpers
def _db_url(cfg: DbConfig, *, with_db: bool = True) -> str:
    if cfg.db_type == "sqlite":
        return f"sqlite+aiosqlite:///./{cfg.db_name}.db"
    dbname = cfg.db_name if with_db else ""
    return (
        f"mysql+aiomysql://{cfg.db_user}:{cfg.db_password}"
        f"@{cfg.db_host}:{cfg.db_port}/{dbname}?charset=utf8mb4"
    )


async def _test_mysql(cfg: DbConfig) -> tuple[bool, str]:
    """Connect to MySQL, ensure database exists (create if missing)."""
    # 1. connect without db → check/create database
    try:
        engine_nodb = create_async_engine(_db_url(cfg, with_db=False), pool_pre_ping=True)
        async with engine_nodb.connect() as conn:
            exists = (
                await conn.execute(
                    text(
                        "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                        "WHERE SCHEMA_NAME = :name"
                    ),
                    {"name": cfg.db_name},
                )
            ).scalar_one_or_none()
            if not exists:
                await conn.execute(
                    text(
                        f"CREATE DATABASE `{cfg.db_name}` "
                        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
                )
        await engine_nodb.dispose()
    except Exception as exc:
        return False, f"MySQL 连接失败: {exc}"

    # 2. connect with db → verify usable
    try:
        engine = create_async_engine(_db_url(cfg), pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True, "连接成功（数据库已就绪）"
    except Exception as exc:
        return False, f"数据库访问失败: {exc}"


# ---------------------------------------------------------------- routes
@router.get("/setup/api/status")
async def get_status():
    """Wizard status: installed flag + setup_mode (pre/post restart)."""
    return success_response(data=setup_status())


@router.post("/setup/api/test-db")
async def test_db(cfg: DbConfig):
    """Test MySQL connectivity; create the database if it doesn't exist."""
    if cfg.db_type == "sqlite":
        return success_response(data={"ok": True, "message": "SQLite 无需连接测试，直接下一步即可"})
    ok, msg = await _test_mysql(cfg)
    return success_response(data={"ok": ok, "message": msg})


@router.get("/setup", include_in_schema=False)
async def setup_page():
    """Serve the wizard SPA."""
    html = Path(__file__).resolve().parent / "setup.html"
    return FileResponse(str(html), media_type="text/html")


@router.post("/setup/api/install")
async def install(req: InstallRequest):
    """Run the installation: write .env → create tables → lock.

    Seeding is intentionally deferred to the post-restart boot, where
    JWT_SECRET (and thus the Fernet key) is freshly loaded from .env.
    """
    if is_installed():
        return error_response(msg="系统已完成安装，请直接访问后台", code=400)

    # normalize site_url (strip trailing slash)
    site_url = (req.site_url or "").strip().rstrip("/")
    admin_path = (req.admin_path or "/admin").strip()
    if not admin_path.startswith("/"):
        admin_path = "/" + admin_path
    admin_path = admin_path.rstrip("/") or "/admin"

    # 1. database connectivity / creation
    if req.db.db_type == "mysql":
        ok, msg = await _test_mysql(req.db)
        if not ok:
            return error_response(msg=msg, code=500)

    # 2. write .env
    jwt_secret = secrets.token_hex(32)
    cors = [site_url] if site_url else []
    for origin in req.cors_origins:
        if origin and origin not in cors:
            cors.append(origin)
    write_env(
        db_type=req.db.db_type,
        db_host=req.db.db_host,
        db_port=req.db.db_port,
        db_user=req.db.db_user,
        db_password=req.db.db_password,
        db_name=req.db.db_name,
        jwt_secret=jwt_secret,
        admin_username=req.admin_username,
        admin_password=req.admin_password,
        cors_origins=cors,
        site_name=req.site_name,
        admin_path=admin_path,
        site_url=site_url,
    )

    # 3. create tables against the NEW database (no seed — deferred to restart)
    try:
        await _create_tables(req.db)
    except Exception as exc:
        return error_response(msg=f"建表失败: {exc}", code=500)

    # 4. lock & report (seed will run on next restart with fresh JWT_SECRET)
    result = {
        "admin_username": req.admin_username,
        "admin_password": req.admin_password,
        "admin_path": admin_path,
        "site_url": site_url,
        "site_name": req.site_name,
        "db_type": req.db.db_type,
    }
    write_lock(result)

    return success_response(data={
        "installed": True,
        "restart_required": True,
        **result,
        "message": "安装完成，请重启后端服务（重启时自动初始化账号与基础数据）",
    })


# ---------------------------------------------------------------- internals
async def _create_tables(cfg: DbConfig) -> None:
    """Create all tables (base + any installed plugins present in the package)."""
    import src.models  # noqa: F401  register base models

    # Plugin models are optional (base-only package has no apehub_web)
    try:
        import src.plugins.builtin.apehub_web.models  # noqa: F401
    except ImportError:
        pass

    from src.db.engine import Base

    engine = create_async_engine(_db_url(cfg), pool_pre_ping=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()
