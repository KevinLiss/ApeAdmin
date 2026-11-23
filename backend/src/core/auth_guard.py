"""Brute-force protection for the login endpoint.

Tracks failed login attempts per (username, IP) and locks the pair out
for a cooldown window after too many consecutive failures.

Storage:
- **Redis** (when reachable): counters live under ``apeadmin:authlock:``
  so multi-worker deployments share one view of the attempts. Lockout
  TTL is enforced by Redis itself.
- **In-memory fallback** (Redis disabled/unreachable): identical
  behavior to the historical implementation — counters in a process
  dict. Correct for the documented single-worker deployment; multi-worker
  deployments lose cross-worker consistency until Redis is reachable.

The lock window is short (minutes); surviving a process restart is not
a requirement — an attacker regains attempts after a restart but the
operator also regains a healthy system.

Success resets the counter for the pair. Successful logins for other
users from the same IP are unaffected.
"""

import time
from dataclasses import dataclass

from loguru import logger

from src.core.redis_client import kv_delete, kv_get, kv_set, memory_clear

MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60

_SPACE = "authlock"

# In-memory fallback: (username.lower(), ip) -> [fail_count, locked_until_epoch]
_attempts: dict[tuple[str, str], list[float]] = {}

# Periodic sweep bookkeeping (fallback mode only)
_LAST_SWEEP = 0.0


@dataclass
class LockState:
    locked: bool
    retry_after: int  # seconds until unlock (0 when not locked)


def _k(username: str, ip: str) -> str:
    return f"{username.lower()}:{ip or 'unknown'}"


async def check_lock(username: str, ip: str) -> LockState:
    """Raise-free lock check; returns whether the pair is currently locked."""
    _sweep()
    key = _k(username, ip)
    raw = await kv_get(_SPACE, key)
    if raw is None:
        # Fallback dict mirrors Redis misses; check it too so a degraded
        # session keeps serving counters written before the failure.
        entry = _attempts.get((username.lower(), ip or "unknown"))
        if not entry:
            return LockState(locked=False, retry_after=0)
        locked_until = entry[1]
    else:
        # "count|locked_until"
        try:
            count_s, locked_s = raw.split("|", 1)
            locked_until = float(locked_s) if locked_s else 0.0
        except ValueError:
            return LockState(locked=False, retry_after=0)
    if locked_until and locked_until > time.time():
        return LockState(locked=True, retry_after=int(locked_until - time.time()) + 1)
    return LockState(locked=False, retry_after=0)


async def record_failure(username: str, ip: str) -> LockState:
    """Register a failed attempt; locks the pair at MAX_FAILURES."""
    key = _k(username, ip)
    raw = await kv_get(_SPACE, key)
    if raw is not None:
        try:
            count_s, locked_s = raw.split("|", 1)
            count = int(count_s)
        except ValueError:
            count = 0
    else:
        # Seed from fallback dict (degraded-mode continuity), else zero.
        entry = _attempts.get((username.lower(), ip or "unknown"))
        count = int(entry[0]) if entry else 0

    count += 1
    if count >= MAX_FAILURES:
        locked_until = time.time() + LOCK_SECONDS
        await kv_set(_SPACE, key, f"0|{locked_until}", ttl=LOCK_SECONDS)
        logger.warning(
            f"Login lockout engaged: user={username!r} ip={ip} "
            f"for {LOCK_SECONDS}s"
        )
        return LockState(locked=True, retry_after=LOCK_SECONDS)

    await kv_set(_SPACE, key, f"{count}|", ttl=LOCK_SECONDS)
    return LockState(locked=False, retry_after=0)


async def record_success(username: str, ip: str) -> None:
    """A successful login clears the pair's failure counter."""
    await kv_delete(_SPACE, _k(username, ip))
    _attempts.pop((username.lower(), ip or "unknown"), None)


def _sweep() -> None:
    """Drop stale fallback entries (expired locks / idle counters)."""
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


def reset_fallback() -> None:
    """Clear in-memory fallback counters (tests / admin diagnostics)."""
    memory_clear(_SPACE)
    _attempts.clear()


# ---------------------------------------------------------------- i18n keys
# The login route formats the user-visible message:
#   t("auth.too_many_attempts", locale, minutes=N)
# Keys (added in src/core/i18n.py):
#   zh-CN: "登录失败次数过多，账号已临时锁定，请 {minutes} 分钟后重试"
#   en-US: "Too many failed attempts, account temporarily locked, retry in {minutes} minutes"
