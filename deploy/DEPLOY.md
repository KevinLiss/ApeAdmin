---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '5c2b6e20-f36c-44c4-8451-eb6062c79328'
  PropagateID: '5c2b6e20-f36c-44c4-8451-eb6062c79328'
  ReservedCode1: 'ce3dc2d2-cbc7-462a-88cb-5be1ba9d075a'
  ReservedCode2: 'ce3dc2d2-cbc7-462a-88cb-5be1ba9d075a'
---

# ApeAdmin 宝塔服务器部署指南

> **部署目标**：服务器 118.89.55.247（宝塔面板）· 域名 `apehub.finecv.cn`
> **部署方式**：宝塔面板 Python 项目可视化部署（对应面板「网站 → Python项目 → 添加项目」表单）
> **数据库**：MySQL（宝塔数据库页已可建库）

## 部署包内容

```
apeadmin-deploy-<date>.tar.gz
├── backend/            后端源码 + frontend_dist/（管理后台构建产物）
│   ├── requirements.txt  生产依赖锁定版本
│   ├── apeadmin.db       开发库数据（迁移源，--with-db 打包时才有）
│   └── scripts/migrate_sqlite_to_mysql.py  SQLite→MySQL 迁移脚本
├── nginx/apeadmin.conf Nginx 站点配置模板（已按 apehub.finecv.cn 配好）
├── scripts/
│   ├── deploy.sh       备选：纯命令行一键部署（不用宝塔 Python 项目时）
│   └── manage.sh       日常运维（状态/重启/日志/更新/备份）
├── .env.example        环境变量模板（已按部署域名配好 CORS）
└── DEPLOY.md           本文档
```

## 一、本地打包（开发机）

```bash
cd deploy
bash build_deploy_package.sh --with-db --with-uploads
```

产物在 `deploy/dist/apeadmin-deploy-<date>.tar.gz`（约 10MB）。

> `--with-db` 把开发库 apeadmin.db 打进包（迁移源）；`--with-uploads` 带上插件 ZIP、官网图片素材。

## 二、服务器准备（宝塔操作）

### 1. DNS 解析

到域名管理（腾讯云 DNSPod 或 finecv.cn 所在服务商）添加 A 记录：

```
主机记录: apehub   记录类型: A   记录值: 118.89.55.247
```

### 2. MySQL 建库

宝塔 → 数据库 → 添加数据库：

| 项 | 建议值 |
|---|---|
| 数据库名 | apeadmin |
| 用户名 | apeadmin |
| 密码 | 点「随机生成」并**记下来** |
| 访问权限 | 本地服务器 |
| 字符集 | utf8mb4 |

### 3. Python 环境

宝塔 → 网站 → Python项目 → Python环境 → 环境管理：确认有 **Python 3.11.6**（截图里默认已选中，无需再装）。

## 三、上传解压

```bash
# 开发机上传（或宝塔文件管理器直接传）
scp deploy/dist/apeadmin-deploy-*.tar.gz root@118.89.55.247:/www/wwwroot/

# 服务器上（宝塔终端）
cd /www/wwwroot
tar xzf apeadmin-deploy-*.tar.gz
mv apeadmin-deploy-* apeadmin
```

## 四、创建 Python 项目（宝塔可视化，对应截图表单）

宝塔 → 网站 → Python项目 → 添加项目，逐项填写：

| 表单项 | 填写值 | 说明 |
|---|---|---|
| **项目名称** | `apeadmin` | |
| **项目端口** | `8000` | 后端监听端口 |
| **Python环境** | `Python 3.11.6` | 默认即可 |
| **启动方式** | **命令行启动** | 不要选 uwsgi/gunicorn（FastAPI 需 asgi，用面板命令行最可控） |
| **项目路径** | `/www/wwwroot/apeadmin/backend` | 项目根路径 |
| **入口/启动命令** | 见下方说明 | 面板用启动命令代替入口文件 |
| **通讯协议** | `asgi` | FastAPI 必须 asgi，别选 wsgi |
| **环境变量** | 无 | 配置走 .env 文件 |
| **启动用户** | `www` | |
| **安装依赖包路径** | `/www/wwwroot/apeadmin/backend/requirements.txt` | 面板自动建 venv 并安装 |

