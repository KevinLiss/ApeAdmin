#!/usr/bin/env bash
# =============================================================================
# ApeAdmin 服务器端一键部署脚本（宝塔 / CentOS / Ubuntu 通用）
#
# 在服务器上以 root 或 sudo 用户运行:
#   bash deploy.sh
#
# 前置要求:
#   1. 部署包已解压到任意目录（包内自带 backend/ nginx/ scripts/）
#   2. 已安装 Python 3.11+（宝塔: 软件商店 → Python 项目管理器 2.0 可装）
#      没有时脚本会尝试用系统 python3 并提示版本
#   3. 如用 MySQL: 先在宝塔建好库和用户，并配好 .env
#
# 脚本行为:
#   - 创建运行用户/目录（默认 /www/wwwroot/apeadmin）
#   - 建立 venv 并安装 requirements.txt
#   - 引导生成 .env（交互式，或提前放好则跳过）
#   - 检测到本地迁移库 apeadmin.db 时提示执行 SQLite → MySQL 迁移
#   - 配置 systemd 守护进程并启动
#   - 输出后续 Nginx 配置提示
# =============================================================================
set -euo pipefail

# ---- 可调参数（可用环境变量覆盖） ----
APP_NAME="${APP_NAME:-apeadmin}"
INSTALL_DIR="${INSTALL_DIR:-/www/wwwroot/${APP_NAME}}"
RUN_USER="${RUN_USER:-www}"
PORT="${PORT:-8000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 部署包根目录（backend/ 所在处）
PKG_ROOT="$(dirname "$SCRIPT_DIR")"

log()  { echo -e "\033[32m[部署]\033[0m $*"; }
warn() { echo -e "\033[33m[警告]\033[0m $*" >&2; }
die()  { echo -e "\033[31m[错误]\033[0m $*" >&2; exit 1; }

# ---------------------------------------------------------------- 0. 前置检查
[[ $EUID -eq 0 ]] || die "请用 root 或 sudo 运行"
[[ -d "$PKG_ROOT/backend" ]] || die "未找到 $PKG_ROOT/backend，请在部署包解压目录内运行"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || die "未找到 $PYTHON_BIN"

PY_VER=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
log "检测到 Python $PY_VER"
"$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' \
  || die "需要 Python 3.11+（宝塔: 软件商店 → Python 项目管理器 安装后用 PYTHON_BIN=/路径/python3 重新运行）"

# ---------------------------------------------------------------- 1. 目录与用户
log "部署目录: $INSTALL_DIR"
id "$RUN_USER" >/dev/null 2>&1 || RUN_USER=root
[[ "$RUN_USER" == "root" ]] && warn "使用 root 运行服务，建议用宝塔 www 用户"

mkdir -p "$INSTALL_DIR"
log "复制代码到 $INSTALL_DIR"
rsync -a --delete "$PKG_ROOT/backend/" "$INSTALL_DIR/backend/"
[[ -d "$INSTALL_DIR/backend/src" ]] || die "复制失败"

# uploads 目录提前建好并赋权
mkdir -p "$INSTALL_DIR/backend/src/uploads/plugins" \
         "$INSTALL_DIR/backend/src/uploads/files" \
         "$INSTALL_DIR/backend/src/uploads/apehub_web"
chown -R "$RUN_USER":"$RUN_USER" "$INSTALL_DIR" 2>/dev/null || true

# ---------------------------------------------------------------- 2. 虚拟环境
log "创建虚拟环境并安装依赖（约 1~3 分钟）"
cd "$INSTALL_DIR/backend"
if [[ ! -d .venv ]]; then
  "$PYTHON_BIN" -m venv .venv
fi
./.venv/bin/pip install --upgrade pip -q
./.venv/bin/pip install -r requirements.txt -q \
  || die "依赖安装失败，请检查网络（可用: pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/）"
log "依赖安装完成"

