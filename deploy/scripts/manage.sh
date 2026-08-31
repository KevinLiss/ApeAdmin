#!/usr/bin/env bash
# =============================================================================
# ApeAdmin 日常运维脚本（服务器上运行）
# 用法: bash manage.sh <命令>   （不带参数查看帮助）
#
# 包结构为扁平化（项目根即原 backend/）: INSTALL_DIR 直接就是源码根。
# 服务名自动探测: 先找 apeadmin，再找宝塔常用的 pyproject_apeadmin；
# 都找不到时提示用宝塔面板操作。
# =============================================================================
set -euo pipefail

APP_NAME="${APP_NAME:-apeadmin}"
INSTALL_DIR="${INSTALL_DIR:-/www/wwwroot/${APP_NAME}}"
BACKEND="$INSTALL_DIR"              # 扁平结构：项目根即源码根（原 backend/）
ENV_FILE="$BACKEND/.env"

# ---- 工具函数 ----
get_env() { # 从 .env 读配置项
  grep -E "^${1}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'"'"''
}

detect_service() { # 探测 systemd 服务名
  for name in "$APP_NAME" "pyproject_${APP_NAME}"; do
    if systemctl list-unit-files 2>/dev/null | grep -q "^${name}\.service"; then
      SYSTEMD_NAME="$name"; return 0
    fi
  done
  return 1
}

need_systemd() {
  if ! detect_service; then
    echo "未找到 systemd 服务（试过 ${APP_NAME} / pyproject_${APP_NAME}）。"
    echo "请用宝塔面板操作: 网站 → Python项目 → ${APP_NAME} → 重启/日志"
    exit 1
  fi
}

usage() {
  cat <<EOF
用法: bash $0 <命令>

  status    服务状态（含 80 端口监听检查）
  restart   重启服务
  stop      停止服务
  logs      实时查看日志（Ctrl+C 退出）
  update    更新代码（先把新版包解压到 /tmp/apeadmin-update/，自动保留 .env/数据库/上传文件）
  backup    备份数据库(MySQL/SQLite 自动识别) + .env + uploads 到 $INSTALL_DIR/backup/
  restore   从备份恢复: bash $0 restore <备份目录>   如 restore /www/wwwroot/apeadmin/backup/20260901-0300
  shell     进入后端虚拟环境 Python shell
  pwd       显示项目根路径（宝塔项目路径应填的值）
EOF
  exit 1
}