**启动命令**（若表单要求填执行命令/入口）：

```
.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 1
```

> ⚠️ **必须单 worker**：插件热拔插运行态是进程本地的，多 worker 会导致插件/MCP 状态错乱。面板若默认给了多进程选项，改回 1。
>
> ⚠️ 面板「Python项目管理器」创建的项目若自动配了 venv，启动命令里的 `.venv/bin/uvicorn` 路径以面板实际生成的 venv 为准（一般是 `/www/wwwroot/apeadmin/backend/.venv/bin/uvicorn`，面板日志里能看到）。

创建后面板会自动：建 venv → 装 requirements.txt 依赖 → 启动 → 映射到 `/www/wwwroot/apeadmin` 站点。

### 首次启动前：先配好 .env

面板创建项目会尝试启动，但**必须先有 .env**（否则用默认配置连 SQLite）。先在宝塔文件管理器或终端创建：

```bash
cd /www/wwwroot/apeadmin/backend
cp /www/wwwroot/apeadmin/.env.example .env
```

然后编辑 `.env`（宝塔文件管理器双击编辑）：

```ini
DEBUG=False
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=apeadmin
DB_PASSWORD=<第二步生成的数据库密码>
DB_NAME=apeadmin
JWT_SECRET=<保持 .env.example 的占位不动，下一步面板生成后替换>
CORS_ORIGINS=["https://apehub.finecv.cn","http://apehub.finecv.cn"]
SUPER_ADMIN_PASSWORD=<改成强密码>
```

> 顺序建议：先建 .env → 再在面板创建项目（避免面板用空配置先跑一次）。
> 如果面板已经创建项目：改完 .env 在面板里**重启**项目即可。

### JWT_SECRET 生成

```bash
openssl rand -hex 32
```

把输出填进 `.env` 的 `JWT_SECRET=`。此密钥同时用于数据库内 API Key 加密，**生成后不可再改**（否则已存密钥解不开）。

## 五、SQLite → MySQL 数据迁移（把开发库数据带过来）

部署包里带了开发库 `backend/apeadmin.db`（官网内容、插件市场、菜单、日志等 6000+ 行）。迁移命令：

```bash
cd /www/wwwroot/apeadmin/backend
.venv/bin/python -m scripts.migrate_sqlite_to_mysql \
    --source apeadmin.db \
    --old-jwt-secret 'change-me-in-production-please-32chars!'
```

**参数说明（关键）：**

- `--old-jwt-secret`：本地开发库加密数据所用的密钥。开发机从未设过 JWT_SECRET，默认值即上面那串
- **不传会怎样**：迁移成功但所有密文字段（DeepSeek API Key、邮箱授权码、支付密钥）在新服务器密钥下解不开

**迁移脚本自动做：**

| 步骤 | 说明 |
|---|---|
| 建表 | 按 ORM 模型建全部 MySQL 表（幂等） |
| 搬数据 | 28 张表 6000+ 行按拓扑序迁移 |
| 版本表 | 迁 apehub_web_schema_version（避免插件 migration 重跑损坏数据） |
| 密钥轮换 | 5 个加密字段旧密钥解密 → 服务器新密钥重加密 |
| 自增校正 | 重置 AUTO_INCREMENT 避免主键冲突 |

**验证：**

```bash
# 登录接口应返回 token（账号密码为本地后台在用的）
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
```

迁移确认无误后删除源库避免误用：

```bash
rm /www/wwwroot/apeadmin/backend/apeadmin.db
```

## 六、域名反代配置（宝塔操作）

### 若用 Python项目 自带站点

