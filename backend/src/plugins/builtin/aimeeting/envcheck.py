"""AI 会议助手插件——运行环境自检（只读，不安装、不改系统）。

用途：
- 插件 install()/register() 时探测依赖库与模型文件是否就绪，缺失只 warning 降级、不阻塞启动；
- 为管理端「运行环境」诊断页提供 GET /aimeeting/env/check 数据。

设计约束（与运维决策一致）：
- **只报告，绝不在线 pip install / 下载模型**。环境补齐交给 scripts/setup_aimeeting_env.sh。
- 探测必须轻量：import 探测用 importlib.util.find_spec（不触发真正 import，零副作用、快），
  模型探测只 stat 目录与关键文件，不加载权重。
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from loguru import logger

# backend/ 根目录（.../backend/src/plugins/builtin/aimeeting/envcheck.py 向上 4 级）
BACKEND_DIR = Path(__file__).resolve().parents[4]
MODELS_DIR = BACKEND_DIR / "models"

# ── 依赖库声明（与 pyproject.toml [project.optional-dependencies].meeting 对齐）──
# key=import 名, value={pip 包名, 期望版本(仅提示不强制), 用途}
_PY_DEPS: list[dict[str, str]] = [
    {"import": "faster_whisper", "pip": "faster-whisper", "want": "1.2.1", "role": "离线语音转写（Whisper 高性能推理）"},
    {"import": "ctranslate2", "pip": "ctranslate2", "want": "4.8.2", "role": "faster-whisper 推理引擎（CPU int8）"},
    {"import": "sherpa_onnx", "pip": "sherpa-onnx", "want": "1.13.7", "role": "说话人分离 + 流式中文识别"},
    {"import": "onnxruntime", "pip": "onnxruntime", "want": "1.29.0", "role": "sherpa-onnx 的 ONNX 推理后端"},
    {"import": "av", "pip": "av", "want": "18.1.0", "role": "音频解码 / 切片 / merged.wav 合并"},
    {"import": "numpy", "pip": "numpy", "want": "2.5.3", "role": "音频数值计算"},
    {"import": "tokenizers", "pip": "tokenizers", "want": "0.23.2", "role": "流式模型分词"},
    {"import": "huggingface_hub", "pip": "huggingface_hub", "want": "1.30.0", "role": "模型下载（部署脚本用，运行时可选）"},
]

# ── 模型文件声明（目录 + 必需文件）──
# 允许用环境变量覆盖路径（与 services.py / streaming.py 保持一致）
import os

_WHISPER_DIR = Path(os.environ.get("AIMEETING_WHISPER_MODEL", MODELS_DIR / "faster-whisper-small"))
_DIAR_DIR = Path(os.environ.get("AIMEETING_DIARIZATION_MODEL", MODELS_DIR / "sherpa-diarization"))
# 注意：streaming.py 中流式模型路径为硬编码（不读环境变量），此处保持一致以免自检与实际加载路径不符
_STREAM_DIR = MODELS_DIR / "sherpa-streaming-zh-14m"

_MODELS: list[dict[str, Any]] = [
    {
        "name": "faster-whisper-small",
        "path": _WHISPER_DIR,
        "required_any": ["model.bin"],          # CTranslate2 权重
        "optional": ["config.json", "tokenizer.json", "vocabulary.txt"],
        "role": "离线转写主模型（缺 → 转写完全不可用）",
        "critical": True,
    },
    {
        "name": "sherpa-diarization",
        "path": _DIAR_DIR,
        "required_any": ["segmentation.onnx", "embedding.onnx"],
        "optional": [],
        "require_all": ["segmentation.onnx", "embedding.onnx"],
        "role": "说话人分离模型（缺 → 说话人区分不可用，转写仍可用）",
        "critical": False,
    },
    {
        "name": "sherpa-streaming-zh-14m",
        "path": _STREAM_DIR,
        "required_any": ["encoder.int8.onnx"],
        "require_all": ["tokens.txt", "encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx"],
        "optional": [],
        "role": "实时流式识别模型（缺 → 会议中实时转写不可用，可走离线切片转写）",
        "critical": False,
    },
]


@dataclass
class DepStatus:
    """单个依赖库的探测结果。"""
    pip: str
    import_name: str
    role: str
    wanted: str
    installed: str = ""
    ok: bool = False
    note: str = ""


@dataclass
class ModelStatus:
    """单个模型的探测结果。"""
    name: str
    path: str
    role: str
    critical: bool
    exists: bool = False
    size_mb: float = 0.0
    missing_files: list[str] = field(default_factory=list)
    ok: bool = False


def _check_python_deps() -> list[DepStatus]:
    out: list[DepStatus] = []
    for spec in _PY_DEPS:
        imp, pipname = spec["import"], spec["pip"]
        st = DepStatus(pip=pipname, import_name=imp, role=spec["role"], wanted=spec["want"])
        # find_spec 只查元数据、不执行模块顶层代码，安全快速
        found = importlib.util.find_spec(imp) is not None
        st.ok = found
        if found:
            try:
                st.installed = importlib.metadata.version(pipname)
            except importlib.metadata.PackageNotFoundError:
                st.installed = "已导入（未记录版本）"
        else:
            st.note = f"未安装，请 pip install {pipname}=={spec['want']}（或运行 setup_aimeeting_env.sh）"
        out.append(st)
    return out


def _dir_size_mb(p: Path) -> float:
    total = 0
    try:
        for f in p.rglob("*"):
            if f.is_file():
                try:
                    total += f.stat().st_size
                except OSError:
                    pass
    except OSError:
        return 0.0
    return round(total / 1024 / 1024, 1)


def _check_models() -> list[ModelStatus]:
    out: list[ModelStatus] = []
    for spec in _MODELS:
        path: Path = spec["path"]
        st = ModelStatus(
            name=spec["name"], path=str(path), role=spec["role"], critical=spec["critical"]
        )
        if path.exists() and path.is_dir():
            st.exists = True
            st.size_mb = _dir_size_mb(path)
            required_any: list[str] = spec["required_any"]
            require_all: list[str] = spec.get("require_all", [])
            missing: list[str] = []
            # require_all：全部必需文件在才算就绪（如声纹 segmentation+embedding 需同时存在）
            if require_all:
                ok = all((path / f).exists() for f in require_all)
                missing = [f for f in require_all if not (path / f).exists()]
            else:
                # required_any：任一关键文件存在即视为就绪
                ok = any((path / f).exists() for f in required_any)
                if not ok:
                    missing = list(required_any)
            # 可选文件缺失单独记录（不影响 ok，仅提示）
            opt_missing = [f for f in spec["optional"] if not (path / f).exists()]
            st.ok = ok
            st.missing_files = missing + ([f"(可选) {f}" for f in opt_missing] if not missing else [])
        else:
            st.missing_files = spec.get("require_all") or spec["required_any"]
        out.append(st)
    return out


def _check_ffmpeg() -> dict[str, Any]:
    """系统 ffmpeg 可执行文件（录音格式转换会用；av/PyAV 自带解码，故非硬性）。"""
    exe = shutil.which("ffmpeg")
    return {"available": bool(exe), "path": exe or "", "note": "" if exe else "未找到系统 ffmpeg（多数场景 PyAV 已可解码，非硬性）"}


def check_env() -> dict[str, Any]:
    """执行全量自检，返回结构化结果（含总状态），供 API 与启动日志共用。"""
    deps = _check_python_deps()
    models = _check_models()
    ffmpeg = _check_ffmpeg()

    missing_deps = [d.pip for d in deps if not d.ok and d.pip != "huggingface_hub"]
    missing_critical_models = [m.name for m in models if m.critical and not m.ok]
    degraded_models = [m.name for m in models if not m.critical and not m.ok]

    if missing_deps or missing_critical_models:
        overall = "broken"          # 核心转写不可用
    elif degraded_models:
        overall = "degraded"        # 主流程可用，部分能力降级
    else:
        overall = "ready"

    return {
        "overall": overall,
        "summary": {
            "deps_ok": sum(1 for d in deps if d.ok),
            "deps_total": len(deps),
            "models_ok": sum(1 for m in models if m.ok),
            "models_total": len(models),
            "missing_deps": missing_deps,
            "missing_critical_models": missing_critical_models,
            "degraded_models": degraded_models,
        },
        "python": {
            "version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
        },
        "dependencies": [asdict(d) for d in deps],
        "models": [asdict(m) for m in models],
        "ffmpeg": ffmpeg,
    }


def log_startup_check(source: str = "register") -> dict[str, Any]:
    """插件启动自检：打印 warning（缺失时）并返回结果。永不抛异常、不阻塞启动。"""
    try:
        result = check_env()
    except Exception as exc:  # 自检本身出错也绝不能影响启动
        logger.warning(f"[aimeeting] env check failed (ignored): {exc}")
        return {"overall": "unknown", "error": str(exc)}

    s = result["summary"]
    if result["overall"] == "ready":
        logger.info(
            f"[aimeeting] env OK ({source}) — deps {s['deps_ok']}/{s['deps_total']}, "
            f"models {s['models_ok']}/{s['models_total']}"
        )
    elif result["overall"] == "degraded":
        logger.warning(
            f"[aimeeting] env DEGRADED ({source}) — 可选模型缺失: {s['degraded_models']}；"
            f"会议实时流式/说话人分离部分能力不可用，详见后台「运行环境」页"
        )
    else:
        logger.warning(
            f"[aimeeting] env BROKEN ({source}) — 缺依赖 {s['missing_deps']}, "
            f"缺核心模型 {s['missing_critical_models']}；转写功能不可用，"
            f"请运行 scripts/setup_aimeeting_env.sh 补齐环境后重启后端"
        )
    return result
