"""Add plugin detail page configuration (JSON) to site_config.

The official-site plugin detail page becomes fully configurable: section
visibility, copy, tabs, demo entries and hero metadata are all driven by the
JSON stored in this new column, editable from the admin Config page.
"""

import json

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


def _default_config() -> dict:
    return {
        "sections": {
            "hero": {
                "enabled": True,
                "star_tag_text": "⭐ 精选插件",
                "show_star": False,
                "show_meta": True,
                "show_rating": True,
                "show_icon": True,
            },
            "intro": {
                "enabled": True,
                "title": "插件介绍",
                "title_em": "介绍",
                "description": "了解这个插件的核心能力、技术特点与使用场景。",
                "show_features": True,
                "show_screenshots": True,
                "show_parameters": True,
            },
            "docs": {
                "enabled": True,
                "title": "技术文档",
                "title_em": "文档",
                "description": "安装配置、接口说明与使用指南。",
                "show_install": True,
                "show_config": True,
            },
            "demo": {
                "enabled": True,
                "title": "Demo 体验",
                "title_em": "体验",
                "description": "选择终端体验方式，直接在线感受插件能力。",
            },
            "changelog": {
                "enabled": True,
                "title": "更新日志",
                "title_em": "日志",
                "description": "插件版本迭代记录与功能变更。",
            },
        },
        "tabs": {
            "intro": {"label": "📖 介绍", "enabled": True, "sort": 1},
            "docs": {"label": "📄 文档", "enabled": True, "sort": 2},
            "demo": {"label": "🖥 Demo 体验", "enabled": True, "sort": 3},
            "changelog": {"label": "📜 更新日志", "enabled": True, "sort": 4},
        },
        "buttons": {
            "demo": {"label": "🖥 立即体验", "enabled": True, "style": "ghost"},
            "buy": {
                "label_free": "免费下载",
                "label_paid": "购买 ¥{price}",
                "enabled": True,
                "style": "primary",
            },
        },
        "labels": {
            "content": "下载",
            "author": "开发者",
            "rating": "评分",
            "version": "版本",
        },
        "float_actions": {
            "contact": {"enabled": True, "icon": "💬", "title": "客服咨询"},
            "docs": {"enabled": True, "icon": "📖", "title": "帮助文档"},
            "top": {"enabled": True, "icon": "↑", "title": "返回顶部"},
        },
    }


async def add_plugin_detail_config(connection: AsyncConnection) -> None:
    columns = await connection.run_sync(
        lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("apehub_web_site_config")}
    )
    if "plugin_detail_config" not in columns:
        await connection.execute(
            text(
                "ALTER TABLE apehub_web_site_config "
                "ADD COLUMN plugin_detail_config JSON NULL"
            )
        )
    # Backfill default config for the existing single-row site config.
    rows = await connection.execute(text("SELECT id FROM apehub_web_site_config"))
    for (row_id,) in rows.all():
        await connection.execute(
            text(
                "UPDATE apehub_web_site_config SET plugin_detail_config = :cfg "
                "WHERE id = :id AND (plugin_detail_config IS NULL OR plugin_detail_config = '')"
            ),
            {"cfg": json.dumps(_default_config(), ensure_ascii=False), "id": row_id},
        )