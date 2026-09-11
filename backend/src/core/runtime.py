"""Cross-platform backend restart utilities.

Shared by:
- src.api.plugin.restart_server  (POST /plugins/restart)
- src.api.system.upload_update   (POST /system/update)

Design:
- POSIX (Linux/macOS):
    * systemd-managed: spawn a detached script running `systemctl restart apeadmin`
    * direct relaunch: spawn a detached script that waits for the old process
      to exit, then relaunches uvicorn on the SAME host/port the server is
      currently bound to (no hardcoded 8000).
- Windows:
    * systemd does not exist; skip detection entirely.
    * spawn a detached PowerShell script that waits for the old process to
      exit, then relaunches uvicorn via the same interpreter.
- Failure visibility: all script output goes to a log file under the OS temp
  dir instead of /dev/null, so a failed restart can be diagnosed.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from loguru import logger

IS_WINDOWS = sys.platform.startswith("win")

# Restart scripts + failure diagnostics all live under the OS temp dir.
RESTART_LOG = Path(
    os.environ.get("APEADMIN_RESTART_LOG")
    or str(Path(tempfile.gettempdir()) / "apeadmin_restart.log")
)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _uvicorn_bind_addr() -> tuple[str, int]:
    """Return the host/port this process is actually serving on.

    Order: explicit env override -> CLI argv (--host/--port) -> bound LISTEN
    socket (psutil) -> 127.0.0.1:8000 fallback.
    """
    host = os.environ.get("APEADMIN_BIND_HOST")
    port = os.environ.get("APEADMIN_BIND_PORT")
    if host and port:
        return host, int(port)

    # uvicorn CLI puts --host/--port into sys.argv; -m uvicorn keeps them too.
    argv = sys.argv
    try:
        for flag, current in (("--host", "host"), ("--port", "port")):
            if flag in argv:
                value = argv[argv.index(flag) + 1]
                if current == "host":
                    host = value
                else:
                    port = value
    except (IndexError, ValueError):
        pass

    # Ask the OS for our LISTEN sockets (covers programmatic uvicorn.run too).
    if not (host and port):
        try:
            import psutil

            for conn in psutil.Process(os.getpid()).net_connections(kind="tcp"):
                if conn.status == psutil.CONN_LISTEN and conn.laddr:
                    if host and port:
                        break
                    if port is None or not port:
                        port = str(conn.laddr.port)
                        if not host:
                            host = conn.laddr.ip if ":" not in conn.laddr.ip or conn.laddr.ip == "::" else "0.0.0.0"
                            if host in ("::", "0.0.0.0"):
                                host = conn.laddr.ip if conn.laddr.ip != "::" else "0.0.0.0"
                    elif not host:
                        host = conn.laddr.ip
        except Exception:
            pass

    # IPv6 wildcard binds as "::"; uvicorn accepts it verbatim.
    if host and port:
        return host, int(port)
    return "127.0.0.1", 8000


async def is_systemd_managed() -> bool:
    """True when a systemd unit named apeadmin manages this process."""
    if IS_WINDOWS:
        return False
    try:
        detect = await asyncio.create_subprocess_exec(
            "bash", "-c",
            "command -v systemctl >/dev/null 2>&1 "
            "&& systemctl list-unit-files 2>/dev/null | grep -q apeadmin "
            "&& echo systemd || echo direct",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await asyncio.wait_for(detect.communicate(), timeout=10)
    except (FileNotFoundError, asyncio.TimeoutError, OSError) as exc:
        # No bash / detection failed: assume direct relaunch mode.
        logger.warning(f"systemd detection unavailable, falling back to direct: {exc}")
        return False
    return out.decode().strip() == "systemd"


async def spawn_restart(
    project_root: Path,
    python_bin: str,
    wait_seconds: float = 2.0,
) -> dict:
    """Spawn a detached, OS-appropriate restart script and return metadata.

    The caller is expected to self-terminate shortly after (the response must
    reach the client first). The script:
      - waits ``wait_seconds`` so the old process can exit gracefully,
      - then either asks systemd to restart the service (POSIX, if managed)
        or relaunches uvicorn directly on the same bound address.
    """
    if IS_WINDOWS:
        mode = "windows"
    elif await is_systemd_managed():
        mode = "systemd"
    else:
        mode = "direct"

    if mode == "systemd":
        script = Path(tempfile.gettempdir()) / "apeadmin_systemd_restart.sh"
        script.write_text(
            "#!/bin/bash\n"
            "# ApeAdmin systemd-managed restart\n"
            f'exec >>"{RESTART_LOG}" 2>&1\n'
            f'echo "[{_timestamp()}] systemd restart begin"\n'
            f"sleep {wait_seconds}\n"
            "systemctl restart apeadmin\n"
            "rc=$?\n"
            f'echo "[{_timestamp()}] systemctl exit $rc"\n'
        )
        _chmod_exec(script)
        proc = await _spawn_detached("bash", str(script))
        return {"mode": mode, "script": str(script), "log": str(RESTART_LOG), "spawner_pid": proc.pid}

    if mode == "direct":
        host, port = _uvicorn_bind_addr()
        script = Path(tempfile.gettempdir()) / "apeadmin_restart.sh"
        script.write_text(
            "#!/bin/bash\n"
            "# ApeAdmin auto-restart script (POSIX, no systemd)\n"
            f'exec >>"{RESTART_LOG}" 2>&1\n'
            f'echo "[{_timestamp()}] direct restart begin (host={host} port={port})"\n'
            f"sleep {wait_seconds}\n"
            f'cd "{project_root}"\n'
            f'exec "{python_bin}" -m uvicorn src.main:app --host {host} --port {port} </dev/null\n'
        )
        _chmod_exec(script)
        proc = await _spawn_detached("bash", str(script))
        return {
            "mode": mode, "script": str(script), "log": str(RESTART_LOG),
            "host": host, "port": port, "spawner_pid": proc.pid,
        }

    # ---- Windows: PowerShell relaunch ----
    host, port = _uvicorn_bind_addr()
    script = Path(tempfile.gettempdir()) / "apeadmin_restart.ps1"
    script.write_text(
        "# ApeAdmin auto-restart script (Windows)\n"
        f"Start-Transcript -Path '{RESTART_LOG}' -Append\n"
        f"Start-Sleep -Seconds {int(wait_seconds)}\n"
        f"Set-Location '{project_root}'\n"
        f"& '{python_bin}' -m uvicorn src.main:app --host {host} --port {port}\n",
        encoding="utf-8-sig",
    )
    proc = await _spawn_detached(
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", str(script),
    )
    return {
        "mode": mode, "script": str(script), "log": str(RESTART_LOG),
        "host": host, "port": port, "spawner_pid": proc.pid,
    }


def _chmod_exec(script: Path) -> None:
    """Make a POSIX script executable (no-op on Windows)."""
    if IS_WINDOWS:
        return
    import stat as _stat

    script.chmod(script.stat().st_mode | _stat.S_IEXEC | _stat.S_IXGRP | _stat.S_IXOTH)


async def _spawn_detached(*args: str) -> asyncio.subprocess.Process:
    """Spawn a fully detached subprocess; raise a readable error on failure."""
    try:
        return await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            start_new_session=not IS_WINDOWS,
            creationflags=_creation_flags(),
        )
    except FileNotFoundError as exc:
        logger.error(f"Restart spawner not found: {args[0]} ({exc})")
        raise RuntimeError(
            f"无法启动重启脚本执行器 {args[0]}：{exc}。请手动重启后端服务。"
        ) from exc
    except Exception as exc:
        logger.error(f"Failed to spawn restart script: {exc}")
        raise RuntimeError(f"启动重启脚本失败：{exc}") from exc


def _creation_flags() -> int:
    """Windows DETACHED_PROCESS flag so the child survives the parent."""
    if not IS_WINDOWS:
        return 0
    DETACHED_PROCESS = 0x00000008
    return DETACHED_PROCESS
