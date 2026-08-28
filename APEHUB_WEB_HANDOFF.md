# Apehub_web 插件开发交接文档

> 文档版本：2026-08-28  
> 对应代码：ApeAdmin 当前工作区，插件版本 `apehub_web 1.4.0`  
> 适用对象：后续开发、联调、测试、部署和插件打包人员

## 1. 项目定位

`apehub_web` 是 ApeAdmin 官方官网与插件市场插件，采用 ApeAdmin 的热拔插件机制交付，不是独立站点。

插件包含四类能力：

1. 官网首页、插件市场、插件详情、技术文档、个人中心。
2. 开发者上传插件包、维护版本和文档、提交审核。
3. 管理员审核、发布、下架插件，查看文件、订单、安装和收益数据。
4. USDT 订单、退款保护期、收益结算和 TRC20 人工提现。

## 2. 当前代码位置

```text
backend/src/plugins/builtin/apehub_web/
  plugin.json                         插件清单，当前版本 1.4.0
  plugin.py                           安装、卸载、API 和静态资源注册
  api.py                              官网、开发者、后台、订单和提现 API
  models.py                           apehub_web_* 数据模型
  schemas.py                          请求和响应模型
  services.py                         邮件、签名、金额及业务辅助函数
  analysis.py                         DeepSeek 文档分析任务
  seed.py                             默认配置、菜单、权限和示例数据
  migrations/                         v0001-v0008 插件迁移
  frontend/src/views/...              七个 ApeAdmin 后台 Vue 页面
  static/                             官网静态页面和运行时脚本
  docs-site/docs/                     VitePress 源文档
  static/docs-portal/                 VitePress 构建后的发布资源
```

宿主前端还需要同步包含：

```text
frontend/src/api/apehub_web.ts
frontend/src/views/apehub_web/admin/
  Config.vue Content.vue Docs.vue Plugins.vue
  Orders.vue Withdrawals.vue Users.vue
```

## 3. 运行入口与访问地址

后端开发启动：

```bash
cd backend
source .venv/bin/activate       # Windows 使用 .venv\\Scripts\\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

本地地址：

| 用途 | 地址 |
|---|---|
| 官网 | `http://127.0.0.1:8000/apehub-web/` |
| 插件市场 | `http://127.0.0.1:8000/apehub-web/plugins.html` |
| 插件详情 | `http://127.0.0.1:8000/apehub-web/plugin-detail.html?id={id}` |
| 技术文档 | `http://127.0.0.1:8000/apehub-web/docs-portal/` |
| 个人中心 | `http://127.0.0.1:8000/apehub-web/profile.html` |
| ApeAdmin 前端 | `http://127.0.0.1:5173/` |
| API 文档 | `http://127.0.0.1:8000/docs` |

官网静态资源和 API 均由插件注册，插件停用后应一起不可用。文档站是随插件打包的 VitePress 静态资源，不会单独注册服务或改变热拔模式。

## 4. API 边界

API 前缀为 `/api/v1/apehub-web`，按鉴权分为：

| 分组 | 主要接口 | 鉴权 |
|---|---|---|
| 公共官网 | `/site/public/config`、`content`、`navigation`、`docs`、`plugins` | 免登录，仅返回公开数据 |
| 账号 | `/site/auth/register/code`、`register` | 注册验证码、邮箱和密码校验 |
| 开发者 | `/developer/plugins/**` | JWT，只能访问自己的插件 |
| 用户 | `/profile`、`/wallet`、`/orders/my`、`/incomes`、`/withdrawals` | JWT，只能访问当前用户数据 |
| 后台 | `/admin/config`、`content`、`docs`、`plugins`、`orders`、`withdrawals`、`users` | JWT + `apehub_web:*` 权限 |
| 文件 | `/files/{id}/download` | 已购买用户或后台授权，路径需校验 |
| 支付 | `/notify` | LemPay 回调验签和订单校验 |

统一响应格式为 `{ code, msg, data }`。前端必须处理加载中、空数据、接口错误、401/403、404 和重复提交状态。

## 5. 已实现能力

### 5.1 插件和菜单