宝塔 → 网站 → Python项目 → 点项目「设置/配置」→ 找到映射的站点配置文件，把 `location /` 段替换为：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # SSE（MCP 传输层必需）
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

并在 server 段补 `client_max_body_size 100m;`（插件 ZIP 上传）。

### 若手动建站点

宝塔 → 网站 → 添加站点 → 域名 `apehub.finecv.cn`（纯静态）→ 站点设置 → 配置文件 → 用包内 `nginx/apeadmin.conf` 整体替换（它是完整可直接用的版本）。

### SSL 证书

宝塔 → 网站 → 站点设置 → SSL → Let's Encrypt 申请 `apehub.finecv.cn` 证书，开启「强制 HTTPS」。
申请后若用整份 conf 模板，把 conf 里 `ssl_certificate` 两行注释放开、路径按宝塔实际路径改。

## 七、验证清单

| 检查项 | 命令/地址 | 预期 |
|---|---|---|
| 后端健康 | `curl 127.0.0.1:8000/docs -I` | 200 |
| 官网首页 | http://apehub.finecv.cn/ | 200，显示官网 |
| 官网内容 | http://apehub.finecv.cn/api/v1/apehub-web/site/public/config | JSON，含迁移过来的内容 |
| 管理后台 | http://apehub.finecv.cn/admin/ | 登录页 |
| 登录 | admin / 密码 | 进入后台，菜单齐全 |
| AI 提供商 | 后台 → AI 设置 | Key 显示为 sk-****xxxx（解密成功） |
| 插件市场 | http://apehub.finecv.cn/apehub-web/ | 展示迁移过来的插件数据 |

## 八、日常运维

```bash
# 面板方式：网站 → Python项目 → 重启/日志按钮

# 命令行方式（若用 scripts/deploy.sh 部署）:
bash /www/wwwroot/apeadmin/scripts/manage.sh status
bash /www/wwwroot/apeadmin/scripts/manage.sh backup    # 备份 db + uploads
```

**版本更新**：本地重打包 → 上传解压到 `/tmp/apeadmin-update/` → `bash scripts/manage.sh update`（保留 .env / 数据库 / uploads）。

## 九、注意事项

| 事项 | 说明 |
|---|---|
| **单 worker** | 插件热拔插运行态是进程本地的，启动命令固定 `--workers 1`，面板里也别开多进程 |
| **asgi 而非 wsgi** | 面板「通讯协议」必须选 asgi；uwsgi/gunicorn 启动方式对 FastAPI 异步路由不友好 |
| **JWT_SECRET** | 生成后不可变更（API Key 加密依赖）；迁移时已自动轮换到服务器新密钥 |
| **MySQL 内存** | 2核2G 跑 MySQL+应用够用；内存紧张时加 2G swap |
| **uploads** | `backend/src/uploads/` 运行时写入（插件 ZIP/图片），备份别漏 |
| **API 文档** | `/docs` `/redoc` 生产建议在 Nginx 屏蔽（conf 模板有现成注释段） |
| **8000 端口** | 只监听 127.0.0.1，云安全组/宝塔防火墙不必放行 |
| **迁移幂等** | migrate_sqlite_to_mysql 可重复执行（清空重灌），生产稳定后别再跑 |

## 十、备选：纯命令行部署（不用面板 Python 项目）

若面板 Python 项目创建遇到问题，可用包内 `scripts/deploy.sh` 直接部署（root 运行）：

```bash
cd /www/wwwroot/apeadmin
bash scripts/deploy.sh          # 建 venv/装依赖/生成 .env/systemd 守护/健康检查
PYTHON_BIN=/www/server/pyporject_evn/versions/3.11.6/bin/python3 bash scripts/deploy.sh  # 指定宝塔 Python
```

systemd 服务名 `apeadmin`，`systemctl status apeadmin` 查看。其余步骤（.env、迁移、Nginx）与本指南相同。

> AI生成