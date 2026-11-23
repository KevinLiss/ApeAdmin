"""Optional Redis infrastructure with in-memory fallback.

ApeAdmin's runtime state splits into two kinds:

- **Cross-request data** (brute-force counters, MCP tickets, token
  blacklist cache): can live in Redis so multi-worker deployments stay
  correct and DB round-trips are avoided on hot paths.
- **Connection-bound state** (SSE session queues, per-session chat
  worker tasks): bound to the process holding the connection — Redis
  does not help these.

This module provides a thin, best-effort Redis client:

- ``REDIS_ENABLED=false`` (default ``true`` when a URL is configured)
  skips Redis entirely.
- Connection failures degrade to the in-memory fallback transparently:
  callers keep using the same API and the fallback behaves identically
  to the pre-Redis implementation. A warning is logged once per
  failure burst to avoid log spam.
- All keys are namespaced under ``apeadmin:`` so multiple deployments
  can share one Redis database.

Usage:

    from src.core.redis_client import kv

    await kv.set("tickets", token, payload_json, ttl=30)
    value = await kv.get("tickets", token)
    await kv.delete("tickets", token)
"""

import asyncio
import time
from typing import Any

from loguru import logger

from src.core.config import settings

KEY_PREFIX = "apeadmin"

# ---------------------------------------------------------------------------
# Connection lifecycle (lazy: Redis is only touched when first used)
# ---------------------------------------------------------------------------

_client: Any = None  # redis.asyncio.Redis when connected
_connect_attempted = False
_degraded = False  # True once we fell back to memory (log once)
_last_recheck = 0.0
_RECHECK_INTERVAL = 30.0  # seconds between reconnect attempts while degraded
_lock = asyncio.Lock()


class RedisUnavailable(RuntimeError):
    """Raised internally when Redis is disabled/unreachable."""


def _enabled() -> bool:
    """Redis is on unless explicitly disabled or no URL is configured."""
    if not settings.REDIS_ENABLED:
        return False
    return bool(settings.REDIS_URL)


async def _get_client() -> Any:
    """Return a connected Redis client, attempting (re)connection lazily."""
    global _client, _connect_attempted, _degraded, _last_recheck

    if not _enabled():
        raise RedisUnavailable("Redis disabled")

    if _client is not None:
        return _client

    now = time.monotonic()
    if _degraded and now - _last_recheck < _RECHECK_INTERVAL:
        # Recently failed; do not hammer a dead Redis on every call.
        raise RedisUnavailable("Redis degraded (recent failure)")

    async with _lock:
        # Double-check under lock (another coroutine may have connected).
        if _client is not None:
            return _client
        if _degraded and time.monotonic() - _last_recheck < _RECHECK_INTERVAL:
            raise RedisUnavailable("Redis degraded (recent failure)")

        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.5,
                socket_timeout=1.5,
                health_check_interval=30,
            )
            await client.ping()
            _client = client
            _connect_attempted = True
            if _degraded:
                logger.info("Redis reconnected — leaving in-memory fallback mode")
            _degraded = False
            logger.info(f"Redis connected: {settings.REDIS_URL}")
            return _client
        except Exception as exc:
            _degraded = True
            _last_recheck = time.monotonic()
            if not _connect_attempted:
                # First failure: explain the fallback once, loudly.
                logger.warning(
                    f"Redis unavailable ({exc.__class__.__name__}: {exc}) — "
                    "falling back to in-memory state. Multi-worker deployments "
                    "will lose cross-worker consistency for brute-force "
                    "guards/tickets until Redis is reachable."
                )
                _connect_attempted = True
            raise RedisUnavailable("Redis unreachable") from exc


def reset_for_tests() -> None:
    """Close the client and forget the degradation state (tests only)."""
    global _client, _connect_attempted, _degraded
    _client = None
    _connect_attempted = False
    _degraded = False


def is_degraded() -> bool:
    """True when Redis is configured but currently unreachable."""
    return _degraded


# ---------------------------------------------------------------------------
# kv API: namespaced get/set/delete used by auth_guard / tickets / blacklist
# ---------------------------------------------------------------------------

def _key(space: str, key: str) -> str:
    return f"{KEY_PREFIX}:{space}:{key}"


async def kv_set(space: str, key: str, value: str, ttl: int | None = None) -> bool:
    """Store a string value; returns True when served by Redis.

    False means the in-memory fallback handled it (or Redis is disabled).
    """
    try:
        client = await _get_client()
    except RedisUnavailable:
        _memory_set(space, key, value, ttl)
        return False
    try:
        if ttl:
            await client.set(_key(space, key), value, ex=ttl)
        else:
            await client.set(_key(space, key), value)
        return True
    except Exception as exc:
        logger.warning(f"Redis kv_set failed ({exc.__class__.__name__}) — using memory fallback")
        _memory_set(space, key, value, ttl)
        return False


async def kv_get(space: str, key: str) -> str | None:
    """Fetch a value; None when missing (memory fallback reads its own writes)."""
    try:
        client = await _get_client()
    except RedisUnavailable:
        return _memory_get(space, key)
    try:
        return await client.get(_key(space, key))
    except Exception as exc:
        logger.warning(f"Redis kv_get failed ({exc.__class__.__name__}) — trying memory fallback")
        return _memory_get(space, key)


async def kv_delete(space: str, key: str) -> bool:
    """Remove a key from Redis (and the memory fallback mirror)."""
    _memory_delete(space, key)
    try:
        client = await _get_client()
    except RedisUnavailable:
        return False
    try:
        await client.delete(_key(space, key))
        return True
    except Exception as exc:
        logger.warning(f"Redis kv_delete failed ({exc.__class__.__name__})")
        return False


# ---------------------------------------------------------------------------
# In-memory fallback mirrors (same shape as the pre-Redis dicts)
# ---------------------------------------------------------------------------

_memory: dict[str, dict[str, tuple[str, float | None]]] = {}


def _memory_set(space: str, key: str, value: str, ttl: int | None) -> None:
    store = _memory.setdefault(space, {})
    store[key] = (value, (time.time() + ttl) if ttl else None)


def _memory_get(space: str, key: str) -> str | None:
    entry = _memory.get(space, {}).get(key)
    if not entry:
        return None
    value, expires_at = entry
    if expires_at is not None and expires_at < time.time():
        _memory.get(space, {}).pop(key, None)
        return None
    return value


def _memory_delete(space: str, key: str) -> None:
    _memory.get(space, {}).pop(key, None)


def memory_clear(space: str | None = None) -> None:
    """Clear fallback state (tests / admin diagnostics)."""
    if space is None:
        _memory.clear()
    else:
        _memory.pop(space, None)
