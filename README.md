---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '9b1a717d-17a6-4f14-9477-bbbfb34635ee'
  PropagateID: '9b1a717d-17a6-4f14-9477-bbbfb34635ee'
  ReservedCode1: 'f09dfaa5-5d32-4837-808f-69ca1abfbfa9'
  ReservedCode2: 'f09dfaa5-5d32-4837-808f-69ca1abfbfa9'
---

<div align="center">
  <br/>
  <img src="assets/logo.png" width="130" alt="ApeAdmin Logo" />
  <h1>ApeAdmin</h1>
  <p> 面向现代AI应用系统打造 · 100%开源后台管理框架</p>
</div>

<p align="center">
  <a href="http://apehub.finecv.cn/apehub-web">官网地址</a> ·
  <a href="http://apehub.finecv.cn/apehub-web/plugins.html">插件市场</a> ·
  <a href="http://apehub.finecv.cn/apehub-web/docs-portal">快速开始</a> ·
  <a href="#功能特性">功能</a> ·
  <a href="#架构">架构</a> ·
  <a href="#配置说明">配置</a> ·
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.11%2B-orange" alt="python">
  <img src="https://img.shields.io/badge/vue-3.5-brightgreen" alt="vue">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="platform">
</p>

---

> **本项目由 AI 驱动开发，人工负责产品与质量。** ApeAdmin 在 AI 辅助下高效迭代：人类开发者负责产品方向、架构评审、质量验证与最终决策，AI 负责加速实现、测试和文档工作。

---

ApeAdmin 是新时代面向 AI 应用打造的后台开发框架，基于 FastAPI + Vue3 搭建平台化管理底座，跳出传统后台系统的设计思路，原生为 AI Agent 能力调用做适配。

项目支持插件化开发，拥有完善的插件社区生态；内置 RBAC 权限管控、插件市场、审计日志等企业级基础能力。框架集成 MCP-SSE 网关，可把系统底座和业务插件的功能直接封装为标准化 AI 工具供 Agent 调用，实现传统业务系统与大模型智能体的无缝打通，同时保留完整的后台管理能力，帮助开发者快速搭建兼具业务管理与 AI 工具输出能力的应用。

你可以把它理解为一个"开箱即用 + 可插拔扩展"的中后台框架——底座提供权限、菜单、日志等基础设施，业务功能以插件形式独立开发和部署，同时通过 MCP 网关将管理能力暴露给 AI Agent 调用。项目采用 MIT 开源协议。

## 功能特性

### 安装向导

WordPress 式开箱体验，无需手工编辑配置文件：

- **自动检测** —— 首次访问自动跳转 `/setup` 安装向导，已完成安装的系统直接进入后台
- **三步安装** —— 配置数据库 → 配置站点与管理员账号 → 完成安装
- **自动建库** —— MySQL 连接自动检测，数据库不存在时自动创建（utf8mb4）
- **密钥自动生成** —— JWT_SECRET 随机生成并写入 `.env`，无需手工处理
- **安装锁保护** —— 安装完成后写入 `setup.lock`，防止向导被重复执行

### RBAC 权限体系

- **五表模型** —— 用户 / 角色 / 菜单 / 部门 + 关联表，标准 RBAC 基础设施
- **四层权限** —— 免登录 → 免鉴权 → 规则鉴权 → 数据范围（本部门 / 本部门及以下 / 全部）
- **菜单三类型** —— 目录(M) / 菜单(C) / 按钮(F)，支持无限层级树形结构
- **超管通配** —— 超级管理员自动拥有所有权限，普通用户按角色菜单分配
- **前端权限指令** —— `v-permission` 指令控制按钮级显示，路由守卫校验页面级权限

### 微服务插件架构

- **自动发现** —— 插件以 Python 包形式开发，通过 `importlib` 自动扫描发现
- **独立部署** —— 业务插件支持 Docker 服务独立部署，与底座完全解耦
- **完整生命周期** —— `load → install → register → uninstall`，支持热启用禁用
- **事件总线** —— EventBus 支持 7 种内置事件（APP_STARTUP / DB_READY / USER_LOGIN 等），插件间松耦合通信
- **ZIP 安装** —— 支持上传 ZIP 包导入插件，无需手动放置文件
- **插件市场** —— 在线浏览、搜索、下载社区插件，开发者发布插件与安装包
- **能力注册** —— 插件可注册自有路由、MCP 工具、事件监听器

### MCP-SSE 网关

将底座与插件的管理能力对外暴露为 AI Agent 可调用的工具：