- 插件身份统一为 `apehub_web`。
- API 为 `/api/v1/apehub-web`，静态资源为 `/apehub-web`。
- 数据表使用 `apehub_web_*` 前缀。
- 后台菜单包含官网配置、内容管理、文档管理、插件管理、订单管理、提现审核、用户管理。
- 七个菜单组件均有对应 Vue 文件，组件路径使用 `apehub_web/admin/*`。
- 插件停用时由宿主隐藏插件菜单；重新启用后恢复。

### 5.2 官网和账号

- 官网配置支持站点信息、SEO、Logo、站点图标、Hero 图片、DeepSeek 和支付配置。
- 导航菜单支持新增、编辑、排序、启停、删除和图标管理。
- 官网公共页面已通过 `site-runtime.js` 读取配置、内容、导航和登录状态。
- 未登录不显示个人中心；登录后个人中心显示在官网右上角。
- 邮箱验证码服务端保存摘要，验证码一次性消费、五分钟过期，并按邮箱/IP 限流。
- 前端发送验证码有 60 秒倒计时，但服务端限制才是最终安全边界。

### 5.3 插件市场闭环基础

- 开发者可以创建插件、创建版本、上传包、文档和截图。
- ZIP 有路径穿越、符号链接、文件数量和大小等基础检查。
- 可以触发 DeepSeek 文档分析并保存 Markdown 结果。
- 版本支持提交审核；后台可查看审核信息、版本文件和源文件树。
- 管理员可审核、发布、下架、删除插件；已产生订单的插件不能直接删除。
- 公共市场只展示已发布内容，插件详情按真实 ID 查询，不使用固定演示回退数据。
- 订单、购买授权、安装统计、下载统计、收入和提现模型已建立。

### 5.4 文档体系

文档采用混合模式：

- ApeAdmin 平台架构文档：VitePress 静态站，源码位于 `docs-site/docs`，发布到 `static/docs-portal`。
- 市场插件文档：存储在插件版本数据中，由开发者维护，详情页按版本展示。

VitePress 文档已覆盖平台概览、架构、本地运行、API、运维、安全、插件生命周期、提交审核、版本和结算。文档右上角只保留“官网首页”，点击使用原生跳转到：

```text
http://127.0.0.1:8000/apehub-web/
```

主题状态使用官网的 `ape-theme` 键同步：官网浅色进入文档为浅色，官网深色进入文档为深色，文档切换后返回官网继续沿用。

## 6. 数据库迁移与生命周期

迁移顺序：

| 迁移 | 作用 |
|---|---|
| `v0001` | 初始官网、文档、插件、订单和提现表 |
| `v0002` | 旧 `apeui_*` 数据迁移到 `apehub_web_*` |
| `v0003` | 邮箱验证码表 |
| `v0004` | 默认 Logo 和首页图片 |
| `v0005` | 清理旧 ApeUI 资源路径 |
| `v0006` | 导航和安装统计 |
| `v0007` | 市场、版本、审核、支付和结算基础表 |
| `v0008` | 文档门户相关数据 |

生命周期约定：

1. `install()` 执行迁移和种子数据，必须幂等。
2. `register()` 注册 API、上传目录和 `/apehub-web` 静态目录。
3. 停用应隐藏菜单并注销运行时资源，但默认保留数据。
4. 卸载时当前实现会删除 `apehub_web_*` 表；生产操作前必须确认是否保留数据并先备份。
5. 重新导入、升级、停用、启用、卸载和重装都要单独验证，不能只验证首次安装。

## 7. 配置和密钥管理

敏感配置只能在 ApeAdmin 后台官网配置页或部署环境变量中管理，不得提交到 Git：

- QQ SMTP 用户、授权码、主机和端口。
- DeepSeek API Key、模型和接口地址。
- LemPay 商户配置。
- JWT、数据库及其他生产凭据。

查询配置时只能返回“已配置/未配置”，不得回传明文。更新时空字符串不能覆盖已有密钥。测试环境可以使用项目管理员提供的凭据，但交付文档和代码仓库不得记录真实值。

结算统一按 USDT 计算，核心金额使用定点/Decimal 语义。当前默认最低提现额为 `100 USDT`，提现手续费、退款期限、收益结算期应以后台配置为准。初期提现采用 TRC20 钱包地址 + 管理员人工打款，不做微信或支付宝自动打款。

## 8. 当前验证记录

