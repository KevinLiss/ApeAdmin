# 架构与请求链路

## 应用启动

`backend/src/main.py` 的 lifespan 按以下顺序启动应用：

1. 初始化日志、中间件和异常处理器。
2. 初始化数据库连接；开发环境可以自动建表。
3. 执行核心种子数据，确保默认部门、角色和菜单存在。
4. 扫描 `backend/src/plugins/builtin`，同步插件元数据和启用状态。
5. 执行启用插件的 `install()`，再注册 HTTP 路由、MCP 工具和事件监听器。
6. 注册 MCP HTTP 路由，发送 `APP_STARTUP` 事件。

关闭应用时，插件会先卸载运行时资源，再关闭数据库连接池。

## 后端分层

```text
HTTP Request
  ↓
Middleware（请求 ID、CORS、异常过滤、操作日志）
  ↓
FastAPI Router
  ↓
Dependency（get_db / get_current_user / require_permission）
  ↓
CRUD / Service
  ↓
SQLAlchemy Model + AsyncSession
```

路由层负责参数校验和响应格式，业务规则放在服务函数中，数据库提交集中在业务操作的事务边界内。统一成功响应格式为 `{ code, msg, data }`；业务异常由全局处理器转换为同样的错误结构。

## 前端路由

管理台启动时先加载用户信息和菜单树。`frontend/src/router/index.ts` 使用 `import.meta.glob('@/views/**/*.vue')` 查找菜单的 `component`：

```text
菜单 component: apehub_web/admin/Config
页面文件:       frontend/src/views/apehub_web/admin/Config.vue
访问路径:       /apehub-web/admin/config
```

组件不存在时不会生成动态路由，用户会进入 404。因此菜单注册、页面文件和权限标识必须作为一个版本交付。

## Apehub_web 的三类接口

| 类型 | 示例 | 鉴权 |
| --- | --- | --- |
| 官网公开接口 | `/api/v1/apehub-web/site/public/*` | 不需要登录 |
| 开发者接口 | `/api/v1/apehub-web/developer/*` | JWT 登录 |
| 后台管理接口 | `/api/v1/apehub-web/admin/*` | JWT + 插件权限 |

公开接口只返回已启用、已发布的数据；开发者接口只允许访问自己的插件；后台接口由 `apehub_web:*` 菜单权限保护。
