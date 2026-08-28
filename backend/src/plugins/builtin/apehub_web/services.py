"""ApeHub business services: LemPay payment, email verification, helpers.

Config source: ``apehub_web_site_config`` table (managed in ApeAdmin admin UI).
"""

import hashlib
import hmac
import random
import re
import secrets
import smtplib
import ssl
import time
from decimal import Decimal, ROUND_HALF_UP
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from typing import Any
from urllib.parse import urlencode

import httpx

from src.core.config import settings

# ---------------------------------------------------------------------------
# Email verification helpers
# ---------------------------------------------------------------------------

CODE_TTL = 300  # 5 minutes
RESEND_INTERVAL = 60  # 60 seconds
MAX_CODE_ATTEMPTS = 5


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email or ""))


def generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(6))


def hash_verification_code(email: str, code: str) -> str:
    """Return a keyed digest so email codes are never persisted in plaintext."""
    payload = f"register:{email.strip().lower()}:{code.strip()}".encode("utf-8")
    return hmac.new(settings.JWT_SECRET.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def verification_code_matches(email: str, code: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_verification_code(email, code), expected_hash)


def _send_smtp(cfg: dict[str, Any], to_addr: str, subject: str, body: str) -> None:
    """Send an email via SMTP using config credentials."""
    mail_user = cfg.get("mail_user") or ""
    mail_code = cfg.get("mail_code") or ""
    mail_host = cfg.get("mail_host") or "smtp.qq.com"
    mail_port = int(cfg.get("mail_port") or 465)
    if not mail_user or not mail_code:
        raise RuntimeError("邮件服务未配置")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header("ApeHub", "utf-8")), mail_user))
    msg["To"] = to_addr
    msg["Date"] = formatdate(localtime=True)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(mail_host, mail_port, timeout=15, context=ctx) as server:
        server.login(mail_user, mail_code)
        server.sendmail(mail_user, [to_addr], msg.as_string())


def send_registration_code(cfg: dict[str, Any], email: str, code: str) -> None:
    """Send a previously persisted registration code through configured SMTP."""
    subject = "ApeHub 验证码"
    body = (
        "亲爱的用户：\n\n"
        f"您正在使用 ApeHub 服务，本次验证码为：{code}\n\n"
        f"验证码 {CODE_TTL // 60} 分钟内有效，请勿泄露给他人。\n"
        "如非本人操作，请忽略本邮件。\n\n"
        "—— ApeHub 团队"
    )
    _send_smtp(cfg, email, subject, body)


# ---------------------------------------------------------------------------
# LemPay payment
# ---------------------------------------------------------------------------

def lempay_md5_sign(params: dict[str, Any], key: str) -> str:
    """LemPay MD5 signature using its documented ASCII ordering contract."""
    if not key:
        raise RuntimeError("支付密钥未配置")
    sorted_keys = sorted(params.keys())
    raw = "&".join(
        f"{k}={params[k]}"
        for k in sorted_keys
        if k not in ("sign", "sign_type") and str(params[k]) not in ("", "0")
    )
    raw = f"{raw}{key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def lempay_verify_notify(params: dict[str, Any], key: str) -> bool:
    """Verify LemPay async notify signature."""
    sign = params.get("sign", "")
    payload = {k: v for k, v in params.items() if k not in ("sign", "sign_type")}
    return lempay_md5_sign(payload, key) == sign.lower()


# Compatibility for callers from the first marketplace implementation.
lepay_verify_notify = lempay_verify_notify


def build_lepay_submit_url(cfg: dict[str, Any], params: dict[str, Any]) -> str:
    """Build the LemPay redirect payment URL with signature."""
    base = cfg.get("lempay_submit_url") or ""
    if not base:
        raise RuntimeError("支付提交地址未配置")
    payload = {**params, "pid": cfg.get("lempay_pid")}
    payload["sign"] = lempay_md5_sign(payload, cfg.get("lempay_key") or "")
    payload["sign_type"] = "MD5"
    query = urlencode(payload)
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{query}"


async def request_lepay_refund(
    cfg: dict[str, Any], *, trade_no: str, out_trade_no: str, money: Decimal
) -> dict[str, Any]:
    """Submit a full refund through LemPay's merchant API."""
    base = str(cfg.get("lempay_api_url") or "").strip()
    if not base:
        raise RuntimeError("支付 API 地址未配置")
    separator = "&" if "?" in base else "?"
    url = base if "act=refund" in base else f"{base}{separator}act=refund"
    payload: dict[str, Any] = {
        "pid": cfg.get("lempay_pid"),
        "trade_no": trade_no,
        "out_trade_no": out_trade_no,
        "money": format(money.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f"),
    }
    payload["sign"] = lempay_md5_sign(payload, str(cfg.get("lempay_key") or ""))
    payload["sign_type"] = "MD5"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, data=payload)
    response.raise_for_status()
    result = response.json()
    if int(result.get("code") or 0) != 1:
        raise RuntimeError(str(result.get("msg") or "支付平台退款失败"))
    return result


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------

def gen_order_no() -> str:
    return f"AH{int(time.time() * 1000)}{random.randint(1000, 9999)}"


def gen_slug(text: str) -> str:
    """Generate a URL slug from a name (Chinese-friendly fallback)."""
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]", "-", text.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or f"item-{int(time.time())}"


def calc_split(amount: Decimal, service_fee_rate: Decimal) -> tuple[Decimal, Decimal]:
    """Return (developer_income, service_fee) for a paid order."""
    quantum = Decimal("0.00000001")
    fee = (amount * service_fee_rate / Decimal("100")).quantize(quantum, rounding=ROUND_HALF_UP)
    return (amount - fee).quantize(quantum, rounding=ROUND_HALF_UP), fee


def calc_withdrawal_fee(amount: Decimal, fee_type: str, fee_value: Decimal) -> Decimal:
    quantum = Decimal("0.00000001")
    if fee_type == "percent":
        fee = amount * fee_value / Decimal("100")
    else:
        fee = fee_value
    return min(amount, max(Decimal("0"), fee)).quantize(quantum, rounding=ROUND_HALF_UP)
