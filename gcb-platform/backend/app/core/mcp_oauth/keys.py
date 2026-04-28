"""RS256 signing key management for the MCP Authorization Server.

Keys are stored in the ``oauth_signing_keys`` table; private halves are
AES-GCM encrypted at rest with a KEK loaded from
``OAUTH_KEY_ENCRYPTION_KEY``. The public JWK is stored as JSON for
direct serialisation at ``/.well-known/jwks.json``.

Rotation runbook
----------------
1. Generate a new key with ``ensure_signing_key()`` (called at startup).
2. To rotate manually, call :func:`rotate_signing_key` — it inserts a
   new ``is_current=True`` row, demotes the prior current key with a
   24-hour ``not_after`` overlap, and returns the new private key.
3. The old key keeps verifying in-flight tokens during the overlap; the
   JWKS endpoint serves both keys until ``not_after`` expires.
4. Rotating ``OAUTH_KEY_ENCRYPTION_KEY`` itself requires re-encrypting
   every row with the new KEK before retiring the old one — that is a
   separate, manual operation; do it in a maintenance window.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy.orm import Session

from app.core.mcp_oauth.config import get_oauth_settings
from app.core.mcp_oauth.models import OAuthSigningKey

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SigningKey:
    """Decrypted signing key materialised in memory for token issuance/verify."""

    kid: str
    private_pem: bytes
    public_jwk: dict


# In-process cache of decrypted keys, indexed by ``kid``. Refreshed by
# :func:`reload_keys`. The cache survives the lifetime of the process.
_KEY_CACHE: dict[str, SigningKey] = {}
_CURRENT_KID: Optional[str] = None


# ---------------------------------------------------------------------------
# KEK helpers
# ---------------------------------------------------------------------------


def _load_kek() -> bytes:
    raw = get_oauth_settings().OAUTH_KEY_ENCRYPTION_KEY.strip()
    if not raw:
        raise RuntimeError(
            "OAUTH_KEY_ENCRYPTION_KEY is required for the MCP OAuth server. "
            "Generate one with `python -c 'import secrets,base64; "
            "print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'`"
        )
    try:
        kek = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:  # pragma: no cover - configuration error path
        raise RuntimeError(
            "OAUTH_KEY_ENCRYPTION_KEY must be url-safe base64 of 32 random bytes"
        ) from exc
    if len(kek) != 32:
        raise RuntimeError(
            "OAUTH_KEY_ENCRYPTION_KEY must decode to exactly 32 bytes; "
            f"got {len(kek)} bytes"
        )
    return kek


def _encrypt_private_pem(pem: bytes) -> bytes:
    kek = _load_kek()
    nonce = os.urandom(12)
    ct = AESGCM(kek).encrypt(nonce, pem, associated_data=b"oauth_signing_key")
    return nonce + ct


def _decrypt_private_pem(blob: bytes) -> bytes:
    kek = _load_kek()
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(kek).decrypt(nonce, ct, associated_data=b"oauth_signing_key")


# ---------------------------------------------------------------------------
# JWK helpers
# ---------------------------------------------------------------------------


def _b64url_uint(n: int) -> str:
    """Encode an integer as a URL-safe base64 big-endian byte string."""
    if n == 0:
        return "AA"
    length = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode(
        "ascii"
    )


def _public_jwk_from_private(private_key: rsa.RSAPrivateKey, kid: str) -> dict:
    public_numbers = private_key.public_key().public_numbers()
    return {
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": kid,
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }


# ---------------------------------------------------------------------------
# Database-backed key lifecycle
# ---------------------------------------------------------------------------


def _generate_signing_key(db: Session, *, mark_current: bool) -> SigningKey:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    kid = secrets.token_urlsafe(16)
    public_jwk = _public_jwk_from_private(private_key, kid)

    row = OAuthSigningKey(
        kid=kid,
        alg="RS256",
        public_jwk=public_jwk,
        private_pem_encrypted=_encrypt_private_pem(pem),
        is_current=mark_current,
    )
    db.add(row)
    db.commit()
    logger.info("Generated new MCP OAuth signing key kid=%s current=%s", kid, mark_current)
    return SigningKey(kid=kid, private_pem=pem, public_jwk=public_jwk)


def ensure_signing_key(db: Session) -> SigningKey:
    """Return the current key, generating one on first run."""
    current = (
        db.query(OAuthSigningKey)
        .filter(OAuthSigningKey.is_current.is_(True))
        .first()
    )
    if current is None:
        return _generate_signing_key(db, mark_current=True)
    pem = _decrypt_private_pem(bytes(current.private_pem_encrypted))
    return SigningKey(kid=current.kid, private_pem=pem, public_jwk=current.public_jwk)


def rotate_signing_key(db: Session, overlap: timedelta = timedelta(hours=24)) -> SigningKey:
    """Generate a new current key and demote the prior current key.

    ``overlap`` controls how long the prior key stays in JWKS so existing
    in-flight tokens continue to verify.
    """
    prior = (
        db.query(OAuthSigningKey)
        .filter(OAuthSigningKey.is_current.is_(True))
        .first()
    )
    new_key = _generate_signing_key(db, mark_current=True)
    if prior is not None and prior.kid != new_key.kid:
        prior.is_current = False
        prior.not_after = datetime.now(timezone.utc) + overlap
        db.commit()
    reload_keys(db)
    return new_key


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------


def reload_keys(db: Session) -> None:
    """Refresh the in-process cache from the database.

    Called at startup and after rotation. The cache holds every key
    whose ``not_after`` has not yet passed (or that has no expiry yet)
    so token verification works during the rotation overlap window.
    """
    global _CURRENT_KID
    now = datetime.now(timezone.utc)
    rows: List[OAuthSigningKey] = (
        db.query(OAuthSigningKey)
        .filter(
            (OAuthSigningKey.not_after.is_(None))
            | (OAuthSigningKey.not_after > now)
        )
        .all()
    )
    _KEY_CACHE.clear()
    current_kid: Optional[str] = None
    for row in rows:
        try:
            pem = _decrypt_private_pem(bytes(row.private_pem_encrypted))
        except Exception:
            logger.exception("Failed to decrypt signing key kid=%s", row.kid)
            continue
        _KEY_CACHE[row.kid] = SigningKey(
            kid=row.kid, private_pem=pem, public_jwk=row.public_jwk
        )
        if row.is_current:
            current_kid = row.kid
    _CURRENT_KID = current_kid


def current_signing_key() -> SigningKey:
    """Return the currently-current key for new-token signing.

    Raises :class:`RuntimeError` if :func:`reload_keys` has not been
    called yet — startup wiring should call it once before serving
    traffic.
    """
    if _CURRENT_KID is None:
        raise RuntimeError(
            "Signing key cache is empty — call reload_keys(db) at startup"
        )
    return _KEY_CACHE[_CURRENT_KID]


def get_signing_key_by_kid(kid: str) -> Optional[SigningKey]:
    return _KEY_CACHE.get(kid)


def public_jwks() -> dict:
    """JSON document returned at ``/.well-known/jwks.json``."""
    return {"keys": [k.public_jwk for k in _KEY_CACHE.values()]}
