"""In-process brute-force protection for the login endpoint.

Tracks failed login attempts per (username, IP) and locks the pair out
for a cooldown window after too many consecutive failures. State lives
in process memory on purpose:

- The lock window is short (minutes); surviving a process restart is
  not a requirement — an attacker regains attempts after a restart but
  the operator also regains a healthy system.
- The admin panel is a single-worker deployment (systemd unit runs
  uvicorn with --workers 1); multi-worker deployments would need a
  shared store (Redis). Guarded by a warning in ``check_lock`` docs.

Success resets the counter for the pair. Successful logins for other
users from the same IP are unaffected.
"""

import time
from dataclasses import dataclass

from loguru import logger

from src.core.config import settings

MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60

# (username.lower(), ip) -> [fail_count, locked_until_epoch]
_attempts: dict[tuple[str, str], list[float]] = {}

# Periodic sweep bookkeeping
_LAST_SWEEP = 0.0


@dataclass
class LockState:
    locked: bool
    retry_after: int  # seconds until unlock (0 when not locked)


def check_lock(username: str, ip: str) -> LockState:
    """Raise-free lock check; returns whether the pair is currently locked."""
    _sweep()
    key = (username.lower(), ip or "unknown")
    entry = _attempts.get(key)
    if not entry:
        return LockState(locked=False, retry_after=0)
    locked_until = entry[1]
    if locked_until and locked_until > time.time():
        return LockState(locked=True, retry_after=int(locked_until - time.time()) + 1)
    return LockState(locked=False, retry_after=0)


def record_failure(username: str, ip: str) -> LockState:
    """Register a failed attempt; locks the pair at MAX_FAILURES."""
    key = (username.lower(), ip or "unknown")
    entry = _attempts.setdefault(key, [0, 0.0])
    entry[0] += 1
    if entry[0] >= MAX_FAILURES:
        entry[1] = time.time() + LOCK_SECONDS
        entry[0] = 0
        logger.warning(
            f"Login lockout engaged: user={username!r} ip={ip} "
            f"for {LOCK_SECONDS}s"
        )
        return LockState(locked=True, retry_after=LOCK_SECONDS)
    return LockState(locked=False, retry_after=0)


def record_success(username: str, ip: str) -> None:
    """A successful login clears the pair's failure counter."""
    _attempts.pop((username.lower(), ip or "unknown"), None)


def _sweep() -> None:
    """Drop stale entries (expired locks / idle counters) opportunistically."""
    global _LAST_SWEEP
    now = time.time()
    if now - _LAST_SWEEP < 60:
        return
    _LAST_SWEEP = now
    stale = [
        k
        for k, (count, locked_until) in _attempts.items()
        if (locked_until and locked_until < now)
        or (not locked_until and count == 0)
    ]
    for k in stale:
        _attempts.pop(k, None)


# ---------------------------------------------------------------- i18n keys
# The login route formats the user-visible message:
#   t("auth.too_many_attempts", locale, minutes=N)
# Keys (added in src/core/i18n.py):
#   zh-CN: "登录失败次数过多，账号已临时锁定，请 {minutes} 分钟后重试"
#   en-US: "Too many failed attempts, account temporarily locked, retry in {minutes} minutes"
