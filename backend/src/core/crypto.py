"""API key encryption/decryption using Fernet symmetric encryption.

Uses a key derived from JWT_SECRET for deterministic encryption.
"""

import base64
import hashlib

from cryptography.fernet import Fernet

from src.core.config import settings


def _derive_key() -> bytes:
    """Derive a 32-byte Fernet key from JWT_SECRET using SHA-256."""
    digest = hashlib.sha256(settings.JWT_SECRET.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_derive_key())


def encrypt_api_key(plaintext: str) -> str:
    """Encrypt an API key and return the ciphertext string."""
    return _fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_api_key(ciphertext: str) -> str:
    """Decrypt an encrypted API key back to plaintext."""
    return _fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")


def mask_api_key(plaintext: str) -> str:
    """Return a masked version for display: sk-****last4."""
    if len(plaintext) <= 8:
        return "****"
    return plaintext[:3] + "****" + plaintext[-4:]
