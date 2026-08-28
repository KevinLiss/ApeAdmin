"""Safe ZIP inspection and DeepSeek-backed plugin documentation generation."""

from __future__ import annotations

import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import httpx

MAX_PACKAGE_SIZE = 50 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 5000
MAX_UNCOMPRESSED_SIZE = 200 * 1024 * 1024
MAX_SINGLE_TEXT_FILE = 1024 * 1024
MAX_PROMPT_CHARS = 180_000

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".json", ".md", ".toml",
    ".yaml", ".yml", ".ini", ".cfg", ".sql", ".css", ".scss", ".html", ".txt",
}
IGNORED_PARTS = {
    ".git", ".idea", ".vscode", "node_modules", "dist", "build", "coverage",
    "__pycache__", ".venv", "venv",
}
RISK_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("critical", re.compile(r"\b(eval|exec)\s*\("), "动态执行代码"),
    ("high", re.compile(r"\bos\.system\s*\("), "调用系统命令"),
    ("high", re.compile(r"subprocess\.[A-Za-z_]+\([^\n]{0,200}shell\s*=\s*True"), "使用 shell=True"),
    ("high", re.compile(r"\b(rm\s+-rf|shutil\.rmtree)\b"), "包含递归删除操作"),
    ("medium", re.compile(r"\b(requests|httpx|urllib3?)\.(get|post|request)\s*\("), "包含外部网络请求"),
    ("medium", re.compile(r"\b(open|Path)\s*\([^\n]{0,120}(/etc/|\.\./)"), "可能访问插件目录外路径"),
    ("high", re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*['\"][^'\"]{12,}"), "疑似硬编码凭据"),
)


class PackageValidationError(ValueError):
    pass


def _safe_member(info: zipfile.ZipInfo) -> PurePosixPath:
    path = PurePosixPath(info.filename.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise PackageValidationError(f"压缩包包含非法路径：{info.filename}")
    mode = info.external_attr >> 16
    if mode and stat.S_ISLNK(mode):
        raise PackageValidationError(f"压缩包包含符号链接：{info.filename}")
    return path


def inspect_package(package_path: Path) -> dict[str, Any]:
    """Inspect an untrusted plugin ZIP without extracting or executing it."""
    if not package_path.is_file():
        raise PackageValidationError("插件包不存在")
    if package_path.stat().st_size > MAX_PACKAGE_SIZE:
        raise PackageValidationError("插件包不能超过 50 MB")
    if not zipfile.is_zipfile(package_path):
        raise PackageValidationError("插件安装包必须是有效 ZIP 文件")

    file_tree: list[dict[str, Any]] = []
    text_sources: list[tuple[str, str]] = []
    manifest: dict[str, Any] | None = None
    warnings: list[dict[str, str]] = []
    total_uncompressed = 0

    with zipfile.ZipFile(package_path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ARCHIVE_ENTRIES:
            raise PackageValidationError("压缩包文件数量超过 5000")
        for info in infos:
            path = _safe_member(info)
            if info.flag_bits & 0x1:
                raise PackageValidationError(f"不支持加密文件：{info.filename}")
            if info.is_dir():
                continue
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_UNCOMPRESSED_SIZE:
                raise PackageValidationError("解压后总体积不能超过 200 MB")
            if info.compress_size and info.file_size / info.compress_size > 200:
                raise PackageValidationError(f"文件压缩比异常：{info.filename}")

            normalized = path.as_posix()
            file_tree.append({"path": normalized, "size": info.file_size})
            if any(part in IGNORED_PARTS for part in path.parts):
                continue
            if path.name == "plugin.json" and info.file_size <= MAX_SINGLE_TEXT_FILE:
                try:
                    candidate = json.loads(archive.read(info).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise PackageValidationError("plugin.json 不是有效 UTF-8 JSON") from exc
                if manifest is not None:
                    raise PackageValidationError("压缩包只能包含一个 plugin.json")
                manifest = candidate
            if path.suffix.lower() not in TEXT_EXTENSIONS or info.file_size > MAX_SINGLE_TEXT_FILE:
                continue
            try:
                content = archive.read(info).decode("utf-8")
            except UnicodeDecodeError:
                continue
            for severity, pattern, message in RISK_PATTERNS:
                if pattern.search(content):
                    warnings.append({"severity": severity, "file": normalized, "message": message})
            text_sources.append((normalized, content))

    if manifest is None:
        raise PackageValidationError("插件包缺少 plugin.json")
    for field in ("name", "version", "entry"):
        if not str(manifest.get(field, "")).strip():
            raise PackageValidationError(f"plugin.json 缺少必填字段：{field}")

    chunks: list[str] = []
    used = 0
    priority_names = {"plugin.json", "readme.md", "pyproject.toml", "package.json", "plugin.py", "api.py", "models.py"}
    text_sources.sort(key=lambda item: (Path(item[0]).name.lower() not in priority_names, item[0]))
    for filename, content in text_sources:
        block = f"\n\n--- FILE: {filename} ---\n{content}"
        if used + len(block) > MAX_PROMPT_CHARS:
            remaining = MAX_PROMPT_CHARS - used
            if remaining > 500:
                chunks.append(block[:remaining])
            break
        chunks.append(block)
        used += len(block)

    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    max_severity = max((warning["severity"] for warning in warnings), key=severity_rank.get, default="none")
    return {
        "manifest": manifest,
        "file_tree": file_tree,
        "file_count": len(file_tree),
        "uncompressed_size": total_uncompressed,
        "warnings": warnings,
        "risk_level": max_severity,
        "source_context": "".join(chunks),
        "source_truncated": sum(len(content) for _, content in text_sources) > len("".join(chunks)),
    }


def _documentation_prompt(report: dict[str, Any]) -> list[dict[str, str]]:
    system = (
        "你是 ApeAdmin/FastAPI 插件审核与技术文档专家。只根据提供的文件内容分析，"
        "不得编造不存在的接口。输出严格 JSON，包含 summary、features、architecture、"
        "installation、configuration、permissions、api、database、security、documentation_markdown。"
        "documentation_markdown 必须是完整中文 Markdown，适合直接进入 VitePress。"
    )
    payload = {
        "manifest": report["manifest"],
        "file_tree": report["file_tree"],
        "static_warnings": report["warnings"],
        "source": report["source_context"],
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "请分析以下插件并输出 json：\n" + json.dumps(payload, ensure_ascii=False)},
    ]


async def generate_documentation(
    report: dict[str, Any],
    *,
    api_key: str,
    base_url: str,
    model: str,
) -> tuple[dict[str, Any], dict[str, int]]:
    if not api_key:
        raise RuntimeError("DeepSeek API Key 未配置")
    endpoint = base_url.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": _documentation_prompt(report),
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 12000,
            },
        )
    response.raise_for_status()
    payload = response.json()
    content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError("DeepSeek 返回了空内容")
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("DeepSeek 未返回有效 JSON") from exc
    usage = payload.get("usage") or {}
    return result, {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
    }
