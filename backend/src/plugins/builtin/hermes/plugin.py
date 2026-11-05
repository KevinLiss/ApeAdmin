"""Hermes AI 助手插件。

将 hermes-agent（Nous Research 的自进化 AI 代理）融入 ApeAdmin。

架构形态：**瘦客户端插件 + hermes 独立进程**。
- ApeAdmin 插件机制不允许声明 pip 依赖，hermes 依赖树庞大（约 259 个包），
  因此 hermes 本体必须作为独立进程运行（本机已验证 v0.21.4 可跑）。
- 插件通过 tui_gateway 的 WebSocket JSON-RPC 协议（hermes 官方 Web UI 同款
  桥接路径）与 hermes 进程通信，实现流式对话、会话管理。
- 插件进程由本插件托管：启用时启动（hermes dashboard --skip-build）、
  禁用/卸载时在 unregister()/on_unload() 中终止，不遗留孤儿进程。
"""

import asyncio
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from loguru import logger

from src.plugins import PluginInterface
from src.core.config import settings

# hermes 安装根目录（默认取 ApeAdmin 仓库工作区下的 hermesagent/hermes-agent）
# 目录结构：workspace/apeadmin/backend/src/plugins/builtin/hermes/plugin.py
# parents[6] = workspace（共 7 层上溯），hermes 在其兄弟目录 hermesagent/hermes-agent
DEFAULT_HERMES_DIR = str(
    Path(__file__).resolve().parents[6] / "hermesagent" / "hermes-agent"
)
HERMES_ENV_VAR = "APEADMIN_HERMES_DIR"


