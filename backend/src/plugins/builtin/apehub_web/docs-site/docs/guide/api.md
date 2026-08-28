# API 约定

## 地址与响应

核心 API 前缀由 `settings.API_PREFIX` 配置，默认是 `/api/v1`。Apehub_web API 在此基础上使用 `/apehub-web` 前缀。

成功响应格式为 `{ code, msg, data }`。业务错误使用 `401`（登录态无效）、`403`（权限不足）、`404`（资源不存在）、`409`（状态冲突）和 `422`（参数校验失败）。

## 认证

需要登录的请求携带：

```http
Authorization: Bearer <access_token>
```

核心依赖 `get_current_user` 校验 JWT、用户状态和用户记录。后台权限接口还需要 `require_permission("system:user:list")` 这类权限依赖；插件接口应使用自己的 `apehub_web:*` 权限标识。

## 核心接口分组

| 分组 | 作用 |
| --- | --- |
| `/auth` | 登录、刷新令牌、当前用户信息 |
| `/users` | 用户管理 |
| `/roles` | 角色和菜单权限 |
| `/menus` | 菜单树和动态路由来源 |
| `/depts` | 部门和数据范围 |
| `/plugins` | 插件发现、热启停、上传和卸载 |
| `/mcp` | 工具、资源、提示词和审计 |
| `/apehub-web/site/public` | 官网公开数据 |
| `/apehub-web/developer` | 插件开发者工作台 |
| `/apehub-web/admin` | 官网和市场后台管理 |

## 编写插件 API

插件路由应在插件自己的 `register()` 中挂载，使用 Pydantic 请求模型和统一异常类型。不要在公开接口返回密钥、内部文件路径或未发布版本数据；文件路径必须经过目录边界校验。
