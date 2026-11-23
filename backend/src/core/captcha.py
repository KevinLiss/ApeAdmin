"""Stateless arithmetic captcha for the login endpoint.

Design goals:
- **No server-side storage** — the answer and expiry are encoded into the
  ``captcha_id`` and protected by an HMAC signature (reuse ``JWT_SECRET``),
  so it is safe with multiple workers and survives restarts.
- **Short TTL** — 5 minutes, single-use semantics enforced by the login
  flow (the answer is bound to one successful submit; a replay within TTL
  is acceptable only while the same question remains unanswered — see
  README security notes).
- **Cheap** — a math question rendered as plain text; the admin frontend
  displays it alongside the existing slider (UX gate) when enabled.

Enable/disable is driven by the ``login_captcha_enabled`` sys_setting row
(admin UI → 系统设置), default **off** so existing deployments keep their
current login behaviour until an operator opts in.
"""

import hashlib
import hmac
import secrets
import time

from src.core.config import settings

_TTL_SECONDS = 300


def _sign(payload: str) -> str:
    """HMAC-SHA256 truncated signature over "expire|answer"."""
    key = settings.JWT_SECRET.encode()
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()[:32]


def generate() -> dict:
    """Create a signed arithmetic question.

    Returns ``{"captcha_id", "question", "expires_in"}``.
    """
    a = secrets.randbelow(20) + 1
    b = secrets.randbelow(20) + 1
    if secrets.randbelow(2):
        question = f"{a} + {b} = ?"
        answer = a + b
    else:
        hi, lo = max(a, b), min(a, b)
        question = f"{hi} − {lo} = ?"
        answer = hi - lo
    expire = int(time.time()) + _TTL_SECONDS
    payload = f"{expire}|{answer}"
    return {
        "captcha_id": f"{payload}.{_sign(payload)}",
        "question": question,
        "expires_in": _TTL_SECONDS,
    }


def verify(captcha_id: str | None, code: str | None) -> bool:
    """Validate a submitted answer against its signed id."""
    if not captcha_id or not code:
        return False
    try:
        payload, sig = captcha_id.rsplit(".", 1)
        if not hmac.compare_digest(sig, _sign(payload)):
            return False
        expire_s, answer_s = payload.split("|", 1)
        if int(time.time()) > int(expire_s):
            return False
        # Normalize: accept "12", " 12 " but reject "1 2".
        submitted = code.strip()
        return submitted.isdigit() and int(submitted) == int(answer_s)
    except (ValueError, AttributeError):
        return False
