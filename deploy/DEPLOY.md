---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '975f6190-01c0-4d88-8b4c-a14071e6aee1'
  PropagateID: '975f6190-01c0-4d88-8b4c-a14071e6aee1'
  ReservedCode1: 'c6c3c78c-4c7d-499d-8eea-f904adb73e40'
  ReservedCode2: 'c6c3c78c-4c7d-499d-8eea-f904adb73e40'
---

# ApeAdmin 宝塔部署指南（安装向导版 · Nginx 反代）

> **部署目标**：服务器 118.89.55.247（宝塔面板）· 域名 `apehub.finecv.cn`
> **部署方式**：部署包解压 → 一键脚本部署（127.0.0.1:8000）→ 宝塔建反代站点 → 浏览器进入**安装向导**（3 步完成）
> **多域名共存**：Nginx 占 80/443 按 Host 分发，ApeAdmin 只监听本机回环，服务器上其他网站项目不受影响

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

## 为什么用 Nginx 反代（多域名场景的标准架构）

```
用户浏览器 → http://apehub.finecv.cn
                ↓ (80端口, Nginx)
        Nginx 按 Host 分发:
        ├─ apehub.finecv.cn  → 127.0.0.1:8000 (ApeAdmin)
        └─ 其他域名           → 服务器上其他项目（不受影响）
```

- **其他项目零影响**：Nginx 按 Host 分发，各走各的
- **HTTPS 随时可上**：站点设置 → SSL → Let's Encrypt 一键申请
- **安全**：ApeAdmin 只监听 127.0.0.1，外网无法直接访问 8000，无需放行

## 一、本地打包

```bash
cd deploy
bash build_deploy_package.sh              # 底座版（推荐先用这个）
# 或带官网插件的完整版:
bash build_deploy_package.sh --with-apehub
```

## 二、服务器准备（宝塔，两件事）

1. **DNS 解析**：域名服务商加 A 记录 `apehub → 118.89.55.247`
2. **Nginx 保持运行**：反代模式依赖它（宝塔软件商店已装的话不用动）

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

## 四、一键脚本部署（终端，推荐路线）

> 服务器终端（root）执行，自动：建虚拟环境 → 装依赖（阿里云镜像）→ 注册 systemd（开机自启/崩溃拉起）→ 监听 127.0.0.1:8000

```bash
cd /www/wwwroot/apeadmin
bash scripts/deploy.sh
```

服务管理：`systemctl status|restart apeadmin` · `journalctl -u apeadmin -f`（实时日志）

<details>
<summary>备选：宝塔面板 Python 项目方式（点击展开，仅当不想用命令行时）</summary>

宝塔 → 网站 → Python项目 → 添加项目：

| 表单项 | 填写值 |
|---|---|
| 项目名称 | `apeadmin` |
| 项目路径 | `/www/wwwroot/apeadmin` |
| 启动方式 | 命令行启动 |
| 启动命令 | `python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 1` |
| 启动用户 | `root`（若面板环境准备失败，用上面的一键脚本） |
| 安装依赖包路径 | `/www/wwwroot/apeadmin/requirements.txt` |

注意：面板路线与脚本路线**二选一**，勿同时建（会抢端口）。
</details>

## 五、宝塔建反代站点（可视化两步）

1. 宝塔 → **网站 → 添加站点**：
   - 域名：`apehub.finecv.cn`
   - PHP 版本：**纯静态**
   - 其他默认，提交
2. 站点右侧**「设置」**：
   - **「反向代理」→「添加反向代理」**：代理名称 `apeadmin`、目标 URL `http://127.0.0.1:8000`，提交
   - **「配置文件」**：在 `server{}` 内补三行后保存（大文件上传/长连接，MCP 必需）：

```nginx
    client_max_body_size 100m;
    proxy_read_timeout 3600s;
    proxy_buffering off;
```

> 完整参考：包内 `nginx/apeadmin.conf`（已按 apehub.finecv.cn 配好，含 SSE/上传配置）。
> 若服务器 80 被其他项目占用属正常——Nginx 按 Host 分发互不影响。

## 六、安装向导（浏览器）

访问 `http://apehub.finecv.cn/`，自动跳转 `/setup`：

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

显示前后台地址、管理员账号密码（提示保存）。按提示重启服务——重启时自动初始化超管账号、菜单、种子数据（用新密钥加密，保证 AI Key 等密文可解）：

```bash
systemctl restart apeadmin
```

重启完成页面自动检测到，点「进入站点」即完成。

## 七、验证清单

| 检查项 | 预期 |
|---|---|
| `http://apehub.finecv.cn/admin/` | 管理后台登录页 |
| 用向导设的账号密码登录 | 进入后台，菜单/用户/角色正常 |
| 后台 → AI 设置 | Key 显示 sk-****（加密解密一致） |
| 后台 → 系统设置 | 站点名/域名 = 向导填的值 |
| 服务器 `curl http://127.0.0.1:8000/health` | `status: healthy` |
| 后台 → 日志审计里的登录 IP | 真实公网 IP，非 127.0.0.1（--proxy-headers 生效） |

## 八、后续：安装 apehub_web 官网插件

底座部署稳定后，需要官网/插件市场时：

1. 后台 → 插件管理 → 安装 apehub_web 插件（或用 `--with-apehub` 的完整包重新部署）
2. 插件自带 migration，安装即自动建表初始化

## 九、日常运维

```bash
# 服务管理（一键脚本路线）:
systemctl status|restart|stop apeadmin
journalctl -u apeadmin -f        # 实时日志
# 或用包内脚本:
bash /www/wwwroot/apeadmin/scripts/manage.sh status|logs|restart|backup
```

**重装/重置**：删除 `setup.lock` 和 `.env` → 重启 → 重新进入安装向导（数据表会保留，向导会重新建缺失的表）。

```bash
rm /www/wwwroot/apeadmin/setup.lock /www/wwwroot/apeadmin/.env
bash /www/wwwroot/apeadmin/scripts/manage.sh restart
```

## 十、以后要 HTTPS 怎么办（可选）

反代架构下 HTTPS 零改造，宝塔可视化操作：

1. 站点设置 → SSL → Let's Encrypt 申请 `apehub.finecv.cn` 证书
2. 开启「强制 HTTPS」

ApeAdmin 无需任何改动（Nginx 层完成加密，应用照常监听 8000）。

## 注意事项

| 事项 | 说明 |
|---|---|
| **单 worker** | 启动命令固定 `--workers 1` |
| **反代模式端口** | 默认 127.0.0.1:8000，外网不可直接访问，安全组无需放行 8000 |
| **真实 IP 透传** | 启动命令带 `--proxy-headers --forwarded-allow-ips 127.0.0.1`，否则日志全记 127.0.0.1 |
| **无 .env 才有向导** | 手工放了 .env 则直接按 .env 启动，不走向导 |
| **JWT_SECRET** | 向导自动生成；生成后不可改（API Key 加密依赖） |
| **SQLite 够用吗** | 2000 用户量级写并发足够；上量后后台导出再切 MySQL |
| **uploads** | `src/uploads/` 运行时写入，备份别漏 |

> AI生成