[[ $# -ge 1 ]] || usage
cmd="$1"

case "$cmd" in
  status)
    if detect_service; then
      systemctl status "$SYSTEMD_NAME" --no-pager -l || true
    else
      echo "（未找到 systemd 服务，改用进程/端口探测）"
      pgrep -af "uvicorn src.main:app" || echo "进程未运行!"
    fi
    echo ""
    ss -tlnp 2>/dev/null | grep -E ":80\b" && echo "✓ 80 端口监听中" || echo "✗ 80 端口未监听!"
    ;;

  restart)
    need_systemd
    systemctl restart "$SYSTEMD_NAME" && echo "已重启"
    ;;

  stop)
    need_systemd
    systemctl stop "$SYSTEMD_NAME" && echo "已停止"
    ;;

  logs)
    need_systemd
    journalctl -u "$SYSTEMD_NAME" -f --no-pager -n 100
    ;;

  update)
    SRC="/tmp/apeadmin-update"
    # 兼容两种结构: 新版扁平包（$SRC/apeadmin/）与旧版（$SRC/backend/）
    if [[ -d "$SRC/apeadmin" ]]; then SRC="$SRC/apeadmin"; fi
    [[ -d "$SRC/src" ]] || { echo "请先把新版部署包解压到 /tmp/apeadmin-update/（应含 src/ 目录）"; exit 1; }
    echo "==> 停服更新（自动保留: .env / setup.lock / 数据库文件 / uploads）"
    if detect_service; then systemctl stop "$SYSTEMD_NAME" || true; fi
    rsync -a --delete \
      --exclude='.env' --exclude='setup.lock' --exclude='.venv' \
      --exclude='apeadmin.db*' --exclude='src/uploads/' \
      "$SRC/" "$BACKEND/"
    if detect_service; then systemctl start "$SYSTEMD_NAME"; fi
    echo "==> 完成，查看日志: bash $0 logs"
    ;;

  backup)
    DEST="$INSTALL_DIR/backup/$(date +%Y%m%d-%H%M)"
    mkdir -p "$DEST"
    DB_TYPE="$(get_env DB_TYPE)"
    echo "==> 数据库类型: ${DB_TYPE:-未配置(检查 .env)}"
    if [[ "$DB_TYPE" == "mysql" ]]; then
      DB_HOST="$(get_env DB_HOST)"; DB_PORT="$(get_env DB_PORT)"
      DB_USER="$(get_env DB_USER)"; DB_NAME="$(get_env DB_NAME)"
      DB_PASSWORD="$(get_env DB_PASSWORD)"
      [[ -n "$DB_NAME" && -n "$DB_USER" ]] || { echo ".env 缺少 DB_* 配置，无法备份 MySQL"; exit 1; }
      MYSQL_PWD="$DB_PASSWORD" mysqldump -h"${DB_HOST:-127.0.0.1}" -P"${DB_PORT:-3306}" \
        -u"$DB_USER" --single-transaction --routines --triggers "$DB_NAME" \
        > "$DEST/${DB_NAME}.sql"
      echo "    - MySQL 已导出: $DEST/${DB_NAME}.sql"
    elif [[ -f "$BACKEND/apeadmin.db" ]]; then
      sqlite3 "$BACKEND/apeadmin.db" ".backup '$DEST/apeadmin.db'"
      echo "    - SQLite 已备份: $DEST/apeadmin.db"
    else
      echo "    - 未识别到数据库，跳过（请检查 .env）"
    fi
    # .env 含 JWT_SECRET（API Key 解密依赖），必须随备份保存
    [[ -f "$ENV_FILE" ]] && cp "$ENV_FILE" "$DEST/.env.bak" && echo "    - .env 已备份（含 JWT_SECRET，务必妥善保管）"
    [[ -d "$BACKEND/src/uploads" ]] && cp -R "$BACKEND/src/uploads" "$DEST/" && echo "    - uploads 已备份"
    echo "==> 备份完成: $DEST"
    ;;

  restore)
    SRC_DIR="${2:-}"
    [[ -d "$SRC_DIR" ]] || { echo "用法: bash $0 restore <备份目录路径>"; exit 1; }
    echo "==> 停止服务"
    if detect_service; then systemctl stop "$SYSTEMD_NAME" || true; fi
    DB_TYPE="$(get_env DB_TYPE)"
    if [[ "$DB_TYPE" == "mysql" && -f "$SRC_DIR"/*.sql ]]; then
      DB_HOST="$(get_env DB_HOST)"; DB_PORT="$(get_env DB_PORT)"
      DB_USER="$(get_env DB_USER)"; DB_NAME="$(get_env DB_NAME)"
      DB_PASSWORD="$(get_env DB_PASSWORD)"
      MYSQL_PWD="$DB_PASSWORD" mysql -h"${DB_HOST:-127.0.0.1}" -P"${DB_PORT:-3306}" \
        -u"$DB_USER" "$DB_NAME" < "$SRC_DIR"/*.sql
      echo "    - MySQL 已导入"
    elif [[ -f "$SRC_DIR/apeadmin.db" ]]; then
      cp "$SRC_DIR/apeadmin.db" "$BACKEND/apeadmin.db"
      echo "    - SQLite 已恢复"
    fi
    [[ -f "$SRC_DIR/.env.bak" ]] && cp "$SRC_DIR/.env.bak" "$ENV_FILE" && echo "    - .env 已恢复"
    [[ -d "$SRC_DIR/uploads" ]] && rm -rf "$BACKEND/src/uploads" && cp -R "$SRC_DIR/uploads" "$BACKEND/src/uploads" && echo "    - uploads 已恢复"
    if detect_service; then systemctl start "$SYSTEMD_NAME"; fi
    echo "==> 恢复完成"
    ;;

  shell)
    cd "$BACKEND" && ./.venv/bin/python
    ;;

  pwd)
    echo "项目根: $BACKEND"
    echo "（宝塔 Python 项目路径应填: $BACKEND）"
    ;;

  *)
    usage ;;
esac
