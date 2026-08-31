#!/usr/bin/env bash
# =============================================================================
# ApeAdmin 生产部署包打包脚本（在开发机 macOS 上运行）
#
# 用法:
#   bash build_deploy_package.sh                     # 底座模式（默认）
#   bash build_deploy_package.sh --with-apehub       # 底座 + apehub_web 官网插件
#
# 底座模式（默认）:
#   只打包管理后台底座（RBAC/菜单/插件框架/MCP），不含 apehub_web 官网插件。
#   首次启动进入 /setup 安装向导：选数据库 → 配账号/域名 → 完成。
#
# 包结构（扁平化：解压出来直接就是项目根，无需重命名、无需进子目录）:
#   apeadmin.tar.gz 解压后:
#   apeadmin/
#   ├── src/                后端源码（含 frontend_dist/ 管理后台构建产物）
#   ├── requirements.txt    生产依赖锁定版本
#   ├── scripts/            服务器端部署/管理脚本
#   ├── nginx/              Nginx 配置模板（仅以后上 HTTPS 用）
#   ├── .env.example        环境变量参考模板
#   └── DEPLOY.md           部署文档
#
#   宝塔 Python 项目「项目路径」直接选 /www/wwwroot/apeadmin 即可。
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND="$PROJECT_ROOT/backend"
OUT_DIR="$SCRIPT_DIR/dist"
STAGE="$SCRIPT_DIR/.stage"

WITH_APEHUB=0
for arg in "$@"; do
  case "$arg" in
    --with-apehub) WITH_APEHUB=1 ;;
    *) echo "[忽略] 未知参数: $arg" ;;
  esac
done

DATE_TAG=$(date +%Y%m%d-%H%M)
if [[ $WITH_APEHUB -eq 1 ]]; then
  PKG_NAME="apeadmin-full"
else
  PKG_NAME="apeadmin-base"
fi
PKG_FILE="$OUT_DIR/${PKG_NAME}-${DATE_TAG}.tar.gz"

# ---------------------------------------------------------------- 检查前置
if [[ ! -f "$BACKEND/src/main.py" ]]; then
  echo "[错误] 未找到后端代码: $BACKEND/src/main.py" >&2
  exit 1
fi
if [[ ! -d "$BACKEND/frontend_dist" ]]; then
  echo "[错误] 缺少 backend/frontend_dist/，请先构建前端:" >&2
  echo "       cd frontend && npx vite build && rm -rf backend/frontend_dist && cp -r frontend/dist backend/frontend_dist" >&2
  exit 1
fi

echo "==> [1/6] 清理并准备暂存目录"
rm -rf "$STAGE"
mkdir -p "$STAGE/apeadmin"
STAGE_PKG="$STAGE/apeadmin"

echo "==> [2/6] 复制后端代码到扁平结构（剔除开发文件）"
# 后端源码直接放包根的 src/（不再有 backend/ 一层）
mkdir -p "$STAGE_PKG"
(cd "$PROJECT_ROOT" && git ls-files backend --exclude-standard -z |
  xargs -0 -I{} rsync -R "{}" "$STAGE_PKG/" 2>/dev/null) || true
