---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'c4f4214e-e596-4af3-92d0-afca36ae12fb'
  PropagateID: 'c4f4214e-e596-4af3-92d0-afca36ae12fb'
  ReservedCode1: '7f0720ef-af19-4a09-bed7-09c831e4ed1d'
  ReservedCode2: '7f0720ef-af19-4a09-bed7-09c831e4ed1d'
---

# ApeAdmin

> 基于 FastAPI + Vue3 构建的平台化管理底座，内置 RBAC 权限、插件市场、审计日志。采用微服务插件架构，业务插件以 Docker 服务独立部署，支持插件热启用禁用。集成 MCP-SSE 网关，可将底座与插件能力对外暴露为 AI 工具，适配 Agent 调用，提供完整后台管理与 AI 能力输出能力。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0 (async) + Alembic |
| 前端 | Vue3 + Vite + Element Plus + Pinia |
| 数据库 | MySQL / SQLite（开发模式） |
| 缓存 | Redis（可降级内存） |
| 认证 | JWT (access + refresh token) |
| AI 协议 | MCP (Model Context Protocol) — SSE 传输 |

## 核心特性

### RBAC 权限体系

- 用户 / 角色 / 菜单 / 部门 五表模型
- 四层权限：免登录 → 免鉴权 → 规则鉴权 → 数据范围
- 菜单类型：目录(M) / 菜单(C) / 按钮(F)
- 超管通配权限，普通用户按角色菜单分配

### 微服务插件架构

- 插件以独立 Python 包形式开发，通过 importlib 自动发现
- 业务插件支持 Docker 服务独立部署，与底座解耦
- 完整生命周期：load → install → register → uninstall
- 事件总线（EventBus）支持插件间通信，7 种内置事件
- 插件可注册自有路由、MCP 工具、事件监听器

### MCP-SSE 网关

- 三原语：Tools（工具调用）/ Resources（资源读取）/ Prompts（模板渲染）
- 工具注册时自动从函数签名推断 JSON Schema
- RBAC 权限过滤：AI Agent 只能看到有权限的工具
- 插件可向 MCP 网关注册工具，实现能力对外暴露
- 适配 AI Agent 调用场景

### 审计日志

- 请求链路追踪（RequestContextMiddleware）
- 操作日志记录
- 请求耗时监控

## 项目结构

```
apeadmin/
├── backend/                  # FastAPI 后端
│   ├── src/
│   │   ├── api/              # 路由层（auth/user/role/menu/dept）
│   │   ├── core/              # 基础设施（config/security/deps/middleware/exceptions）
│   │   ├── crud/             # 通用 CRUD 基类 + RBAC CRUD
│   │   ├── db/                # 数据库引擎与会话管理
│   │   ├── models/            # ORM 模型（RBAC 五表 + Mixins）
│   │   ├── mcp/               # MCP 协议体系
│   │   ├── plugins/           # 插件系统（Manager + EventBus + 内置示例）
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── cli.py             # 命令行工具
│   │   └── main.py            # 应用入口
│   ├── alembic/               # 数据库迁移
│   └── pyproject.toml
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── api/               # Axios 封装 + 接口定义
│   │   ├── layout/            # 主布局（侧边栏 + 头部）
│   │   ├── router/            # 路由 + 守卫
│   │   ├── stores/            # Pinia 状态管理
│   │   └── views/             # 页面（登录/仪表盘/系统管理/MCP 管理）
│   └── vite.config.ts
└── .gitignore
```

## 快速开始

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e .
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

默认使用 SQLite，无需额外安装数据库。访问 `http://localhost:8000/docs` 查看 API 文档。

### 前端

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

### 默认账号

```
用户名: admin
密码:   admin123
```

## 配置说明

后端配置通过 `.env` 文件或环境变量，关键项：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `DB_TYPE` | sqlite | 数据库类型 (sqlite/mysql) |
| `DB_HOST` | localhost | MySQL 地址 |
| `DB_PORT` | 3306 | MySQL 端口 |
| `REDIS_URL` | redis://localhost:6379/1 | Redis 连接 |
| `JWT_SECRET` | change-me | JWT 签名密钥 |
| `MCP_ENABLED` | true | 是否启用 MCP 网关 |
| `PLUGINS_ENABLED` | true | 是否启用插件系统 |

## License

MIT

> AI生成