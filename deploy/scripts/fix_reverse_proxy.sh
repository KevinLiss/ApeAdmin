#!/usr/bin/env bash
# =============================================================================
# ApeAdmin 服务器端修复脚本（反代模式一键修复）
# 用途: 修复 systemd 服务配置(80→127.0.0.1:8000) + 检查服务状态
# 在服务器 root 终端执行: bash fix_reverse_proxy.sh
# =============================================================================
set -uo pipefail

SERVICE_FILE="/etc/systemd/system/apeadmin.service"
INSTALL_DIR="/www/wwwroot/apeadmin"

echo "===== ApeAdmin 反代模式修复 ====="
echo ""

# ---- 1. 检查文件是否存在 ----
if [[ ! -f "$SERVICE_FILE" ]]; then
  echo "[错误] 未找到服务文件 $SERVICE_FILE"
  echo "       请先在 $INSTALL_DIR 下执行: bash scripts/deploy.sh"
  exit 1
fi

echo "[1/5] 重写服务启动配置（127.0.0.1:8000 + 真实IP透传）"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=ApeAdmin Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
# 单 worker（插件热拔插运行态为进程本地，多 worker 不支持）
# proxy-headers: Nginx 反代场景还原真实客户端 IP
ExecStart=${INSTALL_DIR}/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
echo "      已写入 $SERVICE_FILE"

# ---- 2. 重载并重启 ----
echo "[2/5] 重载 systemd 并重启服务"
systemctl daemon-reload
systemctl enable apeadmin >/dev/null 2>&1
systemctl restart apeadmin 2>/dev/null || true
sleep 4

# ---- 3. 状态检查 ----
echo "[3/5] 服务状态"
systemctl is-active apeadmin --quiet && echo "      ✓ 服务运行中 (active)" || {
  echo "      ✗ 服务未运行，最近日志:"
  journalctl -u apeadmin -n 15 --no-pager | sed 's/^/        /'
}

# ---- 4. 健康检查 ----
echo "[4/5] 健康检查 (http://127.0.0.1:8000/health)"
for i in 1 2 3 4 5; do
  RESP=$(curl -s -m 3 http://127.0.0.1:8000/health 2>/dev/null)
  if [[ -n "$RESP" ]]; then
    echo "      ✓ 响应: $RESP"
    break
  fi
  [[ $i -eq 5 ]] && echo "      ✗ 无响应（服务可能仍启动失败，查看日志: journalctl -u apeadmin -n 30）"
  sleep 2
done

# ---- 5. 端口与 Nginx 提示 ----
echo "[5/5] 端口监听情况"
ss -tlnp 2>/dev/null | grep -E ":(80|8000)\b" | sed 's/^/      /' || echo "      (无 80/8000 监听)"

echo ""
echo "===== 完成 ====="
echo "若上方健康检查返回 JSON（含 status），则服务侧已就绪。"
echo "接下来只需在宝塔站点配置反向代理（不是重定向!）:"
echo "  站点设置 → 反向代理 → 添加反向代理 → 目标URL http://127.0.0.1:8000"
