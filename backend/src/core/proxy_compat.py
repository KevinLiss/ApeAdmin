"""Normalize malformed proxy environment variables at import time.

Why this exists
---------------
Some local dev machines run Clash-style proxies that write system proxy
env vars in a *non-standard* IPv6 form::

    http_proxy=http://::1:7890        # bare IPv6, no brackets
    all_proxy=socks5://::1:7890

The legal URL form requires brackets around IPv6 hosts::

    http://[::1]:7890

httpx (and any RFC-3986 parser) fails outright on the bare form with
``Invalid port: ':1:7890'`` — which used to break *every* outbound HTTP
call in this project on such machines (AI chat, provider connectivity
test, update check, payment callbacks …) even though the user's own
service config was perfectly fine.

What this module does
---------------------
1. At import time (cheap, once), scan the well-known proxy env vars.
2. If a value looks like ``scheme://<bare-ipv6-host>:port``, rewrite it
   to the bracketed legal form **in os.environ** so every subsequent
   httpx/requests client — including plugin code and third-party
   libraries — sees a parseable value.
3. Vars that are already legal, or absent, are left untouched.
4. ``trust_env`` decisions stay with each call site: machines with
   valid proxies keep working (traffic still flows through them);
   machines with no proxy env are unaffected.

Run ``python -m src.core.proxy_compat`` to self-test the normalizer.
"""

from __future__ import annotations

import os
import re
import sys

__all__ = ["normalize_proxy_env", "PROXY_ENV_KEYS"]

# All conventional proxy env var names (upper/lower handled via lookup).
PROXY_ENV_KEYS: tuple[str, ...] = (
    "HTTP_PROXY", "http_proxy",
    "HTTPS_PROXY", "https_proxy",
    "ALL_PROXY", "all_proxy",
)

# scheme://<bare-ipv6-host>[:port][/] — the malformed shape.
# The host group is non-greedy so the trailing numeric port peels off first
# ("::1:7890" → host "::1", port "7890"); the host part is then validated
# as hex-and-colons (at least two segments = IPv6-ish, not an IPv4/plain name).
_BARE_IPV6_RE = re.compile(
    r"^(?P<scheme>[a-z][a-z0-9+.-]*)://"
    r"(?P<host>.+?)"
    r"(?::(?P<port>\d+))?"
    r"/?$"
)
_IPV6_HOST_RE = re.compile(r"^(?:[0-9A-Fa-f]{0,4}:){1,7}[0-9A-Fa-f]{0,4}$")

_FIXED_LOG = "[proxy_compat] normalized %s: %r -> %r"


def _fix_value(raw: str) -> str | None:
    """Return the bracketed-IPv6 form of ``raw``, or None if already fine."""
    raw = raw.strip()
    if not raw or raw.startswith("proxy://"):  # empty / https_proxy helper-dummy
        return None
    m = _BARE_IPV6_RE.match(raw)
    if not m:
        return None
    host = m.group("host")
    # Only bare IPv6 hosts need bracketing; IPv4 / hostnames / anything
    # containing "[", "]", or non-hex-colon chars is already fine.
    if not _IPV6_HOST_RE.match(host) or host.count(":") < 2:
        return None
    port = f":{m.group('port')}" if m.group("port") else ""
    fixed = f"{m.group('scheme')}://[{host}]{port}"
    return fixed if fixed != raw else None


def normalize_proxy_env(env: dict[str, str] | None = None) -> list[tuple[str, str, str]]:
    """Normalize proxy env vars in ``os.environ`` (in place).

    Pass a custom ``env`` dict for testing. Returns the list of fixed
    ``(key, old, new)`` tuples (empty when nothing needed fixing).
    """
    target = os.environ if env is None else env
    fixed: list[tuple[str, str, str]] = []
    for key in PROXY_ENV_KEYS:
        raw = target.get(key)
        if raw is None:
            continue
        new = _fix_value(raw)
        if new is not None:
            target[key] = new
            fixed.append((key, raw, new))
    return fixed


def _self_test() -> int:
    """Offline self-test: malformed → bracketed, legal → untouched."""
    cases = {
        "http://::1:7890": "http://[::1]:7890",
        "http://::1:7890/": "http://[::1]:7890",
        "socks5://::1:7890": "socks5://[::1]:7890",
        "http://fe80::1:7890": "http://[fe80::1]:7890",
        # untouched (already legal / not IPv6 / empty-ish)
        "http://[::1]:7890": None,
        "http://127.0.0.1:7890": None,
        "socks5://127.0.0.1:7891": None,
        "http://10.0.0.5:7890": None,
        "http://proxy.lan.corp:8080": None,
        "": None,
    }
    failures = 0
    for raw, want in cases.items():
        got = _fix_value(raw)
        if got != want:
            print(f"  FAIL {raw!r}: got {got!r}, want {want!r}")
            failures += 1
    print(f"proxy_compat self-test: {len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


# Normalize once at import. Cheap (pure regex over ≤6 env vars) and it must
# happen before ANY httpx client is constructed anywhere in the process.
_fixed = normalize_proxy_env()
if _fixed and "pytest" not in sys.modules:  # stay quiet under tests
    import logging

    for key, old, new in _fixed:
        logging.getLogger(__name__).info(_FIXED_LOG, key, old, new)
