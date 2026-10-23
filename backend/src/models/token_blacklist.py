"""JWT token blacklist: logout actually invalidates the token server-side.

JWTs are stateless by design; without this table a "logged out" token
kept working until natural expiry (24h for access, 7d for refresh).
Each issued token carries a ``jti``; logout records it here and the
auth dependency rejects any request whose ``jti`` is blacklisted.

Tokens issued before this feature (no ``jti``) cannot be pinpoint-
revoked; they age out naturally within their original expiry. New
logins always produce revocable tokens.

Rows are self-cleaning: expired entries are deleted opportunistically
on write, so the table stays small in normal operation.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.mixins import IDMixin
from src.models.rbac import Base


class TokenBlacklist(IDMixin, Base):
    """Revoked token identifiers (one row per logged-out token)."""

    __tablename__ = "sys_token_blacklist"

    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, comment="JWT ID")
    user_id: Mapped[int] = mapped_column(comment="关联用户，便于审计")
    token_type: Mapped[str] = mapped_column(String(10), default="access", comment="access/refresh")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), comment="原 token 过期时间，到期后条目可清理"
    )

    @classmethod
    def expired_cutoff(cls) -> datetime:
        return datetime.now(timezone.utc)


Index("ix_sys_token_blacklist_user", TokenBlacklist.user_id)
