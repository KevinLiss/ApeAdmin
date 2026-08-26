"""ApeUI seed data: site config + content blocks + doc categories + docs + demo plugins."""

from loguru import logger
from sqlalchemy import func, select

from src.db.engine import SessionLocal
from src.plugins.builtin.apeui.models import (
    ApeUiDoc,
    ApeUiDocCategory,
    ApeUiPlugin,
    ApeUiSiteConfig,
    ApeUiSiteContent,
    PluginStatus,
)


async def seed_apeui_data() -> None:
    """Seed all ApeUI initial data (idempotent: skip if rows already exist)."""
    async with SessionLocal() as db:
        # ── 1. 站点配置（单行） ──
        cfg_count = (await db.execute(select(func.count()).select_from(ApeUiSiteConfig))).scalar() or 0
        if cfg_count == 0:
            db.add(ApeUiSiteConfig(
                site_name="ApeAdmin",
                site_logo="/apeui/assets/logo.png",
                site_prefix="/apeui",
                seo_title="ApeAdmin · 面向 AI 智能体场景的开发框架",
                seo_description="企业级 AI 原生管理底座，让插件化开发像搭积木一样简单",
                seo_keywords="ApeAdmin,ApeUI,插件,AI,管理后台,RBAC,MCP",
                service_fee_rate=30.0,
            ))

        # ── 2. 内容区块（9 个 block，对应首页 9 个区块） ──
        content_count = (await db.execute(select(func.count()).select_from(ApeUiSiteContent))).scalar() or 0
        if content_count == 0:
            blocks = [
                dict(block_key="hero", title="ApeAdmin",
                     subtitle="面向 AI 智能体场景的开发框架",
                     body="企业级 AI 原生管理底座，让插件化开发像搭积木一样简单",
                     sort=0, enabled=True,
                     extra={"badge": "v0.1.0", "cta_primary": "开始使用", "cta_link": "/apeui/docs.html",
                            "cta_secondary": "插件市场", "cta_link2": "/apeui/plugins.html",
                            "stats": [{"label": "RBAC 权限", "value": "细粒度"},
                                      {"label": "插件生态", "value": "73+"},
                                      {"label": "MCP 网关", "value": "内置"},
                                      {"label": "开源", "value": "100%"}]}),
                dict(block_key="features", title="核心特性", subtitle="为 AI 智能体场景而生的全栈能力",
                     sort=1, enabled=True, extra={"items": [
                         {"icon": "🔐", "title": "RBAC 权限", "desc": "细粒度角色/菜单/按钮权限"},
                         {"icon": "🧩", "title": "插件化架构", "desc": "ZIP 上传安装，运行时热拔插"},
                         {"icon": "🤖", "title": "MCP 网关", "desc": "AI 模型上下文协议工具注册"},
                         {"icon": "💬", "title": "AI 对话", "desc": "集成多模型对话引擎"},
                         {"icon": "📝", "title": "审计日志", "desc": "全链路操作审计"},
                         {"icon": "🎨", "title": "UI 组件库", "desc": "Vue3 + Element Plus 响应式"},
                     ]}),
                dict(block_key="architecture", title="架构设计", sort=2, enabled=True,
                     extra={"nodes": ["Vue3 前端", "FastAPI 底座", "业务插件"]}),
                dict(block_key="mcp", title="MCP 网关", sort=3, enabled=True,
                     extra={"points": ["工具注册", "资源管理", "权限过滤", "审计日志"]}),
                dict(block_key="techstack", title="技术栈", sort=4, enabled=True, extra={"items": [
                    {"cat": "前端", "items": ["Vue3", "Vite", "Element Plus", "ECharts"]},
                    {"cat": "后端", "items": ["FastAPI", "SQLAlchemy 2.0", "Pydantic V2"]},
                    {"cat": "数据库", "items": ["SQLite/MySQL", "Redis(可选)"]},
                    {"cat": "工具链", "items": ["Ruff", "Pytest", "Uvicorn"]},
                ]}),
                dict(block_key="plugin_eco", title="插件生态", sort=5, enabled=True, extra={"items": [
                    {"icon": "🔄", "title": "生命周期管理", "desc": "安装/启用/禁用/卸载"},
                    {"icon": "📦", "title": "ZIP 安装", "desc": "一键上传安装插件包"},
                    {"icon": "🔌", "title": "能力开放", "desc": "路由/MCP/事件/菜单全注册"},
                ]}),
                dict(block_key="quickstart", title="快速开始", sort=6, enabled=True,
                     extra={"steps": ["git clone", "pip install", "python run"]}),
                dict(block_key="cta", title="开始构建你的 AI 中后台", sort=7, enabled=True,
                     extra={"btn_text": "GitHub Star", "btn_link": "https://github.com/KevinLiss/ApeAdmin"}),
                dict(block_key="footer", title="ApeAdmin", sort=99, enabled=True,
                     extra={"text": "© 2026 ApeAdmin · 面向 AI 智能体场景的开发框架"}),
            ]
            for b in blocks:
                db.add(ApeUiSiteContent(**b))

        # ── 3. 文档分类（5 组） ──
        cat_count = (await db.execute(select(func.count()).select_from(ApeUiDocCategory))).scalar() or 0
        if cat_count == 0:
            cats = [
                dict(name="入门", description="快速上手 ApeAdmin", sort=1),
                dict(name="核心架构", description="框架设计原理", sort=2),
                dict(name="插件开发", description="插件开发指南", sort=3),
                dict(name="MCP 网关", description="AI 工具集成", sort=4),
                dict(name="配置与运维", description="部署与运维", sort=5),
            ]
            for c in cats:
                db.add(ApeUiDocCategory(**c))
            await db.flush()

        # ── 4. 文档（15 篇，对应 docs.html 侧边栏） ──
        doc_count = (await db.execute(select(func.count()).select_from(ApeUiDoc))).scalar() or 0
        if doc_count == 0:
            cat_map = {c.name: c.id for c in (await db.execute(select(ApeUiDocCategory))).scalars().all()}
            docs = [
                dict(category_id=cat_map["入门"], title="项目简介", slug="intro", sort=1,
                     summary="ApeAdmin 是什么", body="# 项目简介\n\nApeAdmin 是面向 AI 智能体场景的开发框架。"),
                dict(category_id=cat_map["入门"], title="快速开始", slug="quickstart", sort=2,
                     summary="5 分钟上手", body="# 快速开始\n\n```bash\ngit clone ...\npip install -r requirements.txt\npython run.py\n```"),
                dict(category_id=cat_map["入门"], title="默认账号", slug="account", sort=3,
                     summary="内置管理员", body="# 默认账号\n\nadmin / admin123"),
                dict(category_id=cat_map["核心架构"], title="目录结构", slug="architecture", sort=4,
                     summary="项目目录", body="# 目录结构\n\n```\napeadmin/\n├── backend/\n└── frontend/\n```"),
                dict(category_id=cat_map["核心架构"], title="设计原则", slug="principles", sort=5,
                     summary="架构理念", body="# 设计原则\n\n插件化、热拔插、AI 原生。"),
                dict(category_id=cat_map["核心架构"], title="技术栈", slug="techstack", sort=6,
                     summary="技术选型", body="# 技术栈\n\nVue3 + FastAPI + SQLAlchemy"),
                dict(category_id=cat_map["插件开发"], title="创建插件", slug="plugin-create", sort=7,
                     summary="插件骨架", body="# 创建插件\n\n创建 plugin.json + plugin.py"),
                dict(category_id=cat_map["插件开发"], title="插件接口", slug="plugin-api", sort=8,
                     summary="PluginInterface", body="# 插件接口\n\ninstall/uninstall/register"),
                dict(category_id=cat_map["插件开发"], title="事件总线", slug="plugin-events", sort=9,
                     summary="EventBus", body="# 事件总线\n\non/emit/off"),
                dict(category_id=cat_map["MCP 网关"], title="网关概览", slug="mcp-overview", sort=10,
                     summary="MCP 架构", body="# MCP 网关\n\n模型上下文协议"),
                dict(category_id=cat_map["MCP 网关"], title="内置工具", slug="mcp-tools", sort=11,
                     summary="内置 MCP 工具", body="# 内置工具\n\nCRUD 工具"),
                dict(category_id=cat_map["MCP 网关"], title="注册工具", slug="mcp-register", sort=12,
                     summary="插件注册 MCP", body="# 注册工具\n\nmcp_manager.register_tool()"),
                dict(category_id=cat_map["配置与运维"], title="配置说明", slug="config", sort=13,
                     summary="配置项", body="# 配置说明\n\n.env 配置"),
                dict(category_id=cat_map["配置与运维"], title="AI 模型配置", slug="ai-config", sort=14,
                     summary="模型 Key", body="# AI 模型配置\n\nDeepSeek / OpenAI"),
                dict(category_id=cat_map["配置与运维"], title="贡献指南", slug="contribute", sort=15,
                     summary="参与贡献", body="# 贡献指南\n\nFork → PR"),
            ]
            for d in docs:
                db.add(ApeUiDoc(**d))

        # ── 5. 演示插件（18 个，对应 plugins.html PLUGINS 数组） ──
        plugin_count = (await db.execute(select(func.count()).select_from(ApeUiPlugin))).scalar() or 0
        if plugin_count == 0:
            plugins = [
                dict(name="ai-chat-engine", display_name="AI Chat Engine", slug="ai-chat-engine",
                     category="ai", version="2.1.0", price=0, tags="AI,SSE,多模型",
                     icon="🤖", summary="多模型对话引擎，支持 DeepSeek/通义千问/智谱GLM",
                     description="多模型对话引擎，支持 DeepSeek/通义千问/智谱GLM，流式 SSE 输出与 Function Calling。",
                     download_count=12300, rating_avg=4.9, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="code-graph-analyzer", display_name="Code Graph Analyzer", slug="code-graph-analyzer",
                     category="dev", version="1.4.2", price=0, tags="AST,tree-sitter,分析",
                     icon="🔍", summary="基于 tree-sitter AST 解析的代码图谱工具",
                     description="基于 tree-sitter AST 解析的代码图谱工具，支持多语言项目结构与依赖分析。",
                     download_count=8700, rating_avg=4.7, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="doc-generator", display_name="Doc Generator", slug="doc-generator",
                     category="dev", version="3.0.1", price=99, tags="DOCX,PPT,Excel",
                     icon="📄", summary="一键生成 DOCX/PPT/Excel 三件套",
                     description="一键生成 DOCX/PPT/Excel 三件套，自动从代码注释提取文档结构。",
                     download_count=15200, rating_avg=4.8, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="rag-knowledge-base", display_name="RAG Knowledge Base", slug="rag-knowledge-base",
                     category="ai", version="2.0.0", price=199, tags="RAG,向量,检索",
                     icon="📚", summary="TF-IDF + 向量索引双引擎 RAG 知识库",
                     description="TF-IDF + 向量索引双引擎 RAG 知识库，支持文档分块、语义检索与引用溯源。",
                     download_count=9100, rating_avg=4.6, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="sandbox-code-runner", display_name="Sandbox Code Runner", slug="sandbox-code-runner",
                     category="dev", version="1.2.3", price=0, tags="沙盒,隔离,安全",
                     icon="🛡️", summary="云端 AI 沙盒执行环境",
                     description="云端 AI 沙盒执行环境，路径隔离 + 命令白/黑名单双重防护，安全运行用户代码。",
                     download_count=6400, rating_avg=4.5, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="system-monitor", display_name="System Monitor", slug="system-monitor",
                     category="sys", version="1.8.0", price=0, tags="psutil,监控,仪表盘",
                     icon="📊", summary="基于 psutil 的系统监控面板",
                     description="基于 psutil 的系统监控面板，实时 CPU/内存/磁盘/网络，支持历史曲线与告警。",
                     download_count=11000, rating_avg=4.7, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="project-preview", display_name="Project Preview", slug="project-preview",
                     category="dev", version="1.5.1", price=0, tags="预览,Vite,实时",
                     icon="👁️", summary="项目实时预览",
                     description="项目实时预览，支持 Vite/Webpack 项目自动检测与一键启动预览服务。",
                     download_count=5800, rating_avg=4.4, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="data-masking", display_name="Data Masking", slug="data-masking",
                     category="data", version="1.1.0", price=0, tags="脱敏,隐私,规则",
                     icon="🔐", summary="数据脱敏规则管理",
                     description="数据脱敏规则管理，支持手机号/身份证/邮箱等自动脱敏与自定义规则配置。",
                     download_count=4200, rating_avg=4.3, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="smart-routing", display_name="Smart Routing", slug="smart-routing",
                     category="ai", version="2.3.0", price=0, tags="路由,自动,意图",
                     icon="🧭", summary="AI 引擎按消息内容自动路由模型",
                     description="AI 引擎按消息内容自动路由模型，根据对话意图智能选择最匹配的大模型。",
                     download_count=7900, rating_avg=4.6, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="log-dashboard", display_name="Log Dashboard", slug="log-dashboard",
                     category="sys", version="1.6.0", price=0, tags="日志,审计,追踪",
                     icon="📋", summary="操作日志可视化面板",
                     description="操作日志可视化面板，按模块/时间/用户多维筛选，支持请求链路追踪。",
                     download_count=6700, rating_avg=4.5, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="ui-theme-studio", display_name="UI Theme Studio", slug="ui-theme-studio",
                     category="ui", version="1.3.0", price=0, tags="主题,CSS,响应式",
                     icon="🎨", summary="深色/浅色主题自定义工作室",
                     description="深色/浅色主题自定义工作室，CSS 变量体系，768px 断点 PC/H5 自适应。",
                     download_count=5100, rating_avg=4.4, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="plugin-manager-pro", display_name="Plugin Manager Pro", slug="plugin-manager-pro",
                     category="sys", version="2.0.0", price=0, tags="管理,ZIP,生命周期",
                     icon="📦", summary="插件管理增强版",
                     description="插件管理增强版，ZIP 上传导入、生命周期可视化、一键启用禁用与依赖检查。",
                     download_count=8300, rating_avg=4.8, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="form-designer", display_name="Form Designer", slug="form-designer",
                     category="ui", version="1.0.2", price=0, tags="表单,拖拽,EP",
                     icon="📝", summary="可视化表单设计器",
                     description="可视化表单设计器，拖拽生成 Element Plus 表单，支持校验规则与自定义组件。",
                     download_count=3900, rating_avg=4.2, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="api-tester", display_name="API Tester", slug="api-tester",
                     category="dev", version="1.4.0", price=0, tags="API,REST,测试",
                     icon="🔌", summary="内置 API 测试工具",
                     description="内置 API 测试工具，支持 REST/GraphQL，自动生成请求模板与断言。",
                     download_count=5500, rating_avg=4.3, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="cron-scheduler", display_name="Cron Scheduler", slug="cron-scheduler",
                     category="sys", version="1.2.0", price=0, tags="定时,cron,调度",
                     icon="⏰", summary="定时任务管理插件",
                     description="定时任务管理插件，支持 cron 表达式与一次性任务，可视化运行日志。",
                     download_count=4800, rating_avg=4.4, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="data-export-kit", display_name="Data Export Kit", slug="data-export-kit",
                     category="data", version="1.1.0", price=0, tags="导出,Excel,CSV",
                     icon="📤", summary="数据导出工具包",
                     description="数据导出工具包，支持 CSV/Excel/JSON 多格式，大数据量分页流式导出。",
                     download_count=6000, rating_avg=4.5, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="chat-widget", display_name="Chat Widget", slug="chat-widget",
                     category="biz", version="1.0.0", price=0, tags="聊天,浮窗,Markdown",
                     icon="💬", summary="可嵌入的 AI 对话浮窗组件",
                     description="可嵌入的 AI 对话浮窗组件，Markdown 实时渲染 + 代码高亮，支持多会话管理。",
                     download_count=3500, rating_avg=4.3, status=PluginStatus.APPROVED, developer_id=1),
                dict(name="workflow-engine", display_name="Workflow Engine", slug="workflow-engine",
                     category="biz", version="2.1.0", price=0, tags="工作流,编排,自动化",
                     icon="🔄", summary="可视化工作流编排引擎",
                     description="可视化工作流编排引擎，节点拖拽连线、条件分支、支持自定义节点与 Webhook 触发。",
                     download_count=7200, rating_avg=4.7, status=PluginStatus.APPROVED, developer_id=1),
            ]
            for p in plugins:
                db.add(ApeUiPlugin(**p))

        await db.commit()
    logger.info("ApeUI seed data ready")
