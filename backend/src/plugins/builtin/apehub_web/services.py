"""ApeHub business services: LemPay payment, email verification, helpers.

Config source: ``apehub_web_site_config`` table (managed in ApeAdmin admin UI).
"""

import hashlib
import hmac
import re
import secrets
import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from typing import Any

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
    """LemPay MD5 signature: sort keys, concat k=v&..., append &key=KEY."""
    if not key:
        raise RuntimeError("支付密钥未配置")
    sorted_keys = sorted(params.keys())
    raw = "&".join(f"{k}={params[k]}" for k in sorted_keys if params[k] != "")
    raw = f"{raw}&key={key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def lepay_verify_notify(params: dict[str, Any], key: str) -> bool:
    """Verify LemPay async notify signature."""
    sign = params.get("sign", "")
    payload = {k: v for k, v in params.items() if k not in ("sign", "sign_type")}
    return lempay_md5_sign(payload, key) == sign.lower()


def build_lepay_submit_url(cfg: dict[str, Any], params: dict[str, Any]) -> str:
    """Build the LemPay redirect payment URL with signature."""
    base = cfg.get("lempay_submit_url") or ""
    if not base:
        raise RuntimeError("支付提交地址未配置")
    params["pid"] = cfg.get("lempay_pid")
    params["sign"] = lempay_md5_sign(params, cfg.get("lempay_key") or "")
    params["sign_type"] = "MD5"
    query = "&".join(f"{k}={v}" for k, v in params.items())
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{query}"


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


def calc_split(amount: float, service_fee_rate: float) -> tuple[float, float]:
    """Return (developer_income, service_fee) for a paid order."""
    fee = round(amount * service_fee_rate / 100.0, 2)
    return round(amount - fee, 2), fee
