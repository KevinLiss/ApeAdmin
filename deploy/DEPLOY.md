---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'a87da057-03ff-4a3b-b424-6895d7df792b'
  PropagateID: 'a87da057-03ff-4a3b-b424-6895d7df792b'
  ReservedCode1: '1bf90ff3-3a00-4d49-9817-9fe65ffa67fa'
  ReservedCode2: '1bf90ff3-3a00-4d49-9817-9fe65ffa67fa'
---

# ApeAdmin 宝塔服务器部署指南

## 部署包内容

```
apeadmin-deploy-<date>.tar.gz
├── backend/            后端源码 + frontend_dist/（管理后台构建产物）
│   └── requirements.txt  生产依赖锁定版本
├── nginx/apeadmin.conf Nginx 站点配置模板
├── scripts/
│   ├── deploy.sh       一键部署（服务器上运行）
│   └── manage.sh       日常运维（状态/重启/日志/更新/备份）
├── .env.example        环境变量模板
└── DEPLOY.md           本文档
```

## 一、本地打包（开发机）

```bash
cd deploy
bash build_deploy_package.sh
# 迁移现有数据（官网内容/插件市场/AI Key 等）必加:
bash build_deploy_package.sh --with-db --with-uploads
```

产物在 `deploy/dist/apeadmin-deploy-<date>.tar.gz`（约 10MB 上下）。

> **带数据迁移时必须加 `--with-db`**：包内 apeadmin.db 是迁移源；
> `--with-uploads` 带上插件 ZIP、官网图片等运行时素材。

## 二、服务器准备（宝塔）

1. **Python 3.11+**：宝塔 → 软件商店 → **Python 项目管理器 2.0** → 安装 3.11 或 3.12
   - 记下解释器路径，如 `/usr/local/python311/bin/python3`
   - （若系统自带 python3 ≥ 3.11 也可直接用）
2. **Nginx**：宝塔 → 软件商店 → 安装 Nginx
3. **MySQL**：宝塔 → 数据库 → 添加库 `apeadmin` + 用户（记下库名/用户/密码）
   - 建议字符集 utf8mb4
   - 2核2G 配置下 MySQL 与应用同机可行；内存紧张时加 2G swap

## 三、上传并部署

```bash
# 1. 上传部署包（宝塔文件管理或 scp）
scp dist/apeadmin-deploy-*.tar.gz root@服务器IP:/root/

# 2. 服务器上解压并一键部署
cd /root
tar xzf apeadmin-deploy-*.tar.gz
cd apeadmin-deploy-*
bash scripts/deploy.sh
# 若用宝塔 Python 管理器的解释器:
# PYTHON_BIN=/usr/local/python311/bin/python3 bash scripts/deploy.sh
```

脚本会自动：建目录、装依赖、生成 `.env`（含随机 JWT_SECRET）、配 systemd 守护、启动并健康检查。

## 四、SQLite → MySQL 数据迁移（带数据部署必做）

> 前提：部署包是用 `--with-db` 打的，包内含 `backend/apeadmin.db`；
> 且已在宝塔建好 MySQL 库。

```bash
# 1. 先把 .env 配好 MySQL 五项 + 记住新生成的 JWT_SECRET
vim /www/wwwroot/apeadmin/backend/.env
#   DB_TYPE=mysql
#   DB_HOST=127.0.0.1
#   DB_PORT=3306
#   DB_USER=apeadmin
#   DB_PASSWORD=<宝塔建的密码>
#   DB_NAME=apeadmin
#   （JWT_SECRET 用 deploy.sh 生成的随机值，不要改）

# 2. 执行迁移（在 backend 目录）
cd /www/wwwroot/apeadmin/backend
./.venv/bin/python -m scripts.migrate_sqlite_to_mysql \
    --source apeadmin.db \
    --old-jwt-secret '<本地开发时的 JWT_SECRET>'

# 3. 重启生效
systemctl restart apeadmin
```

**--old-jwt-secret 参数说明（关键）：**