- **三原语** —— Tools（工具调用）/ Resources（资源读取）/ Prompts（模板渲染）
- **自动 Schema** —— 工具注册时自动从函数签名推断 JSON Schema，无需手写
- **RBAC 过滤** —— AI Agent 只能看到当前用户有权限调用的工具
- **安全传输** —— SSE 一次性 ticket 认证（替代 URL 裸 JWT），工具调用 30s 超时保护
- **持久化恢复** —— 插件注册信息持久化，服务重启后自动恢复 MCP 工具注册
- **审计日志** —— 每次工具调用自动记录请求、响应、耗时、调用者
- **插件扩展** —— 插件可向 MCP 网关注册工具，实现能力级对外开放

内置 MCP 工具：

| 工具 | 说明 |
|------|------|
| `system_health_check` | 系统健康检查 |
| `system_list_plugins` | 列出已安装插件 |
| `role_list / create / update / delete` | 角色管理（需权限） |
| `dept_list / create / update / delete` | 部门管理（需权限） |
| `menu_list / create / update / delete` | 菜单管理（需权限） |

### AI 对话

- **多模型支持** —— DeepSeek / 通义千问 / 智谱 GLM / OpenAI / 自定义端点，OpenAI 兼容接口
- **流式 SSE** —— 流式输出 + Markdown 实时渲染 + 代码高亮
- **Function Calling** —— AI 可调用 MCP 工具完成管理操作，最多 5 轮工具调用循环
- **密钥管理** —— 后台管理 AI 供应商密钥，Fernet 加密存储（密钥派生自 JWT_SECRET）

### 审计日志

- **请求链路追踪** —— RequestContextMiddleware 全局唯一请求 ID
- **操作日志** —— 记录用户操作行为，支持按模块、时间、用户筛选
- **请求耗时监控** —— 自动记录每个 API 请求耗时

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0 (async) + Alembic |
| 前端 | Vue 3.5 + Vite 6 + TypeScript 5.7 + Element Plus 2.9 |
| 状态管理 | Pinia 2.3 |
| 图表 | ECharts 5.6 + vue-echarts |
| 数据库 | MySQL（aiomysql）/ SQLite（aiosqlite）双驱动自动切换 |
| 缓存 | Redis（可选，缺失自动降级内存） |
| 认证 | JWT（access token）+ bcrypt 密码哈希 |
| AI 协议 | MCP (Model Context Protocol) — SSE 传输 |
| AI 模型 | DeepSeek / 通义千问 / 智谱 GLM / OpenAI（OpenAI 兼容接口） |

## 快速开始

### 方式一：安装向导（推荐）

无需手工配置，浏览器里点几下即可完成安装：

```bash
# 1. 启动后端
cd backend
python -m venv .venv && .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 2. 启动前端（开发模式）
cd frontend
npm install --legacy-peer-deps
npm run dev
```

打开 `http://localhost:5173`，系统检测到未安装会自动进入安装向导：

1. **配置数据库** —— 选择 SQLite（零配置）或 MySQL（填连接信息，可自动建库）
2. **配置站点** —— 站点名称、管理员账号密码、访问地址
3. **完成安装** —— 写入配置并建表，按提示重启后端，重启后自动初始化管理员账号与基础数据

> SQLite 适合本地开发和轻量部署；MySQL 适合生产环境与多服务场景。

### 方式二：生产部署

服务器（宝塔面板 / Docker / 裸机 Nginx）一键部署方案、部署包构建、SQLite→MySQL 数据迁移，见 **[deploy/DEPLOY.md](deploy/DEPLOY.md)**。

部署包只包含管理后台底座（RBAC / 菜单 / 插件框架 / MCP 网关），不含业务插件，首次启动进入安装向导。业务插件通过后台的插件导入机制按需安装（上传 ZIP 包 / 插件市场在线安装），与部署包解耦：

### 默认体验路径

1. 登录后台（安装向导中设置的管理员账号）
2. 系统管理 → 用户 / 角色 / 菜单 / 部门 / 插件管理
3. MCP 管理 → 工具 / 资源 / 提示词 / 调用日志
4. AI 助手 → 配置模型密钥后即可对话

## 架构

ApeAdmin 是一个前后端分离的单体应用，后端插件化扩展，内置安装向导：

