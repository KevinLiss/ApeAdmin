#!/usr/bin/env bash
# AI 会议助手（aimeeting 插件）环境搭建脚本
# 用途：在新机器 / 重建 venv 后补齐语音转写运行环境。
#   [1] 安装 Python 推理依赖（pyproject [meeting] 可选依赖组）
#   [2] 补齐 backend/models/ 下的三个模型
# 幂等：重复执行安全（依赖已装则 pip 自动跳过，模型存在则不下载）。
# 注意：sherpa 两个模型不在 HF 官方标准仓库，推荐直接从现有部署机拷贝整个
#       backend/models/ 目录（约 530M，内含已通过验证的文件布局）。
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="$BACKEND_DIR/models"
PY="$BACKEND_DIR/.venv/bin/python"
PIP="$BACKEND_DIR/.venv/bin/pip"

echo "==> backend: $BACKEND_DIR"

if [ ! -x "$PY" ]; then
  echo "!! 未找到 venv（$PY）。请先创建虚拟环境并安装 apeadmin 基础依赖："
  echo "   cd $BACKEND_DIR && python3 -m venv .venv && .venv/bin/pip install -e ."
  exit 1
fi

echo "==> [1/3] 安装 AI 推理依赖（meeting 可选组）"
"$PIP" install -e "$BACKEND_DIR[meeting]" \
  || { echo "!! pip 失败。网络受限时可加镜像：PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple 重试"; exit 1; }

echo "==> [2/3] 检查模型目录 $MODELS_DIR"
mkdir -p "$MODELS_DIR"

need_whisper=0; need_diar=0; need_stream=0
[ -f "$MODELS_DIR/faster-whisper-small/model.bin" ] || need_whisper=1
ls "$MODELS_DIR/sherpa-diarization/"*.onnx   >/dev/null 2>&1 || need_diar=1
[ -f "$MODELS_DIR/sherpa-streaming-zh-14m/encoder.int8.onnx" ] || need_stream=1

if [ "$need_whisper" = 1 ]; then
  echo "  ↓ 下载 faster-whisper-small（Systran/faster-whisper-small）"
  # 镜像可用 HF_ENDPOINT=https://hf-mirror.com 前缀重试
  "$PY" -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Systran/faster-whisper-small',
                  local_dir='$MODELS_DIR/faster-whisper-small')
print('  whisper-small OK')
" || echo "  !! whisper 下载失败：请设置 HF_ENDPOINT 镜像/代理后重跑本脚本，或从现有机器拷贝 $MODELS_DIR/faster-whisper-small"
fi

if [ "$need_diar" = 1 ] || [ "$need_stream" = 1 ]; then
  echo "  ⚠ sherpa 模型（说话人分离 / 实时流式）无法从公开 HF 仓库一键获取："
  [ "$need_diar" = 1 ]   && echo "    - 缺 $MODELS_DIR/sherpa-diarization/（*.onnx）"
  [ "$need_stream" = 1 ] && echo "    - 缺 $MODELS_DIR/sherpa-streaming-zh-14m/（encoder/decoder/joiner.int8.onnx + tokens.txt）"
  echo "    推荐从现有部署机直接拷贝 backend/models/ 对应目录（约 67M）；"
  echo "    缺失不阻塞：仅降级（无说话人区分 / 无会中实时流式，离线转写仍可用）。"
fi

echo "==> [3/3] 环境自检验证"
cd "$BACKEND_DIR"
"$PY" - <<PYEOF
import sys
sys.path.insert(0, "$BACKEND_DIR")
from src.plugins.builtin.aimeeting.envcheck import check_env
r = check_env()
s = r["summary"]
print(f"overall = {r['overall']}   deps {s['deps_ok']}/{s['deps_total']}   models {s['models_ok']}/{s['models_total']}")
for m in r["models"]:
    print(f"  [{'OK' if m['ok'] else '--'}] {m['name']}  {m['size_mb']}MB  {m['path']}" + (f"  缺:{m['missing_files']}" if m['ok'] and m['missing_files'] else ""))
if s["missing_deps"]: print("缺依赖:", s["missing_deps"])
if s["missing_critical_models"]: print("缺核心模型:", s["missing_critical_models"])
if s["degraded_models"]: print("降级模型:", s["degraded_models"])
PYEOF

echo
echo "完成。如 overall 非 ready，按提示补齐后重启后端（重启须脱离会话，防被回收）："
echo "  cd $BACKEND_DIR && nohup .venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000 >> /tmp/aimeeting-uvicorn.log 2>&1 &"
