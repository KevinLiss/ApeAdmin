# 平台概览

ApeAdmin 是一个前后端分离的管理底座：后端使用 FastAPI，数据访问使用 SQLAlchemy 2.0 异步会话，前端使用 Vue 3、TypeScript、Vite 和 Element Plus。业务能力通过插件扩展，核心只负责通用的认证、权限、菜单、日志、数据访问和 AI 能力。

## 解决什么问题

- 用统一的用户、角色、菜单和接口权限支撑中后台业务。
- 用插件包隔离业务代码，支持运行时启用、停用和资源回收。
- 用 MCP 将可授权的管理能力暴露给 AI Agent。
- 用统一的异常响应、请求追踪和操作日志降低排查成本。

## 运行边界

```text
浏览器
  ├─ Vue 管理台（/）
  └─ Apehub_web 官网（/apehub-web）
          │
          └─ FastAPI（/api/v1）
               ├─ 核心 API：auth / user / role / menu / dept / plugin
               ├─ MCP：tools / resources / prompts / audit-logs
               └─ 插件 API：由插件自行挂载
```

Apehub_web 是一个普通的 ApeAdmin 插件：它提供官网、插件市场、开发者中心和官网管理 API，但不修改核心路由生成规则。插件启用时挂载 `/api/v1/apehub-web` 和 `/apehub-web`；停用时由插件管理器移除其运行时资源并隐藏插件菜单。

## 目录速览

| 目录 | 责任 |
| --- | --- |
| `backend/src/api` | 核心 HTTP 路由 |
| `backend/src/core` | 配置、安全、依赖注入、中间件、种子数据 |
| `backend/src/db` | 异步引擎、会话和数据库初始化 |
| `backend/src/models` | 核心 ORM 模型 |
| `backend/src/crud` | 通用 CRUD 与 RBAC 数据操作 |
| `backend/src/plugins` | 插件接口、发现、安装、热启停和资源跟踪 |
| `backend/src/mcp` | MCP 工具、资源、提示词和审计 |
| `backend/src/ai` | 多模型对话和工具调用循环 |
| `frontend/src/router` | 静态路由、动态菜单路由和权限守卫 |
| `frontend/src/views` | Vue 页面，路径必须与菜单 component 对应 |

## 关键原则

1. 核心能力放在 `backend/src`，业务能力放在插件目录。
2. 插件的菜单、接口、数据表和静态资源必须使用自己的命名空间。
3. 页面权限只用于前端体验，后端接口必须再次校验权限。
4. 生产环境使用迁移脚本；`init_db()` 仅用于开发环境首次启动。