```
apeadmin/
  backend/                       # FastAPI 后端
    src/
      api/                       # 路由层
        auth.py                  # 认证（登录/登出/用户信息）
        user.py                  # 用户管理
        role.py                  # 角色管理
        menu.py                  # 菜单管理（树形）
        dept.py                  # 部门管理（树形）
        plugin.py                # 插件管理
        ai_provider.py           # AI 模型密钥管理
        chat.py                  # AI 对话（流式 SSE）
        dashboard.py             # 仪表盘统计
        log.py                   # 系统日志
      core/                      # 基础设施
        config.py                # 配置（pydantic-settings）
        security.py              # 密码哈希 + JWT
        deps.py                  # 依赖注入
        middleware.py            # 中间件（CORS / 请求追踪）
        seed.py                  # 种子数据初始化
        crypto.py                # API Key 加密
      crud/                      # 泛型 CRUD 基类 + RBAC CRUD
      db/                        # 数据库引擎与会话管理
      models/                    # ORM 模型
        rbac.py                  # RBAC 五表
        ai.py                    # AI 供应商
        plugin.py                # 插件记录
        mcp.py                   # MCP 审计日志
        log.py                   # 系统日志
      mcp/                       # MCP 协议体系
        manager.py               # 工具/资源/提示词管理 + RBAC 过滤
        routes.py                # MCP HTTP 路由 + 审计日志
        builtin_resources.py     # 内置工具/资源/提示词
      plugins/                   # 插件系统
        base.py                  # PluginInterface + EventBus
        manager.py               # 插件发现/加载/安装/卸载
        builtin/                 # 内置插件（按需放入，目录动态扫描）
          dev_example/           # 插件开发示例
      setup_wizard/              # 安装向导（未安装时挂载）
        state.py                 # 安装状态（setup.lock / .env 读写）
        api.py                   # 向导 API（状态/测试连接/执行安装）
        setup.html               # 向导页面
      ai/                        # AI 智能体
        agent.py                 # 多模型对话 + 工具调用循环
        tools.py                 # MCP 工具列表构建
      schemas/                   # Pydantic 请求/响应模型
      main.py                    # 应用入口（lifespan + setup 模式切换）
      cli.py                     # 命令行工具
    alembic/                     # 数据库迁移
    pyproject.toml

  frontend/                      # Vue3 前端
    src/
      api/                       # Axios 封装 + 全部接口定义
      components/                # ApeHeader / ApeSidebar
      composables/               # useTheme（深色/浅色切换）
      directives/                # v-permission 权限指令
      layout/                    # 主布局
      router/                    # 路由 + 守卫 + 动态路由生成
      stores/                    # Pinia（用户状态/权限/菜单）
      styles/                    # 全局样式
      views/                     # 页面
        login/                   # 登录
        system/                  # 系统管理（用户/角色/菜单/部门/文件/插件/日志/设置/个人中心）
        mcp/                     # MCP 管理（工具/资源/提示词/审计日志）
        ai/                      # AI 助手（对话/模型密钥管理）
        error/                   # 异常页（404 等）

  deploy/                        # 部署物料
    DEPLOY.md                    # 生产部署文档（宝塔/Docker/Nginx）
    build_deploy_package.sh      # 部署包构建脚本（底座版/完整版）
    nginx/                       # Nginx 站点配置模板
    scripts/                     # 服务器端部署/管理脚本
```

### 设计原则

1. **安装即用** —— 未安装时自动进入 `/setup` 向导，配置写 `.env`、建表自动完成，安装锁防止重复执行；安装阶段只建表不跑种子数据，种子在重启后以新密钥执行，避免加密密钥不一致
2. **底座与插件解耦** —— 底座提供 RBAC、日志、MCP 网关等基础设施，业务功能全部以插件形式开发，互不依赖
3. **双数据库驱动** —— 开发用 SQLite 零配置启动，生产用 MySQL，通过 `DB_TYPE` 环境变量切换
4. **Redis 可选** —— 缓存层缺失时自动降级为内存字典，不影响功能
5. **权限贯穿 AI** —— MCP 工具调用和 AI Function Calling 均受 RBAC 权限控制，AI Agent 只能操作有权限的资源
6. **动态路由** —— 前端路由从后端菜单树动态生成，菜单增减无需改前端代码

## 插件开发

### 创建插件

在 `backend/src/plugins/builtin/` 下创建 Python 包：

```
my_plugin/
  __init__.py
  plugin.py          # 插件入口（实现 PluginInterface）
  models.py          # ORM 模型（可选）
  api.py             # 路由（可选）
  services.py        # 业务逻辑（可选）
```

### 插件接口

```python
from src.plugins.base import PluginInterface, PluginInfo, EventBus, Event

class MyPlugin(PluginInterface):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="my-plugin",
            version="1.0.0",
            description="我的第一个插件",
            author="Your Name",
        )

    def on_load(self):
        """插件加载时调用"""
        pass

    def on_install(self):
        """插件安装时调用（可创建数据库表）"""
        pass

    def register_routes(self, app):
        """注册 FastAPI 路由"""
        @app.get("/api/v1/my-plugin/hello")
        def hello():
            return {"msg": "Hello from MyPlugin!"}

    def register_mcp_tools(self, mcp_manager):
        """注册 MCP 工具，暴露给 AI Agent 调用"""
        @mcp_manager.tool("my_plugin_greet", "问候工具")
        def greet(name: str) -> dict:
            """向指定用户问候"""
            return {"message": f"Hello, {name}!"}

    def on_event(self, event: Event, *args, **kwargs):
        """监听事件总线事件"""
        if event == Event.USER_LOGIN:
            print(f"用户登录: {kwargs.get('username')}")
```