- 数据库里存的 AI API Key、邮箱授权码、支付密钥等都是用 JWT_SECRET 派生的密钥加密的
- 本地开发时若没设过 JWT_SECRET，默认值是 `change-me-in-production-please-32chars!`
- 不传该参数 → 迁移会成功，但所有密文字段在新服务器密钥下**解不开**（后台看不到真实 Key）

**迁移脚本会做：**

| 步骤 | 说明 |
|---|---|
| 建表 | 按 ORM 模型在 MySQL 建全部表（幂等，已有则跳过） |
| 搬数据 | 28 张表 6000+ 行按拓扑序迁移（含日志/菜单/官网内容/插件市场） |
| 版本表 | 迁 apehub_web_schema_version（避免插件 migration 重跑导致数据损坏） |
| 密钥轮换 | 5 个加密字段旧密钥解密 → 新密钥重加密 |
| 自增校正 | 重置 AUTO_INCREMENT 避免主键冲突 |

**验证迁移成功：**

```bash
# 服务器 MySQL（用宝塔里的 root 或对应账号）
mysql -u apeadmin -p apeadmin -e "SELECT COUNT(*) FROM sys_log;"
# 应返回本地库的日志条数（如 5972）

# API 冒烟
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 应返回 token（登录账号密码与本地库一致，即迁移前你在后台改过的密码）
```

迁移确认无误后，可删除源文件避免误用：
```bash
rm /www/wwwroot/apeadmin/backend/apeadmin.db
```

## 五、Nginx 配置（宝塔操作）

1. 宝塔 → 网站 → 添加站点：域名填你的域名，纯静态，不建数据库
2. 站点设置 → **配置文件**：参考包内 `nginx/apeadmin.conf` 修改
   - 必改：`server_name`
   - 核心是 `location /` 反代到 `127.0.0.1:8000`，并保留 SSE 相关的
     `proxy_buffering off` 与长超时（MCP 传输层需要）
3. HTTPS：宝塔 → SSL → Let's Encrypt 一键申请，申请后配置文件中放开
   `ssl_certificate` 两行注释
4. `nginx -t && nginx -s reload` 或面板重启

> 安全：8000 端口不要在宝塔防火墙/云安全组放行，仅 Nginx 反代访问。

## 六、首次启动后的配置

1. **改管理员密码**：编辑 `backend/.env` 的 `SUPER_ADMIN_PASSWORD` 后重启
   （注意：该值只在**首次建库**时生效；迁移数据时账号密码来自本地库，直接在后台改密码即可）
2. **登录管理后台**：`http://域名/admin/`
3. **配置 AI Key**：后台 → 官网配置 → 填 DeepSeek/千问 API Key
   （存数据库并加密，依赖 `.env` 里的 `JWT_SECRET` 派生密钥；迁移时已轮换过）
4. **官网域名**：后台 → Apehub_web → 站点配置中设置正式域名

## 七、日常运维

```bash
bash scripts/manage.sh status   # 状态
bash scripts/manage.sh logs     # 日志
bash scripts/manage.sh restart  # 重启
bash scripts/manage.sh backup   # 备份数据库+uploads
```

**版本更新**：本地重新打包 → 上传解压到 `/tmp/apeadmin-update/` →
`bash scripts/manage.sh update`（保留 .env / 数据库 / uploads）

## 八、注意事项

| 事项 | 说明 |
|---|---|
| **单 worker** | 插件热拔插运行态是进程本地的，systemd 配置固定 `--workers 1`，勿改多 worker |
| **JWT_SECRET** | 同时用于 API Key 加密，首次启动后**不可变更**，否则已存密钥解密失败（迁移部署时会轮换到服务器新密钥） |
| **MySQL 连接** | 默认 utf8mb4；aiomysql 驱动已固定在 requirements.txt |
| **uploads** | `backend/src/uploads/` 运行时写入（插件 ZIP/图片），备份别漏 |
| **API 文档** | `/docs` `/redoc` 生产环境建议在 Nginx 屏蔽（配置里有现成注释段） |
| **SSE** | MCP SSE 端点依赖 Nginx `proxy_buffering off`，模板已配好勿删 |
| **迁移幂等** | migrate_sqlite_to_mysql 可重复执行（每次清空目标表重灌），但生产稳定后不建议再跑 |

> AI生成