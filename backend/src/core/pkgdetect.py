"""Deployment-package and plugin-package type detection.

Two base stacks exist in the ApeAdmin ecosystem:

- Python base (this repo, FastAPI):
    * Plugin package: .zip with plugin.json (no ``type`` or ``type != "l2"``)
      plus a python package dir ``{name}/__init__.py``.
    * Upgrade package: .tar.gz whose top-level dir contains ``src/``.
- Go base (ApeAdmin-Gin):
    * Plugin package: .zip with plugin.json declaring ``"type": "l2"`` plus
      optional menu.json / seed.sql; must NOT contain __init__.py; rejects
      executables (.so/.dll/.exe/.bin).

Users occasionally upload a package built for the other stack.  Rather than
failing with a low-level error ("缺少 __init__.py"), we detect the mismatch
early and return an explicit, actionable message.
"""

import json
import tarfile
import zipfile
from pathlib import Path
from typing import Any

# Extensions that mark a package as Go-stack-only (zipguard.go rejects them).
_GO_ONLY_EXTS = {".so", ".dll", ".exe", ".bin"}


def detect_zip_kind(zip_path: Path) -> str:
    """Classify a .zip archive as ``go`` / ``python`` / ``unknown``.

    Decision order (most specific first):
    1. plugin.json with ``type == "l2"`` → go
    2. plugin.json with ``type`` present but != l2 → python (future types)
    3. plugin.json present + python entry ``__init__.py`` → python
    4. plugin.json present + menu.json/seed.sql + no __init__.py → go
    5. Go-only executables present → go
    6. python entry __init__.py present → python
    otherwise unknown.
    """
    if not zip_path.exists() or not zipfile.is_zipfile(zip_path):
        return "unknown"

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

    manifest: dict[str, Any] = {}
    manifest_names = [n for n in names if n.rsplit("/", 1)[-1] == "plugin.json" and n.count("/") <= 1]
    if manifest_names:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                manifest = json.loads(zf.read(manifest_names[0]))
        except (json.JSONDecodeError, OSError, zipfile.BadZipFile):
            manifest = {}

    pkg_type = str(manifest.get("type", "")).strip().lower()
    if pkg_type == "l2":
        return "go"

    has_init = any(
        n.endswith("/__init__.py") or n == "__init__.py"
        for n in names
    )
    has_menu = any(n.rsplit("/", 1)[-1] in {"menu.json", "seed.sql"} for n in names)
    has_go_binaries = any(Path(n).suffix.lower() in _GO_ONLY_EXTS for n in names)

    if manifest_names:
        # A manifest exists: l2 already handled above. If it declares a
        # python entry or the python package structure, treat as python.
        declared_entry = str(manifest.get("entry", ""))
        if has_init or declared_entry:
            return "python"
        if has_menu and not has_init:
            return "go"
        # Manifest without type/entry/init — ambiguous, default python
        # (legacy python manifests had no ``type`` field).
        return "python"

    if has_go_binaries and not has_init:
        return "go"
    if has_init:
        return "python"
    if has_menu:
        return "go"
    return "unknown"


def detect_zip_upgrade_kind(zip_path: Path) -> str:
    """Classify a .zip archive as ``upgrade`` / ``plugin`` / ``unknown``.

    Deploy packages may be distributed as ZIP (ApeHub releases are ZIP-only),
    so the system-update endpoint accepts them. This mirrors
    ``detect_tar_gz_kind`` semantics: a top-level ``src/`` directory marks an
    upgrade package; plugin manifests / Go binaries mark mismatches.
    """
    if not zip_path.exists() or not zipfile.is_zipfile(zip_path):
        return "unknown"
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
    except (zipfile.BadZipFile, OSError):
        return "unknown"

    has_src = any(
        n == "src" or n.startswith("src/") or n.endswith("/src") or "/src/" in n
        for n in names
    )
    has_plugin_json = any(n.rsplit("/", 1)[-1] == "plugin.json" for n in names)
    has_go_binary = any(Path(n).suffix.lower() in _GO_ONLY_EXTS for n in names)

    if has_src:
        return "upgrade"
    if has_plugin_json:
        return "plugin"
    if has_go_binary:
        return "go-binary"
    return "unknown"


def detect_tar_gz_kind(tar_path: Path) -> str:
    """Classify a .tar.gz archive as ``upgrade`` / ``plugin`` / ``unknown``.

    The python base's upgrade package must contain a top-level ``src/``
    directory (system.py validates this).  A plugin package (built for
    python base) or an l2 manifest archive is NOT an upgrade package.
    """
    if not tar_path.exists():
        return "unknown"
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            names = tar.getnames()
    except (tarfile.TarError, OSError):
        return "unknown"

    base_names = [n.split("/", 1)[0] for n in names if n]
    top = set(base_names)

    has_src = any(
        n == "src" or n.startswith("src/") or n.endswith("/src") or "/src/" in n or n.split("/", 1)[-1].startswith("src/")
        for n in names
    )
    # plugin.json anywhere suggests a plugin package, not an upgrade package.
    has_plugin_json = any(n.rsplit("/", 1)[-1] == "plugin.json" for n in names)
    # ApeAdmin-Gin style "deploy" tarballs (if any) would carry a binary.
    has_go_binary = any(Path(n).suffix.lower() in _GO_ONLY_EXTS for n in names)

    if has_src:
        return "upgrade"
    if has_plugin_json:
        return "plugin"
    if has_go_binary:
        return "go-binary"
    # Directory-only check: some archives nest everything one level deep.
    if len(top) == 1 and top != {""}:
        inner = [n.split("/", 1)[1] for n in names if "/" in n]
        if any(i == "src" or i.startswith("src/") for i in inner):
            return "upgrade"
        if any(i.rsplit("/", 1)[-1] == "plugin.json" for i in inner):
            return "plugin"
    return "unknown"


def mismatch_message(kind: str, context: str) -> str | None:
    """Return a friendly, actionable message for a detected mismatch.

    ``context`` is either ``plugin-upload`` or ``system-update``.
    """
    if context == "plugin-upload":
        if kind == "go":
            return (
                "检测到这是 Go 版（ApeAdmin-Gin）L2 声明式插件包（plugin.json 声明了 type=l2"
                "，含 menu.json/seed.sql），无法安装在 Python 版底座上。"
                "请到 ApeAdmin-Gin 管理后台导入该插件。"
            )
        if kind == "unknown":
            return None  # Let the normal validation produce its specific error.
        return None
    if context == "system-update":
        if kind == "plugin":
            return (
                "检测到这是插件包（含 plugin.json），不是底座升级包。"
                "升级包应为 .tar.gz 且顶层目录包含 src/（由 build_deploy_package.sh 生成）。"
                "如需安装插件，请到「插件管理 → 导入插件」上传 .zip 插件包。"
            )
        if kind == "go-binary":
            return (
                "检测到这是 Go 版部署包（含可执行二进制），Python 版底座无法使用。"
                "请使用 build_deploy_package.sh 打包的 Python 版升级包。"
            )
        if kind == "unknown":
            return (
                "部署包结构不正确：缺少 src/ 目录，无法执行升级。"
            )
    return None
