"""Issue and verify RS256 access tokens for the MCP resource.

Tokens are JWTs with an RFC 8707 ``aud`` claim bound to the MCP
resource URL — defence against the confused-deputy hazard MCP
2025-06-18 §2.4 calls out.

Refresh tokens are NOT JWTs: they are opaque random strings stored as
SHA-256 hashes in :class:`OAuthRefreshToken`. See
:mod:`app.core.mcp_oauth.endpoints` for the rotation logic.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.mcp_oauth.config import get_oauth_settings
from app.core.mcp_oauth.keys import (
    SigningKey,
    current_signing_key,
    get_signing_key_by_kid,
)
from app.core.mcp_oauth.models import OAuthTokenAudit


class TokenError(ValueError):
    """Raised by :func:`verify_access_token` for any rejection reason."""


@dataclass(frozen=True)
class AccessTokenClaims:
    """Convenience view of the verified JWT body."""

    jti: str
    sub: str            # user UUID as string
    email: str
    client_id: str
    scopes: frozenset[str]
    expires_at: datetime


# ---------------------------------------------------------------------------
# Issue
# ---------------------------------------------------------------------------


def issue_access_token(
    *,
    db: Session,
    user_id: str,
    user_email: str,
    client_id: str,
    scopes: Iterable[str],
    resource: Optional[str] = None,
) -> tuple[str, AccessTokenClaims]:
    """Mint an RS256 JWT and record an audit row for revocation tracking."""
    settings_ = get_oauth_settings()
    key: SigningKey = current_signing_key()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=settings_.OAUTH_ACCESS_TOKEN_TTL_SECONDS)
    jti = uuid.uuid4().hex
    scope_list = sorted(set(scopes))
    payload = {
        "iss": settings_.issuer,
        "sub": str(user_id),
        "aud": resource or settings_.resource,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "jti": jti,
        "client_id": client_id,
        "scope": " ".join(scope_list),
        "email": user_email or "",
    }
    token = jwt.encode(
        payload,
        key.private_pem.decode("utf-8"),
        algorithm="RS256",
        headers={"kid": key.kid},
    )

    db.add(
        OAuthTokenAudit(
            jti=jti,
            user_id=uuid.UUID(str(user_id)),
            client_id=client_id,
        )
    )
    db.commit()

    return token, AccessTokenClaims(
        jti=jti,
        sub=str(user_id),
        email=user_email or "",
        client_id=client_id,
        scopes=frozenset(scope_list),
        expires_at=exp,
    )


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


def verify_access_token(token: str, db: Session) -> AccessTokenClaims:
    """Decode + validate a bearer token. Raises :class:`TokenError` on failure."""
    settings_ = get_oauth_settings()
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise TokenError(f"malformed_token: {exc}") from exc

    kid = unverified_header.get("kid")
    if not kid:
        raise TokenError("missing_kid")
    key = get_signing_key_by_kid(kid)
    if key is None:
        raise TokenError(f"unknown_kid:{kid}")

    try:
        payload = jwt.decode(
            token,
            _public_pem_from_jwk(key.public_jwk),
            algorithms=["RS256"],
            audience=settings_.resource,
            issuer=settings_.issuer,
            options={"require_aud": True, "require_iss": True, "require_exp": True},
        )
    except JWTError as exc:
        raise TokenError(f"invalid_token: {exc}") from exc

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise TokenError("missing_claims")

    # Revocation check via the partial index. Only revoked rows match.
    revoked = (
        db.query(OAuthTokenAudit.id)
        .filter(
            OAuthTokenAudit.jti == jti,
            OAuthTokenAudit.revoked_at.isnot(None),
        )
        .first()
    )
    if revoked is not None:
        raise TokenError("revoked_token")

    scope_str = payload.get("scope") or ""
    return AccessTokenClaims(
        jti=jti,
        sub=str(sub),
        email=str(payload.get("email") or ""),
        client_id=str(payload.get("client_id") or ""),
        scopes=frozenset(scope_str.split()),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
    )


def _public_pem_from_jwk(jwk: dict) -> bytes:
    """Derive a PEM-encoded public RSA key from the stored JWK.

    We re-derive on each verification rather than caching the PEM
    because key rotation invalidates the cache anyway and the cost is
    negligible compared to RSA verification itself.
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import base64

    def _b64url_to_int(s: str) -> int:
        padded = s + "=" * (-len(s) % 4)
        return int.from_bytes(base64.urlsafe_b64decode(padded), "big")

    n = _b64url_to_int(jwk["n"])
    e = _b64url_to_int(jwk["e"])
    public_numbers = rsa.RSAPublicNumbers(e=e, n=n)
    public_key = public_numbers.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


# ---------------------------------------------------------------------------
# Refresh tokens (opaque)
# ---------------------------------------------------------------------------


def generate_refresh_token() -> tuple[str, str]:
    """Return ``(plaintext, sha256_hex_hash)`` for a fresh refresh token."""
    raw = secrets.token_urlsafe(40)
    return raw, hashlib.sha256(raw.encode("ascii")).hexdigest()


def hash_refresh_token(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("ascii")).hexdigest()


def hash_authorization_code(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("ascii")).hexdigest()


def hash_client_secret(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("ascii")).hexdigest()


__all__ = [
    "AccessTokenClaims",
    "TokenError",
    "generate_refresh_token",
    "hash_authorization_code",
    "hash_client_secret",
    "hash_refresh_token",
    "issue_access_token",
    "verify_access_token",
]