class HermesPlugin(PluginInterface):
    """Hermes AI 助手插件——托管 hermes 独立进程并提供 WS 桥接。"""

    name = "hermes"
    display_name = "Hermes AI 助手"
    description = "自进化 AI 代理（hermes-agent）——流式对话、技能、记忆、自动化，融入 ApeAdmin 管理后台"
    version = "0.1.0"
    author = "ApeAdmin"

    # ── 运行时状态（进程句柄必须挂在 app.state 防 GC）────
    _process: subprocess.Popen | None = None
    _proc_lock: asyncio.Lock | None = None

    # ── 生命周期：内存加载 ─────────────────────────────
    def on_load(self) -> None:
        logger.info("[Hermes] loaded into memory")

    # ── 生命周期：安装（建表 + seed）────────────────────
    async def install(self) -> None:
        # 本插件无自有数据表；菜单与权限在 seed.py 注册
        from src.plugins.builtin.hermes.seed import seed_hermes_menus
        from src.db import SessionLocal

        async with SessionLocal() as db:
            await seed_hermes_menus(db)
            await db.commit()
        logger.info("[hermes] installed — menus seeded")

    # ── 生命周期：卸载（清理）────────────────────────
    async def uninstall(self) -> None:
        from sqlalchemy import delete
        from src.db import SessionLocal
        from src.models import Menu

        async with SessionLocal() as db:
            await db.execute(delete(Menu).where(Menu.permission.like("hermes:%")))
            await db.execute(delete(Menu).where(Menu.path == "/hermes"))
            await db.commit()
        logger.info("[hermes] uninstalled — menus removed")

    # ── 生命周期：注册路由 + 事件 ───────────────────────
    def register(self, app: FastAPI) -> None:
        """挂载 REST API + WS 代理路由，并启动 hermes 子进程。

        .. note::
           hermes 子进程在此启动（而非 install）——register 在应用启动时调用，
           此时事件循环可用；install 在首次启用时调用，可能早于事件循环。
        """
        from src.plugins.builtin.hermes.api import router as api_router
        from src.plugins.builtin.hermes.ws_bridge import router as ws_router
        from src.plugins.builtin.hermes.proxy import router as proxy_router

        app.include_router(api_router, prefix=settings.API_PREFIX)
        app.include_router(ws_router, prefix=settings.API_PREFIX)
        app.include_router(proxy_router, prefix=settings.API_PREFIX)

        # 启动 hermes 子进程（独立进程，失败不阻塞底座启动）
        self._proc_lock = asyncio.Lock()
        self._spawn_hermes(app)

        logger.info("[hermes] registered — routes + WS bridge + child process")

    # ── 生命周期：卸载运行时资源 ───────────────────────
    def unregister(self, app: FastAPI) -> None:
        """禁用/卸载时终止 hermes 子进程。"""
        self._terminate_hermes()
        logger.info("[hermes] unregistered — child process terminated")

    # ── 生命周期：内存卸载 ─────────────────────────────
    def on_unload(self) -> None:
        self._terminate_hermes()
        logger.info("[hermes] unloaded from memory")

    # ─────────────────────────────────────────────────────
    # 子进程托管
    # ─────────────────────────────────────────────────────
    def _hermes_dir(self) -> Path:
        """定位 hermes-agent 根目录。"""
        env = os.environ.get(HERMES_ENV_VAR)
        if env and Path(env).exists():
            return Path(env)
        p = Path(DEFAULT_HERMES_DIR)
        return p if p.exists() else Path(".")

    def _spawn_hermes(self, app: FastAPI) -> None:
        """以分离式子进程启动 hermes dashboard（--skip-build 避免每次构建）。"""
        if self._process and self._process.poll() is None:
            return  # 已在运行

        hermes_dir = self._hermes_dir()
        python_bin = hermes_dir / ".venv" / "bin" / "python"
        if not python_bin.exists():
            logger.error(f"[hermes] 未找到 hermes venv: {python_bin}，跳过子进程启动")
            return

        # 固定 dashboard token，供 WS 桥接使用（跨重启稳定）
        env = os.environ.copy()
        env.setdefault("HERMES_DASHBOARD_SESSION_TOKEN", self._hermes_token())

        # 本机回环绑定 → 无需鉴权；但显式设置避免受外部环境变量影响
        env.setdefault("NO_PROXY", "*")

        # --no-open：hermes dashboard 默认会 webbrowser.open 弹出浏览器标签页，
        # 后端每次重启（含生产部署）都会骚扰管理员；插件场景应由用户主动访问。
        cmd = [str(python_bin), "-m", "hermes_cli.main", "dashboard", "--host", "127.0.0.1", "--port", "9119", "--skip-build", "--no-open"]

        try:
            # start_new_session=True → 独立进程组；父进程退出后子进程继续存活
            self._process = subprocess.Popen(
                cmd,
                cwd=str(hermes_dir),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            app.state.hermes_process = self._process  # 防 GC
            logger.info(f"[hermes] child process spawned pid={self._process.pid}")
        except Exception as exc:
            logger.error(f"[hermes] 子进程启动失败: {exc}")
            self._process = None

    def _terminate_hermes(self) -> None:
        proc = self._process
        if proc is None:
            return
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        except Exception as exc:
            logger.warning(f"[hermes] 终止子进程异常: {exc}")
        finally:
            self._process = None
        logger.info("[hermes] hermes child process terminated")

    def _hermes_token(self) -> str:
        """读取/生成固定 dashboard token。"""
        import secrets
        from src.core.config import settings as _s

        token = os.environ.get("HERMES_DASHBOARD_SESSION_TOKEN")
        if token:
            return token
        # 存到插件目录旁的 .hermes_token 文件，跨重启稳定
        token_file = Path(settings.PLUGINS_BUILTIN_DIR) / "hermes" / ".hermes_token"
        if token_file.exists():
            return token_file.read_text().strip()
        token = secrets.token_urlsafe(32)
        token_file.write_text(token)
        return token

    # ── 提供给 WS 桥接 / API 的状态与连接信息 ──────────
    def get_status(self) -> dict[str, Any]:
        """返回 hermes 子进程与桥接状态。"""
        alive = self._process is not None and self._process.poll() is None
        port = self._port()
        return {
            "running": alive,
            "pid": self._process.pid if alive else None,
            "port": port,
            "token": self._hermes_token() if alive else "",
        }

    def _port(self) -> int:
        return 9119

    def _wait_ready(self, timeout: float = 30.0) -> bool:
        """等待 hermes dashboard HTTP 端口就绪。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self._port()), timeout=1):
                    return True
            except OSError:
                time.sleep(0.5)
        return False


# 模块级单例（manager 通过 _find_plugin_class 实例化；此处保留引用便于状态查询）
_plugin_instance: "HermesPlugin | None" = None


def get_hermes_plugin() -> "HermesPlugin | None":
    """从插件管理器获取真实的 hermes 插件实例（保持子进程/token 状态一致）。

    优先取 plugin_manager 中已注册的实例；未注册时回退到本模块单例。
    """
    global _plugin_instance
    try:
        from src.plugins import plugin_manager

        info = plugin_manager.get_plugin("hermes")
        if info and info.instance is not None:
            return info.instance  # type: ignore[return-value]
    except Exception:
        pass
    if _plugin_instance is None:
        _plugin_instance = HermesPlugin()
    return _plugin_instance