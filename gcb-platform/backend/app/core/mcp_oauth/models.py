"""SQLAlchemy ORM models for the MCP OAuth tables.

Six tables are added to the existing platform database. They use the
shared :data:`app.db.base.Base` so a single Alembic migration ships them
under the existing ``alembic_version`` table.

All raw secrets (authorization codes, refresh tokens, client secrets)
are SHA-256 hashed at rest. The plaintext is returned to the caller
exactly once, at issuance.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID, BYTEA
from sqlalchemy.sql import func

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OAuthClient(Base):
    """RFC 7591 dynamically-registered OAuth client."""

    __tablename__ = "oauth_clients"

    client_id = Column(String(64), primary_key=True)
    # Hash of client_secret. Null for public clients (token_endpoint_auth_method='none').
    client_secret_hash = Column(String(128), nullable=True)
    client_name = Column(String(255), nullable=False)
    redirect_uris = Column(ARRAY(String), nullable=False)
    grant_types = Column(
        ARRAY(String),
        nullable=False,
        server_default="{authorization_code,refresh_token}",
    )
    response_types = Column(
        ARRAY(String),
        nullable=False,
        server_default="{code}",
    )
    token_endpoint_auth_method = Column(
        String(40), nullable=False, server_default="none"
    )
    # Default scope string (space-delimited) the client may request.
    scope = Column(Text, nullable=True)
    software_id = Column(String(255), nullable=True)
    software_version = Column(String(64), nullable=True)
    client_uri = Column(Text, nullable=True)
    registered_by_ip = Column(INET, nullable=True)
    is_approved = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)


class OAuthAuthorizationCode(Base):
    """Single-use authorization code with PKCE binding (~10 min TTL)."""

    __tablename__ = "oauth_authorization_codes"

    # SHA-256 hash of the issued code; the raw code is never stored.
    code_hash = Column(String(64), primary_key=True)
    client_id = Column(
        String(64),
        ForeignKey("oauth_clients.client_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    redirect_uri = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    code_challenge = Column(Text, nullable=False)
    code_challenge_method = Column(String(8), nullable=False)
    # RFC 8707 audience binding so the resulting access token cannot be
    # used against a different resource.
    resource = Column(Text, nullable=True)
    nonce = Column(String(128), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OAuthRefreshToken(Base):
    """Rotating refresh token with replay-detection chain."""

    __tablename__ = "oauth_refresh_tokens"

    token_hash = Column(String(64), primary_key=True)
    client_id = Column(
        String(64),
        ForeignKey("oauth_clients.client_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scope = Column(Text, nullable=False)
    # Hash of the previous token in the rotation chain. Detects replay:
    # if a consumed parent is presented again, we walk the chain via
    # ``replaced_by`` and revoke the entire family (RFC 6819 §5.2.2.3).
    parent_token_hash = Column(String(64), nullable=True, index=True)
    replaced_by = Column(String(64), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OAuthPendingSession(Base):
    """In-flight ``/authorize`` while the user is at Google."""

    __tablename__ = "oauth_pending_sessions"

    session_id = Column(String(64), primary_key=True)
    client_id = Column(String(64), nullable=False)
    redirect_uri = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    state = Column(Text, nullable=False)
    code_challenge = Column(Text, nullable=False)
    code_challenge_method = Column(String(8), nullable=False)
    resource = Column(Text, nullable=True)
    # Google federation parameters
    google_state = Column(String(64), nullable=False)
    google_nonce = Column(String(64), nullable=False)
    google_pkce_verifier = Column(String(128), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OAuthASSession(Base):
    """Browser-side AS session linking a logged-in user to a cookie.

    Lets us skip the round-trip to Google when the user is already
    authenticated within the cookie's lifetime, mirroring how NextAuth
    keeps users signed in across visits.
    """

    __tablename__ = "oauth_as_sessions"

    session_id = Column(String(64), primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OAuthSigningKey(Base):
    """RS256 signing keypair, private half encrypted at rest."""

    __tablename__ = "oauth_signing_keys"

    kid = Column(String(64), primary_key=True)
    alg = Column(String(16), nullable=False, server_default="RS256")
    public_jwk = Column(JSONB, nullable=False)
    # AES-GCM ciphertext of the PKCS#8 private key, KEK from
    # OAUTH_KEY_ENCRYPTION_KEY. ``nonce || ciphertext || tag`` layout.
    private_pem_encrypted = Column(BYTEA, nullable=False)
    not_before = Column(DateTime(timezone=True), server_default=func.now())
    not_after = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OAuthTokenAudit(Base):
    """Per-issuance row used for revocation lookups.

    Access tokens are JWTs verifiable offline; emergency revocation sets
    ``revoked_at`` here and the bearer middleware checks the partial
    index ``WHERE revoked_at IS NOT NULL`` on every request — cheap
    because only revoked rows match.
    """

    __tablename__ = "oauth_token_audit"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    jti = Column(String(64), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id = Column(
        String(64),
        ForeignKey("oauth_clients.client_id", ondelete="SET NULL"),
        nullable=True,
    )
    issued_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at = Column(DateTime(timezone=True), nullable=True)


# Partial index — only revoked rows participate. Matches the access-time
# query "is this jti revoked" without bloating the index.
Index(
    "ix_oauth_token_audit_revoked_jti",
    OAuthTokenAudit.jti,
    postgresql_where=OAuthTokenAudit.revoked_at.isnot(None),
)
