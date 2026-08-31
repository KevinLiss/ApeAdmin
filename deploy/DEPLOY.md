---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'a80eb638-f488-4705-82fc-d62f53a2938f'
  PropagateID: 'a80eb638-f488-4705-82fc-d62f53a2938f'
  ReservedCode1: 'df1fcf4c-f544-4f07-8373-d06381cfff0f'
  ReservedCode2: 'df1fcf4c-f544-4f07-8373-d06381cfff0f'
---

# ApeAdmin 宝塔部署指南（安装向导版 · 80 端口直连）

> **部署目标**：服务器 118.89.55.247（宝塔面板）· 域名 `apehub.finecv.cn`
> **部署方式**：上传部署包 → 宝塔建 Python 项目（**直接绑 80 端口，无需 Nginx 反代**）→ 浏览器打开自动进入**安装向导**（3 步完成）

## 部署包内容（底座版 · 扁平结构）

```
apeadmin-base-<date>.tar.gz 解压后:
apeadmin/
├── src/                后端底座源码 + frontend_dist/（管理后台构建产物）
├── requirements.txt      生产依赖锁定版本
├── scripts/
│   ├── deploy.sh       备选：纯命令行部署（不用宝塔 Python 项目时）
│   └── manage.sh       日常运维（状态/重启/日志/更新/备份）
├── nginx/apeadmin.conf Nginx 配置模板（仅以后上 HTTPS 时才用到）
└── .env.example        环境变量参考模板（向导会自动生成 .env，无需手工配）
```

> **扁平化设计**：解压出来直接就是 `apeadmin/`，无版本号目录、无 backend 子层。
> 宝塔 Python 项目「项目路径」直接选 `/www/wwwroot/apeadmin` 即可，不用再钻子目录。

底座包含：RBAC 权限、菜单、用户/角色/部门管理、插件框架、MCP 工具、AI 供应商配置、日志审计。
不含 apehub_web 官网插件（后续在后台插件管理里按需安装）。

## 为什么可以直接用 80 端口、不用反向代理？

- **80 端口被谁占着**：你服务器上的 Nginx（宝塔默认装的）。卸载或停止它，80 就空出来了。
- **普通用户绑不了 80**：Linux 下 1024 以下端口只有 root 能绑定，所以启动用户必须选 **root**。
- **失去了什么**：HTTPS（443）需要证书服务。首次部署先用 80 跑通；以后要 HTTPS 再把 Nginx 装回来做反代即可（见文末），数据不受影响。

## 一、本地打包

```bash
cd deploy
bash build_deploy_package.sh              # 底座版（推荐先用这个）
# 或带官网插件的完整版:
bash build_deploy_package.sh --with-apehub
```

## 二、服务器准备（宝塔，三件事）

1. **DNS 解析**：域名服务商加 A 记录 `apehub → 118.89.55.247`
2. **卸载 Nginx**：软件商店 → 已安装 → Nginx → 卸载（或停止并关闭自启），释放 80 端口
3. **Python 环境**：网站 → Python项目 → Python环境，确认有 Python 3.11.6（你的面板已有）

MySQL **不用提前建库**——向导第 1 步可以直接创建（用宝塔数据库页建的账号），或选 SQLite 完全免配置。

## 三、上传并解压（解压即用，无需重命名）

宝塔「文件」→ 进入 `/www/wwwroot/` → 上传 `apeadmin-base-*.tar.gz` → 右键解压。

解压出来直接就是 `apeadmin/` 目录（扁平结构，已无版本号目录和 backend 层，**不用重命名**）。

命令行等价操作：

```bash
scp deploy/dist/apeadmin-base-*.tar.gz root@118.89.55.247:/www/wwwroot/
# 服务器上:
cd /www/wwwroot && tar xzf apeadmin-base-*.tar.gz
```

**自检**：`/www/wwwroot/apeadmin/src/main.py` 必须存在（注意是 `src/main.py`，不再是 `backend/src/main.py`）。

## 四、创建 Python 项目（对应宝塔表单逐项填）

宝塔 → 网站 → Python项目 → 添加项目：

