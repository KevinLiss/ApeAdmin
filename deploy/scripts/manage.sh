#!/usr/bin/env bash
# =============================================================================
# ApeAdmin 日常运维脚本（服务器上运行）
# 用法:
#   bash manage.sh {status|restart|stop|logs|update|backup|shell}
# =============================================================================
set -euo pipefail

APP_NAME="${APP_NAME:-apeadmin}"
INSTALL_DIR="${INSTALL_DIR:-/www/wwwroot/${APP_NAME}}"
BACKEND="$INSTALL_DIR/backend"

usage() {
  cat <<EOF
用法: bash $0 <命令>

  status   服务状态
  restart  重启服务
  stop     停止服务
  logs     实时查看日志（Ctrl+C 退出）
  update   更新代码目录（需先把新版 backend/ 放到 /tmp/apeadmin-update/）
  backup   备份数据库与 uploads 到 $INSTALL_DIR/backup/
  shell    进入后端虚拟环境 Python shell
EOF
  exit 1
}

[[ $# -eq 1 ]] || usage
cmd="$1"

case "$cmd" in
  status)
    systemctl status "$APP_NAME" --no-pager -l ;;
  restart)
    systemctl restart "$APP_NAME" && echo "已重启" ;;
  stop)
    systemctl stop "$APP_NAME" && echo "已停止" ;;
  logs)
    journalctl -u "$APP_NAME" -f --no-pager -n 100 ;;
  update)
    SRC="/tmp/apeadmin-update"
    [[ -d "$SRC/backend" ]] || { echo "请把新版部署包解压到 /tmp/apeadmin-update/"; exit 1; }
    echo "==> 停服更新"
    systemctl stop "$APP_NAME" || true
    rsync -a --delete --exclude='.env' --exclude='.venv' \
          --exclude='apeadmin.db*' --exclude='src/uploads/' \
          "$SRC/backend/" "$BACKEND/"
    chown -R www:www "$INSTALL_DIR" 2>/dev/null || true
    systemctl start "$APP_NAME"
    echo "==> 完成，查看日志: bash $0 logs" ;;
  backup)
    DEST="$INSTALL_DIR/backup/$(date +%Y%m%d-%H%M)"
    mkdir -p "$DEST"
    if [[ -f "$BACKEND/apeadmin.db" ]]; then
      sqlite3 "$BACKEND/apeadmin.db" ".backup '$DEST/apeadmin.db'"
    fi
    [[ -d "$BACKEND/src/uploads" ]] && cp -R "$BACKEND/src/uploads" "$DEST/"
    echo "已备份到 $DEST" ;;
  shell)
    cd "$BACKEND" && ./.venv/bin/python ;;
  *)
    usage ;;
esac