已验证：

- `tests/test_apehub_web_marketplace.py`：6 个测试通过。
- VitePress `npm run build`：构建通过。
- `git diff --check`：通过。
- `GET /apehub-web/`：HTTP 200。
- `GET /apehub-web/docs-portal/`：HTTP 200。
- 文档静态产物包含官网返回链接，链接为 `target="_self"`，用于绕过 VitePress 同域内部路由捕获。
- 后端可从当前 SQLite 数据库启动并加载 `apehub_web v1.4.0`；若 8000 端口已被占用，应复用现有服务或先确认进程归属。

环境限制：当前沙箱无法稳定执行真实浏览器点击复测本地地址，浏览器自动化曾被本地安全策略拦截。因此交接方接手后必须在实际浏览器中点击验证官网返回、主题同步和深链刷新。

## 9. 不能直接宣称正式上线的事项

以下项目仍需在正式上线前完成或复核：

1. 支付回调的金额、商户号、币种、订单号、交易号和并发幂等测试。
2. 提现 `pending -> approved -> done`、拒绝退回冻结余额和重复操作测试。
3. 上传包的压缩炸弹、MIME 伪造、依赖和入口模块校验。
4. AI 分析任务的超时、失败重试、进程重启恢复和敏感代码脱敏。
5. 卸载保留数据与删除数据两种路径，以及外键顺序和回滚验证。
6. 管理台普通角色的页面、按钮、接口权限矩阵。
7. 官网全部页面在空数据、401、403、404、500 和移动端下的浏览器回归。
8. 生产部署时将文档返回地址从开发用 `127.0.0.1:8000` 改为实际站点地址或配置化地址。

## 10. 接手后的执行顺序

### 第一步：环境和基线

- 备份数据库和上传目录。
- 确认 Python、Node、虚拟环境、SQLite/MySQL 配置。
- 启动后端和前端，确认官网、管理台、文档入口均可访问。
- 记录当前迁移版本、插件版本和 Git 工作区变更，不要覆盖已有修改。

### 第二步：功能回归

- 注册、验证码 60 秒限制、登录、退出和刷新登录态。
- 官网配置和导航保存后刷新页面验证。
- 开发者创建插件、上传包、生成文档、提交审核。
- 管理员审核、配置服务费、发布、下架。
- 用户购买、退款保护期、收益结算、钱包保存和提现申请。
- 文档入口、官网返回、主题切换和移动端导航。

### 第三步：安全和并发

- 重复支付通知、金额篡改、非法状态迁移、并发提现。
- 文件路径、下载权限、删除保护和历史版本授权。
- 权限不足、失效 Token、账号禁用和审计日志。
- 上传限制、任务超时、数据库事务和服务重启恢复。

### 第四步：交付打包

交付前必须提交：

- 插件源码和 `plugin.json`。
- 完整迁移文件和升级说明。
- 后台 Vue 页面及宿主前端同步文件。
- API 清单、权限清单、菜单组件映射。
- 测试报告、关键页面截图和安装/升级/卸载记录。
- 可重新导入 ApeAdmin 的 ZIP 包。

## 11. 相关文档索引

- `APEHUB_WEB_PLUGIN_REMEDIATION.md`：初始整改需求和验收标准。
- `APEHUB_WEB_PLUGIN_NEXT_TASKS.md`：P0/P1/P2 后续任务和上线门槛。
- `backend/src/plugins/builtin/apehub_web/UPGRADE.md`：版本迁移和升级说明。
- `backend/src/plugins/builtin/apehub_web/FRONTEND_INTEGRATION.md`：宿主前端接入说明。
- `backend/src/plugins/builtin/apehub_web/docs-site/docs/`：平台与市场文档源文件。

## 12. 交接结论

当前版本已经从“静态页面演示”推进到“官网、插件市场、开发者工作台、审核发布、订单和提现”的可联调骨架，核心接口和数据模型已存在，文档站也已纳入插件包。

但它仍应被视为“开发联调版本”，不是未经完整支付、并发、权限、卸载和浏览器回归的正式生产版本。后续开发必须以本文件的真实代码路径和验收顺序为准，禁止重新注册不存在的菜单组件、写死演示数据或把第三方文档服务当成独立插件运行时依赖。
