---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '0372e43b-b5d1-4d2a-bc55-824023cad9fb'
  PropagateID: '0372e43b-b5d1-4d2a-bc55-824023cad9fb'
  ReservedCode1: 'cb2de601-017e-4d2b-b37f-ea46e0672cfc'
  ReservedCode2: 'cb2de601-017e-4d2b-b37f-ea46e0672cfc'
---

# ApeAdmin 宝塔部署指南（安装向导版）

> **部署目标**：服务器 118.89.55.247（宝塔面板）· 域名 `apehub.finecv.cn`
> **部署方式**：上传部署包 → 宝塔建 Python 项目 → 浏览器打开自动进入**安装向导**（3 步完成）

## 部署包内容（底座版）

```
apeadmin-deploy-base-<date>.tar.gz
├── backend/            后端底座源码 + frontend_dist/（管理后台构建产物）
│   └── requirements.txt  生产依赖锁定版本
├── nginx/apeadmin.conf Nginx 站点配置模板（已按 apehub.finecv.cn 配好）
├── scripts/
│   ├── deploy.sh       备选：纯命令行部署（不用宝塔 Python 项目时）
│   └── manage.sh       日常运维（状态/重启/日志/更新/备份）
├── .env.example        环境变量参考模板（向导会自动生成 .env，无需手工配）
└── DEPLOY.md           本文档
```

底座包含：RBAC 权限、菜单、用户/角色/部门管理、插件框架、MCP 工具、AI 供应商配置、日志审计。
不含 apehub_web 官网插件（后续在后台插件管理里按需安装）。

## 一、本地打包

```bash
cd deploy
bash build_deploy_package.sh              # 底座版（推荐先用这个）
# 或带官网插件的完整版:
bash build_deploy_package.sh --with-apehub
```

## 二、服务器准备（宝塔，两项）

1. **DNS 解析**：域名服务商加 A 记录 `apehub → 118.89.55.247`
2. **Python 项目管理器**：宝塔 → 网站 → Python项目 → Python环境，确认有 Python 3.11.6（你的面板已有）

MySQL **不用提前建库**——向导第 1 步可以直接创建（用宝塔数据库页建的 root 或有建库权限的账号），或选 SQLite 完全免配置。

## 三、上传并创建 Python 项目

```bash
# 1. 上传并解压（宝塔文件管理器上传也行）
scp deploy/dist/apeadmin-deploy-base-*.tar.gz root@118.89.55.247:/www/wwwroot/
# 服务器上:
cd /www/wwwroot && tar xzf apeadmin-deploy-base-*.tar.gz && mv apeadmin-deploy-base-* apeadmin
```

2. 宝塔 → 网站 → Python项目 → 添加项目，对应表单填：

| 表单项 | 填写值 |
|---|---|
| 项目名称 | `apeadmin` |
| 项目端口 | `8000` |
| Python环境 | `Python 3.11.6` |
| 启动方式 | **命令行启动** |
| 项目路径 | `/www/wwwroot/apeadmin/backend` |
| 通讯协议 | **asgi**（FastAPI 必须，别用默认 wsgi） |
| 启动用户 | `www` |
| 安装依赖包路径 | `/www/wwwroot/apeadmin/backend/requirements.txt` |

> ⚠️ 单 worker：插件热拔插运行态是进程本地的，多 worker 会状态错乱。
> ⚠️ **不要**提前创建 `.env`——没有 `.env` 才会触发安装向导。

3. 面板启动项目后，日志里应看到：`系统未安装，进入安装向导模式（/setup）`

## 四、浏览器打开向导（核心流程）

访问 `http://118.89.55.247:8000/`（或配好域名后 `http://apehub.finecv.cn/`），自动跳转 `/setup` 安装向导。

### 第 1 步：配置数据库

- **选 MySQL**：填宝塔数据库的地址/账号/密码（点「测试连接」自动建库）
  - 也可以直接填宝塔的 MySQL root 账号，让向导自动建 `apeadmin` 库
- **选 SQLite**：什么都不用填，直接下一步（轻量部署推荐）

### 第 2 步：站点与管理员配置

| 字段 | 说明 |
|---|---|
| 站点名称 | 如 `ApeHub` |
| 站点访问地址 | `http://apehub.finecv.cn`（你的域名，写入 CORS 与站点配置） |
| 管理后台路径 | 默认 `/admin`（可改成自定义前缀增加安全性） |
| 管理员账号/密码 | 后台超级管理员，**务必记牢** |

点「开始安装」→ 自动：生成 .env（含随机 JWT_SECRET）→ 建 36 张表 → 完成锁定。

### 第 3 步：成功页

显示前后台地址、管理员账号密码（提示保存）。按提示**重启项目**（宝塔 Python 项目页点「重启」）——重启时自动初始化超管账号、菜单、种子数据（用新密钥加密，保证 AI Key 等密文可解）。

重启完成页面自动检测到，点「进入站点」即完成。

## 五、域名反代 + HTTPS

1. 宝塔 → 网站 → 找到 Python 项目映射的站点 → 设置 → 配置文件
2. `location /` 段替换为反代配置（完整版见包内 `nginx/apeadmin.conf`，已按 apehub.finecv.cn 配好）：

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
    proxy_buffering off;          # SSE（MCP 必需）
    proxy_read_timeout 3600s;
}
client_max_body_size 100m;        # 插件 ZIP 上传
```

3. 站点设置 → SSL → Let's Encrypt 申请 `apehub.finecv.cn`，开启强制 HTTPS

> 8000 端口只在宝塔面板调试期临时放行；正式走域名后安全组只留 80/443。

## 六、验证清单

| 检查项 | 预期 |
|---|---|
| `http://apehub.finecv.cn/admin/` | 管理后台登录页 |
| 用向导设的账号密码登录 | 进入后台，菜单/用户/角色正常 |
| 后台 → AI 设置 | Key 显示 sk-****（加密解密一致） |
| 后台 → 系统设置 | 站点名/域名 = 向导填的值 |
| `curl http://127.0.0.1:8000/health` | `status: healthy` |

## 七、后续：安装 apehub_web 官网插件

底座部署稳定后，需要官网/插件市场时：

1. 后台 → 插件管理 → 安装 apehub_web 插件（或用 `--with-apehub` 的完整包重新部署）
2. 插件自带 migration，安装即自动建表初始化

## 八、日常运维

```bash
# 面板：网站 → Python项目 → 重启/日志
# 命令行:
bash /www/wwwroot/apeadmin/scripts/manage.sh status|logs|restart|backup
```

**重装/重置**：删除 `backend/setup.lock` 和 `backend/.env` → 重启 → 重新进入安装向导（数据表会保留，向导会重新建缺失的表）。

## 九、注意事项

| 事项 | 说明 |
|---|---|
| **单 worker** | 启动命令固定 `--workers 1` |
| **asgi** | 面板通讯协议必须 asgi |
| **无 .env 才有向导** | 手工放了 .env 则直接按 .env 启动，不走向导 |
| **JWT_SECRET** | 向导自动生成；生成后不可改（API Key 加密依赖） |
| **SQLite 够用吗** | 2000 用户量级写并发足够；上量后后台导出再切 MySQL |
| **uploads** | `backend/src/uploads/` 运行时写入，备份别漏 |

> AI生成