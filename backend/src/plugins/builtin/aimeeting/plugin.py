"""AI 会议助手插件——插件入口类。

功能：
- 会议创建与管理（线上/线下）
- 会议过程实时记录登记
- 会议结束后 AI 自动生成会议总结与会议纪要
"""
from loguru import logger

from fastapi import FastAPI

from src.core.config import settings
from src.db import Base, SessionLocal, engine
from src.plugins import PluginInterface
from src.plugins.builtin.aimeeting.models import (  # noqa: F401 — register ORM metadata
    AimeetingHighlight,
    AimeetingMark,
    AimeetingMeeting,
    AimeetingMinuteRecord,
    AimeetingMinutes,
)
from src.plugins.builtin.aimeeting.seed import seed_aimeeting_data


class AimeetingPlugin(PluginInterface):
    """AI 会议助手插件。"""

    name = "aimeeting"
    display_name = "AI 会议助手"
    description = "录音转写 + AI 会议纪要：开始会议进行录音 → 语音转写 → LLM 一句话总结 → 结构化会议纪要（结论/讨论要点/决议/遗留问题）"
    version = "1.2.0"
    author = "ApeAdmin"

    # ── 生命周期：安装（建表 + seed）──────────────────────
    async def install(self) -> None:
        """创建插件表 + 轻量列迁移 + seed 菜单权限。"""
        from sqlalchemy import inspect, text

        from src.models import User  # noqa: F401  register sys_user before FK resolution
        from src.models.mixins import IDMixin, TimestampMixin  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn,
                    tables=[
                        AimeetingMeeting.__table__,
                        AimeetingMinuteRecord.__table__,
                        AimeetingMinutes.__table__,
                        AimeetingHighlight.__table__,
                        AimeetingMark.__table__,
                    ],
                )
            )
            # 轻量列迁移：create_all 不给已存在的表加列，逐个检查补齐（幂等）。
            # 背景：运行库已有历史会议数据，不能 drop/create。
            _column_migrations = [
                # (表名, 列名, DDL 类型与默认值)
                ("aimeeting_meetings", "transcript_revision", "INTEGER NOT NULL DEFAULT 0"),
            ]
            for table, column, ddl in _column_migrations:
                def _has_column(sync_conn, _t=table, _c=column) -> bool:
                    cols = inspect(sync_conn).get_columns(_t)
                    return any(c["name"] == _c for c in cols)

                exists = await conn.run_sync(_has_column)
                if not exists:
                    await conn.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
                    )
                    logger.info(f"[aimeeting] migration: {table}.{column} added")

        async with SessionLocal() as db:
            await seed_aimeeting_data(db)
            await db.commit()
        logger.info("[aimeeting] installed — tables ready, menus seeded")

        # 安装即做一次环境自检（只 warning，不阻塞启动）
        from src.plugins.builtin.aimeeting.envcheck import log_startup_check

        log_startup_check(source="install")

    # ── 生命周期：卸载（清理）────────────────────────
    async def uninstall(self) -> None:
        """删除插件表与菜单。"""
        from sqlalchemy import delete

        from src.models import Menu

        async with SessionLocal() as db:
            async with engine.begin() as conn:
                await conn.run_sync(
                    lambda sync_conn: Base.metadata.drop_all(
                        sync_conn,
                        tables=[
                            AimeetingMinutes.__table__,
                            AimeetingMinuteRecord.__table__,
                            AimeetingMeeting.__table__,
                            AimeetingHighlight.__table__,
                            AimeetingMark.__table__,
                        ],
                    )
                )
            # 清理菜单
            await db.execute(delete(Menu).where(Menu.permission.like("aimeeting:%")))
            await db.execute(delete(Menu).where(Menu.path == "/aimeeting"))
            await db.commit()
        logger.info("[aimeeting] uninstalled — tables dropped, menus removed")

    # ── 生命周期：注册路由 + MCP 工具 ───────────────────
    def register(self, app: FastAPI) -> None:
        from src.plugins.builtin.aimeeting.api import router
        from src.plugins.builtin.aimeeting.streaming import router as streaming_router

        app.include_router(router, prefix=settings.API_PREFIX)
        app.include_router(streaming_router, prefix=settings.API_PREFIX)
        logger.info("[aimeeting] registered — routes mounted")

        # 每次启动都自检（find_spec + stat，毫秒级；缺失只 warning 不阻塞）
        from src.plugins.builtin.aimeeting.envcheck import log_startup_check

        log_startup_check(source="register")

    def register_mcp_tools(self) -> None:
        from src.plugins.builtin.aimeeting.mcp_tools import register_aimeeting_mcp_tools

        register_aimeeting_mcp_tools()