# ---------------------------------------------------------------- 3. 环境变量
if [[ ! -f "$INSTALL_DIR/backend/.env" ]]; then
  if [[ -f "$PKG_ROOT/.env.example" ]]; then
    cp "$PKG_ROOT/.env.example" "$INSTALL_DIR/backend/.env"
    # 生成随机 JWT_SECRET 写入
    SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | od -An -tx1 | tr -d ' \n')
    sed -i.bak "s|^JWT_SECRET=.*|JWT_SECRET=${SECRET}|" "$INSTALL_DIR/backend/.env" && rm -f "$INSTALL_DIR/backend/.env.bak"
    chown "$RUN_USER":"$RUN_USER" "$INSTALL_DIR/backend/.env" 2>/dev/null || true
    chmod 600 "$INSTALL_DIR/backend/.env"
    log "已生成 .env（随机 JWT_SECRET）"
    warn "请编辑 $INSTALL_DIR/backend/.env 修改:"
    warn "  - SUPER_ADMIN_PASSWORD（管理后台初始密码）"
    warn "  - CORS_ORIGINS（你的域名）"
    warn "  - 如用 MySQL: DB_TYPE=mysql 及 DB_* 五项"
  else
    warn "未找到 .env.example，请手工创建 $INSTALL_DIR/backend/.env"
  fi
else
  log "检测到已有 .env，跳过生成"
fi

# ---------------------------------------------------------------- 4. 数据迁移（可选）
# 检测到包内/目录里的 apeadmin.db 且目标库为空时，引导执行 SQLite → MySQL 迁移
MIGRATE_HINT=0
if [[ -f "$INSTALL_DIR/backend/apeadmin.db" ]]; then
  # 读取 .env 的 DB_TYPE
  ENV_DB_TYPE=$(grep -E '^DB_TYPE=' "$INSTALL_DIR/backend/.env" 2>/dev/null | tail -1 | cut -d= -f2 | tr -d ' "' || true)
  if [[ "$ENV_DB_TYPE" == "mysql" ]]; then
    MIGRATE_HINT=1
  fi
fi
if [[ $MIGRATE_HINT -eq 1 ]]; then
  echo ""
  warn "检测到 apeadmin.db 且 .env 已配 MySQL。若需把开发库数据迁到 MySQL，运行:"
  warn "  cd $INSTALL_DIR/backend"
  warn "  ./.venv/bin/python -m scripts.migrate_sqlite_to_mysql \\"
  warn "      --source apeadmin.db --old-jwt-secret '<本地开发用的JWT_SECRET>'"
  warn "  （旧 JWT_SECRET 指开发库加密数据所用的密钥；不带 --old-jwt-secret 则不轮换密钥，"
  warn "   会导致开发库中已存的 AI Key/邮箱码等密文在新密钥下解不开）"
  warn "  迁移完成后可删除 apeadmin.db 避免误用。"
  echo ""
fi

# ---------------------------------------------------------------- 5. systemd 守护
log "配置 systemd 服务"
UNIT=/etc/systemd/system/${APP_NAME}.service
cat > "$UNIT" <<EOF
[Unit]
Description=ApeAdmin Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${INSTALL_DIR}/backend
# 单 worker（插件热拔插运行态为进程本地，多 worker 不支持）
ExecStart=${INSTALL_DIR}/backend/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port ${PORT} --workers 1
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${APP_NAME}" >/dev/null 2>&1
systemctl restart "${APP_NAME}"

# ---------------------------------------------------------------- 6. 健康检查
log "等待服务启动..."
sleep 4
if curl -sf -o /dev/null "http://127.0.0.1:${PORT}/api/v1/auth/login" -X POST \
     -H "Content-Type: application/json" -d '{"username":"__probe__","password":"__probe__"}' 2>/dev/null \
   || curl -sf -o /dev/null "http://127.0.0.1:${PORT}/docs"; then
  log "服务已在 127.0.0.1:${PORT} 启动 ✅"
else
  warn "健康检查未通过，查看日志: journalctl -u ${APP_NAME} -n 50"
fi

# ---------------------------------------------------------------- 7. 收尾提示
cat <<EOF

============================================================
 部署完成

 服务管理:
   systemctl status  ${APP_NAME}    # 状态
   systemctl restart ${APP_NAME}    # 重启
   journalctl -u ${APP_NAME} -f     # 实时日志

  接下来手工完成:
    1. 编辑配置:  vim ${INSTALL_DIR}/backend/.env
                 （改完 systemctl restart ${APP_NAME}）
    2. 迁移数据:  若从开发库迁移，见上方提示（scripts.migrate_sqlite_to_mysql）
    3. Nginx:     参考包内 nginx/apeadmin.conf，
                 在宝塔站点配置中反代到 127.0.0.1:${PORT}
    4. 访问:      http://域名/admin/  （初始账号见 .env 中 SUPER_ADMIN_*）
                 http://域名/         （官网首页）
    5. 放行端口:  宝塔安全组只需放行 80/443，8000 不对外
============================================================
EOF