| 表单项 | 填写值 | 说明 |
|---|---|---|
| 项目名称 | `apeadmin` | |
| **项目路径** | `/www/wwwroot/apeadmin` | 解压即此目录，直接选，**不用进子目录** |
| Python版本 | 3.11.6 | |
| 启动方式 | **命令行启动** | |
| 启动命令 | `python -m uvicorn src.main:app --host 0.0.0.0 --port 80 --workers 1` | 端口写 80 |
| **项目端口** | `80` | 与启动命令一致 |
| 通讯协议 | **asgi** | FastAPI 必须，别用默认 wsgi |
| 环境变量 | 留空 | |
| **启动用户** | **root** | 默认 www 绑不了 80，必须改 |
| 安装依赖包路径 | `/www/wwwroot/apeadmin/requirements.txt` | 勾选让面板自动装 |

> ⚠️ **单 worker**：插件热拔插运行态是进程本地的，多 worker 会状态错乱。
> ⚠️ **不要**提前创建 `.env`——没有 `.env` 才会触发安装向导。
> ⚠️ 面板若自动在启动命令里追加参数，以「端口 80、workers 1」为准。

## 五、放行 80 端口（两处都要）

1. **腾讯云控制台** → 你的服务器 → 防火墙/安全组 → 添加规则：允许 TCP 80
2. **宝塔** → 安全 → 添加端口规则：放行 80

## 六、浏览器打开向导（核心流程）

访问 `http://118.89.55.247/`（**不带端口号**），自动跳转 `/setup` 安装向导。

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

## 七、验证清单

| 检查项 | 预期 |
|---|---|
| `http://apehub.finecv.cn/admin/` | 管理后台登录页 |
| 用向导设的账号密码登录 | 进入后台，菜单/用户/角色正常 |
| 后台 → AI 设置 | Key 显示 sk-****（加密解密一致） |
| 后台 → 系统设置 | 站点名/域名 = 向导填的值 |
| `curl http://127.0.0.1/health` | `status: healthy` |

## 八、后续：安装 apehub_web 官网插件

底座部署稳定后，需要官网/插件市场时：

1. 后台 → 插件管理 → 安装 apehub_web 插件（或用 `--with-apehub` 的完整包重新部署）
2. 插件自带 migration，安装即自动建表初始化

## 九、日常运维

```bash
# 面板：网站 → Python项目 → 重启/日志
# 命令行:
bash /www/wwwroot/apeadmin/scripts/manage.sh status|logs|restart|backup
```

**重装/重置**：删除 `setup.lock` 和 `.env` → 重启 → 重新进入安装向导（数据表会保留，向导会重新建缺失的表）。

```bash
rm /www/wwwroot/apeadmin/setup.lock /www/wwwroot/apeadmin/.env
bash /www/wwwroot/apeadmin/scripts/manage.sh restart
```

## 十、以后要 HTTPS 怎么办（可选）

跑通后随时可升级，**数据不受影响**：

1. 软件商店装回 Nginx（它会占用 80/443 做证书与转发）
2. 宝塔 Python 项目把启动命令端口从 80 改回 8000、启动用户改回 www、重启
3. 宝塔建站点 `apehub.finecv.cn` → SSL → Let's Encrypt 申请证书
4. 站点反代配置参考包内 `nginx/apeadmin.conf`（含 SSE 与上传大小配置）

## 注意事项

| 事项 | 说明 |
|---|---|
| **单 worker** | 启动命令固定 `--workers 1` |
| **asgi** | 面板通讯协议必须 asgi |
| **启动用户 root** | 80 端口直连的前提；将来切 HTTPS 反代后可改回 www |
| **无 .env 才有向导** | 手工放了 .env 则直接按 .env 启动，不走向导 |
| **JWT_SECRET** | 向导自动生成；生成后不可改（API Key 加密依赖） |
| **SQLite 够用吗** | 2000 用户量级写并发足够；上量后后台导出再切 MySQL |
| **uploads** | `src/uploads/` 运行时写入，备份别漏 |

> AI生成