# rsync -R 保留了 backend/ 前缀，改平到根
if [[ -d "$STAGE_PKG/backend" ]]; then
  (cd "$STAGE_PKG" && mv backend/* . && rmdir backend)
fi

# 覆盖式补充构建产物（frontend_dist 被 gitignore，需单独带）
rm -rf "$STAGE_PKG/frontend_dist"
cp -R "$BACKEND/frontend_dist" "$STAGE_PKG/frontend_dist"

# 迁移脚本兜底（git ls-files 之外的 backend/scripts，防止未提交时漏带）
if [[ -d "$BACKEND/scripts" && ! -d "$STAGE_PKG/scripts" ]]; then
  echo "    - 兜底补充 scripts/（迁移脚本）"
  mkdir -p "$STAGE_PKG/scripts"
  cp "$BACKEND/scripts/"*.py "$STAGE_PKG/scripts/" 2>/dev/null || true
fi

# 底座模式：剔除 apehub_web 官网插件（含源码、静态页、迁移链）
if [[ $WITH_APEHUB -eq 0 ]]; then
  echo "    - 底座模式：剔除 apehub_web 插件"
  rm -rf "$STAGE_PKG/src/plugins/builtin/apehub_web"
  # 插件相关测试与前端构建残留（无运行时硬依赖，纯粹不误导用户）
  rm -f  "$STAGE_PKG/tests/test_apehub_web_marketplace.py"
  find "$STAGE_PKG/frontend_dist" -name "apehub_web*" -delete 2>/dev/null || true
fi

# docs-site 产物已在 static/docs-portal，源码+node_modules 不进包
rm -rf "$STAGE_PKG/src/plugins/builtin/apehub_web/docs-site"
# 官网前端源码备份不进包（产物已在 static/）
rm -rf "$STAGE_PKG/apehub_web"

echo "==> [3/6] 复制部署配套文件（nginx/脚本/模板/文档）"
mkdir -p "$STAGE_PKG/nginx"
cp "$SCRIPT_DIR/nginx/apeadmin.conf" "$STAGE_PKG/nginx/"
cp "$SCRIPT_DIR/scripts/manage.sh" "$STAGE_PKG/scripts/manage.sh"
cp "$SCRIPT_DIR/scripts/deploy.sh" "$STAGE_PKG/scripts/deploy.sh" 2>/dev/null || true
chmod +x "$STAGE_PKG/scripts/"*.sh
cp "$SCRIPT_DIR/.env.example" "$STAGE_PKG/.env.example"
cp "$SCRIPT_DIR/DEPLOY.md" "$STAGE_PKG/DEPLOY.md"

echo "==> [4/6] 清理字节码与缓存"
find "$STAGE_PKG" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$STAGE_PKG" -name "*.pyc" -delete 2>/dev/null || true
find "$STAGE_PKG" -name ".DS_Store" -delete 2>/dev/null || true

echo "==> [5/6] 生成依赖锁文件 requirements.txt（生产固定版本）"
cat > "$STAGE_PKG/requirements.txt" <<'REQ'
# ApeAdmin 生产依赖（版本取自开发环境实测可用的组合）
fastapi[standard]==0.141.1
uvicorn[standard]==0.52.4
sqlalchemy[asyncio]==2.0.52
aiosqlite==0.22.1
aiomysql==0.3.2
alembic==1.19.1
pydantic==2.13.4
pydantic-settings==2.15.0
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.32
mcp==2.0.0
httpx==0.28.1
loguru==0.7.3
rich==15.0.0
typer==0.27.1
redis==8.1.0
orjson==3.12.0
psutil==7.2.2
REQ

echo "==> [6/6] 打 tar 包"
mkdir -p "$OUT_DIR"
tar -czf "$PKG_FILE" -C "$STAGE" "apeadmin"

echo ""
echo "============================================"
echo " 打包完成（$([[ $WITH_APEHUB -eq 1 ]] && echo 完整版 || echo 底座版)）"
echo " 文件: $PKG_FILE"
echo " 大小: $(du -h "$PKG_FILE" | cut -f1)"
echo " 结构（解压即 apeadmin/，项目路径直接选它）:"
tar -tzf "$PKG_FILE" | awk -F/ '{print $1"/"$2}' | sort -u | head -12
echo "============================================"
echo "提示: 解压后宝塔项目路径填 /www/wwwroot/apeadmin（不用再进子目录）"
echo "      首次启动自动进入 /setup 安装向导"
if [[ $WITH_APEHUB -eq 0 ]]; then
  echo "      如需连带 apehub_web 官网插件: bash build_deploy_package.sh --with-apehub"
fi