### 事件类型

| 事件 | 触发时机 |
|------|----------|
| `APP_STARTUP` | 应用启动 |
| `APP_SHUTDOWN` | 应用关闭 |
| `DB_READY` | 数据库初始化完成 |
| `USER_LOGIN` | 用户登录 |
| `USER_LOGOUT` | 用户登出 |
| `BEFORE_REQUEST` | 请求处理前 |
| `AFTER_REQUEST` | 请求处理后 |

## 配置说明

通过安装向导可自动生成 `.env`；手工配置时参考下表（后端目录 `.env` 文件或环境变量）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DB_TYPE` | sqlite | 数据库类型 (sqlite / mysql) |
| `DB_HOST` | localhost | MySQL 地址 |
| `DB_PORT` | 3306 | MySQL 端口 |
| `DB_USER` | root | MySQL 用户名 |
| `DB_PASSWORD` | — | MySQL 密码 |
| `DB_NAME` | apeadmin | 数据库名 |
| `REDIS_URL` | redis://localhost:6379/1 | Redis 连接（可选） |
| `JWT_SECRET` | change-me-in-production... | JWT 签名密钥（向导安装时自动生成） |
| `JWT_EXPIRE_MINUTES` | 1440 | Token 有效期（分钟） |
| `CORS_ORIGINS` | localhost:5173,localhost:8000 | CORS 白名单 |
| `ADMIN_PATH` | /admin | 管理后台访问路径 |
| `SITE_URL` | — | 站点对外访问地址 |
| `MCP_ENABLED` | true | 是否启用 MCP 网关 |
| `PLUGINS_ENABLED` | true | 是否启用插件系统 |
| `SUPER_ADMIN_USERNAME` | admin | 超管用户名 |
| `SUPER_ADMIN_PASSWORD` | admin123 | 超管密码 |

### AI 模型配置

在管理后台 → AI 助手 → 模型密钥管理中添加：

| 供应商 | 默认模型 | Base URL |
|--------|----------|----------|
| DeepSeek | deepseek-chat | `https://api.deepseek.com` |
| 通义千问 | qwen-plus | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 智谱 GLM | glm-4-flash | `https://open.bigmodel.cn/api/paas/v4` |
| OpenAI | gpt-4o-mini | `https://api.openai.com/v1` |
| 自定义 | — | 任意 OpenAI 兼容端点 |

## 系统截图

<table>
  <tr>
    <td width="50%" align="center">
      <img src="assets/screenshots/login.png" alt="登录页" /><br/>
      <sub><b>登录页</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="assets/screenshots/dashboard.png" alt="监控仪表盘" /><br/>
      <sub><b>监控仪表盘</b></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <img src="assets/screenshots/plugins.png" alt="插件市场" /><br/>
      <sub><b>插件市场</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="assets/screenshots/system.png" alt="系统管理" /><br/>
      <sub><b>系统管理</b></sub>
    </td>
  </tr>
</table>

## 贡献指南

欢迎贡献！

### 如何贡献

1. **Fork** 仓库
2. 克隆你的 fork：
   ```bash
   git clone https://github.com/<你的用户名>/ApeAdmin.git
   cd ApeAdmin
   ```
3. 创建分支：
   ```bash
   git checkout -b feat/your-feature
   ```
4. 修改代码，确保能运行：
   ```bash
   # 后端
   cd backend && pip install -e . && uvicorn src.main:app --reload

   # 前端
   cd frontend && npm install --legacy-peer-deps && npm run dev
   ```
5. 清晰地写 commit：
   ```bash
   git commit -m "feat: add xxx support"
   ```
6. **Push** 并向 `master` 分支提交 **Pull Request**

### 分支命名

| 前缀 | 用途 |
|------|------|
| `feat/` | 新功能 |
| `fix/` | Bug 修复 |
| `refactor/` | 重构（不改变行为） |
| `docs/` | 仅文档 |
| `chore/` | 构建、CI、工具链 |

### 约定

- 插件保持独立，不直接依赖其他插件
- 破坏性操作必须需要用户确认
- API 遵循 RESTful 风格，前缀 `/api/v1`
- 提交前确保后端可启动、前端可编译

## 社区交流

---

用微信扫描下方二维码联系作者加入 ApeAdmin 用户群，反馈问题、分享使用心得，和其他用户、维护者一起交流：

<p align="center">
  <img src="assets/wechat-group-qr.png" alt="微信用户群二维码" width="220">
</p>