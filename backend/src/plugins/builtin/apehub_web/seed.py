"""ApeHub seed data: site config defaults + demo content/docs/plugins.

Called from plugin.install() after tables are created.
"""

from loguru import logger

from src.plugins.builtin.apehub_web.models import (
    ApehubWebDoc,
    ApehubWebDocCategory,
    ApehubWebNavigationItem,
    ApehubWebPlugin,
    ApehubWebSiteConfig,
    ApehubWebSiteContent,
    PluginStatus,
)


def _default_plugin_detail_config() -> dict:
    """Default fully-configurable plugin detail page layout."""
    return {
        "sections": {
            "hero": {
                "enabled": True,
                "title_template": "{display_name}",
                "subtitle_template": "{category} · {tags}",
                "description_template": "{description}",
                "show_meta": True,
                "show_rating": True,
                "show_icon": True,
                "star_tag_text": "⭐ 精选插件",
                "show_star_tag": False,
                "breadcrumb": ["首页", "插件市场", "{display_name}"],
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
                "description": "插件的安装配置、接口说明与使用指南。",
                "show_install": True,
                "show_config": True,
            },
            "demo": {
                "enabled": True,
                "title": "Demo 体验",
                "title_em": "体验",
                "description": "选择终端体验方式，直接在线感受插件的 AI 对话能力。",
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
            "demo": {
                "label": "🖥 立即体验",
                "enabled": True,
                "style": "ghost",
            },
            "buy": {
                "label_free": "免费下载",
                "label_paid": "购买 {price} USDT",
                "enabled": True,
                "style": "primary",
            },
        },
        "labels": {
            "content": "下载",
            "author": "开发者",
            "rating": "评分",
            "version": "版本",
            "featured": "⭐ 精选插件",
        },
        "float_actions": {
            "contact": {"enabled": True, "icon": "💬", "title": "客服咨询"},
            "docs": {"enabled": True, "icon": "📖", "title": "帮助文档"},
            "top": {"enabled": True, "icon": "↑", "title": "返回顶部"},
        },
    }


async def seed_apehub_web_data() -> None:
    """Insert initial data if the tables are empty."""
    from sqlalchemy import func, select

    from src.db import SessionLocal

    async with SessionLocal() as db:
        # ---- Site config (single row) ----
        cfg_count = (await db.execute(select(func.count()).select_from(ApehubWebSiteConfig))).scalar() or 0
        if cfg_count == 0:
            db.add(ApehubWebSiteConfig(
                site_name="Apehub_web",
                site_logo="/apehub-web/assets/logo.png",
                site_icon="/apehub-web/assets/logo.png",
                site_prefix="/apehub-web",
                seo_title="Apehub_web - ApeAdmin 官网",
                seo_description="ApeAdmin 企业级 AI 原生管理底座，插件市场与技术文档",
                seo_keywords="ApeAdmin,Apehub_web,插件,AI,管理后台",
                mail_host="smtp.qq.com",
                mail_port=465,
                service_fee_rate=30.0,
                theme_mode="light",
                plugin_detail_config=_default_plugin_detail_config(),
            ))
            logger.info("apehub_web: site_config seeded")

        # ---- Site content blocks ----
        content_count = (await db.execute(select(func.count()).select_from(ApehubWebSiteContent))).scalar() or 0
        if content_count == 0:
            blocks = [
                dict(block_key="hero", title="让中后台管理，为 AI 智能体而生", subtitle="面向 AI 智能体场景的开源开发框架 · MIT License", body="ApeAdmin 基于 FastAPI + Vue3 打造，跳出传统后台设计思路，原生为 AI Agent 能力调用做适配。开箱即用、可插拔扩展，帮开发者快速搭建兼具业务管理与 AI 工具输出能力的应用。", image="/apehub-web/assets/screenshot.png", sort=10, enabled=True, extra={"cta_text": "浏览插件市场", "cta_link": "/apehub-web/plugins.html"}),
                dict(block_key="architecture", title="前后端分离 · 底座与插件解耦", subtitle="Architecture", body="单体应用架构 + 后端插件化扩展，双数据库驱动无缝切换，Redis 可选自动降级。", sort=20, enabled=True, extra={}),
                dict(block_key="features", title="开箱即用的企业级能力", subtitle="Core Features", body="底座提供权限、菜单、日志等基础设施，业务功能以插件形式独立开发与部署，同时通过 MCP 网关将管理能力暴露给 AI Agent 调用。", sort=30, enabled=True, extra={}),
                dict(block_key="mcp", title="把管理系统变成 AI 的工具", subtitle="MCP Gateway", body="通过 MCP-SSE 网关，将底座与插件的管理能力封装为标准化 AI 工具，实现传统业务系统与大模型智能体的无缝打通。", sort=40, enabled=True, extra={}),
                dict(block_key="plugin_eco", title="插件化 · 让业务独立生长", subtitle="Plugin Ecosystem", body="插件间通过事件总线松耦合通信，支持 ZIP 上传安装，能力可路由注册、MCP 工具注册、事件监听。", sort=50, enabled=True, extra={}),
                dict(block_key="techstack", title="现代、稳健、可扩展", subtitle="Tech Stack", body="选型兼顾性能与开发效率，双数据库驱动与可选缓存让你在开发与生产间无缝切换。", sort=60, enabled=True, extra={}),
                dict(block_key="quickstart", title="三分钟跑起来", subtitle="Quick Start", body="默认使用 SQLite 零配置启动，无需额外安装数据库。", sort=70, enabled=True, extra={}),
                dict(block_key="cta", title="开始构建你的 AI 中后台", subtitle="", body="开源 · 免费 · 面向智能体场景，立即体验或给项目点个 Star。", sort=80, enabled=True, extra={}),
                dict(block_key="footer", title="ApeAdmin", subtitle="", body="面向 AI 智能体场景的开发框架。以 FastAPI 异步服务、Vue 3 管理界面、RBAC 与可控插件机制支撑持续交付。", sort=90, enabled=True, extra={}),
            ]
            for b in blocks:
                db.add(ApehubWebSiteContent(**b))
            logger.info("apehub_web: site_content seeded")

        # ---- Public navigation ----
        nav_count = (await db.execute(select(func.count()).select_from(ApehubWebNavigationItem))).scalar() or 0
        if nav_count == 0:
            for item in [
                ("首页", "/apehub-web/index.html", 1),
                ("插件市场", "/apehub-web/plugins.html", 2),
                ("技术文档", "/apehub-web/docs-portal/", 3),
                ("个人中心", "/apehub-web/profile.html", 4),
            ]:
                db.add(ApehubWebNavigationItem(title=item[0], link=item[1], sort=item[2]))
            logger.info("apehub_web: navigation seeded")

        # ---- Doc categories ----
        cat_count = (await db.execute(select(func.count()).select_from(ApehubWebDocCategory))).scalar() or 0
        if cat_count == 0:
            cats = [
                dict(name="快速开始", description="快速上手 ApeAdmin", sort=1),
                dict(name="插件开发", description="开发 Apehub_web 插件", sort=2),
                dict(name="常见问题", description="FAQ", sort=3),
            ]
            for c in cats:
                db.add(ApehubWebDocCategory(**c))
            await db.flush()
            logger.info("apehub_web: doc categories seeded")

        # ---- Docs ----
        doc_count = (await db.execute(select(func.count()).select_from(ApehubWebDoc))).scalar() or 0
        if doc_count == 0:
            cats = {c.name: c.id for c in (await db.execute(select(ApehubWebDocCategory))).scalars().all()}
            docs = [
                dict(category_id=cats.get("快速开始"), title="欢迎使用 Apehub_web", slug="welcome", summary="Apehub_web 官网与插件生态简介", body="# 欢迎使用 Apehub_web\n\nApehub_web 是 ApeAdmin 的官网门户插件。", version="1.1.0", author="admin", published=True, sort=1),
                dict(category_id=cats.get("插件开发"), title="开发你的第一个插件", slug="first-plugin", summary="如何开发并上架 Apehub_web 插件", body="# 开发插件\n\n参考 ApeAdmin 插件开发文档。", version="1.1.0", author="admin", published=True, sort=1),
            ]
            for d in docs:
                db.add(ApehubWebDoc(**d))
            logger.info("apehub_web: docs seeded")

        # ---- Demo plugins ----
        plugin_count = (await db.execute(select(func.count()).select_from(ApehubWebPlugin))).scalar() or 0
        if plugin_count == 0:
            db.add(ApehubWebPlugin(
                developer_id=2,  # kankan
                name="dashboard-plus",
                display_name="Dashboard Plus 增强仪表盘",
                slug="dashboard-plus",
                description="为 ApeAdmin 提供更强大的仪表盘组件与图表库。",
                category="仪表盘",
                version="1.0.0",
                tags="dashboard,图表,ECharts",
                price=0.0,
                service_fee_rate=30.0,
                status=PluginStatus.APPROVED,
                download_count=128,
            ))
            logger.info("apehub_web: demo plugin seeded")

        await db.commit()
    await _seed_admin_menus()
    logger.info("Apehub_web seed data ready")


async def _seed_admin_menus() -> None:
    """Create only the Apehub_web management menus shipped by this release."""
    from sqlalchemy import insert, select

    from src.db import SessionLocal
    from src.models import Menu, Role
    from src.models.rbac import role_menu

    menu_specs = [
        ("官网配置", "C", "admin/config", "apehub_web/admin/Config", "apehub_web:config:list", "Setting", 1),
        ("编辑官网配置", "F", None, None, "apehub_web:config:edit", None, 1),
        ("内容管理", "C", "admin/content", "apehub_web/admin/Content", "apehub_web:content:list", "Document", 2),
        ("编辑内容", "F", None, None, "apehub_web:content:edit", None, 1),
        ("文档管理", "C", "admin/docs", "apehub_web/admin/Docs", "apehub_web:docs:list", "Notebook", 3),
        ("编辑文档", "F", None, None, "apehub_web:docs:edit", None, 1),
        ("插件管理", "C", "admin/plugins", "apehub_web/admin/Plugins", "apehub_web:plugins:review", "Box", 4),
        ("订单管理", "C", "admin/orders", "apehub_web/admin/Orders", "apehub_web:orders:list", "ShoppingCart", 5),
        ("提现审核", "C", "admin/withdrawals", "apehub_web/admin/Withdrawals", "apehub_web:withdrawals:review", "Money", 6),
        ("用户管理", "C", "admin/users", "apehub_web/admin/Users", "apehub_web:users:list", "User", 7),
    ]

    async with SessionLocal() as db:
        menus = list((await db.execute(select(Menu))).scalars().all())
        root = next((menu for menu in menus if menu.path == "/apehub-web" and menu.parent_id == 0), None)
        if root is None:
            root = Menu(name="Apehub_web", parent_id=0, type="M", path="/apehub-web", icon="Shop", sort=50)
            db.add(root)
            await db.flush()
            menus.append(root)
        else:
            root.name, root.icon, root.sort, root.visible, root.status = "Apehub_web", "Shop", 50, 1, 1

        created_or_updated = [root]
        for name, menu_type, path, component, permission, icon, sort in menu_specs:
            menu = next((item for item in menus if item.permission == permission), None)
            if menu is None:
                menu = Menu(name=name, parent_id=root.id, type=menu_type)
                db.add(menu)
                menus.append(menu)
            menu.name = name
            menu.parent_id = root.id
            menu.type = menu_type
            menu.path = path
            menu.component = component
            menu.permission = permission
            menu.icon = icon
            menu.sort = sort
            menu.visible = 1
            menu.status = 1
            created_or_updated.append(menu)
        await db.flush()

        role = (await db.execute(select(Role).where(Role.code == "admin"))).scalar_one_or_none()
        if role is not None:
            bound_ids = set((await db.execute(select(role_menu.c.menu_id).where(role_menu.c.role_id == role.id))).scalars())
            missing = [menu for menu in created_or_updated if menu.id not in bound_ids]
            if missing:
                await db.execute(
                    insert(role_menu),
                    [{"role_id": role.id, "menu_id": menu.id} for menu in missing],
                )
        await db.commit()
