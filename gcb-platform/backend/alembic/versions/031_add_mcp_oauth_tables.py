"""Add MCP OAuth Authorization Server tables

Revision ID: 031
Revises: 030
Create Date: 2026-04-27

Adds the seven OAuth tables backing the public, OAuth-fronted MCP at
/mcp. See app/core/mcp_oauth/models.py for column documentation. Raw
authorization codes / refresh tokens / client secrets are SHA-256
hashed at rest; the plaintext is returned to the caller exactly once.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA, INET, JSONB, UUID


revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # oauth_clients — RFC 7591 Dynamic Client Registration records
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_clients",
        sa.Column("client_id", sa.String(64), primary_key=True),
        sa.Column("client_secret_hash", sa.String(128), nullable=True),
        sa.Column("client_name", sa.String(255), nullable=False),
        sa.Column("redirect_uris", ARRAY(sa.String()), nullable=False),
        sa.Column(
            "grant_types",
            ARRAY(sa.String()),
            nullable=False,
            server_default="{authorization_code,refresh_token}",
        ),
        sa.Column(
            "response_types",
            ARRAY(sa.String()),
            nullable=False,
            server_default="{code}",
        ),
        sa.Column(
            "token_endpoint_auth_method",
            sa.String(40),
            nullable=False,
            server_default="none",
        ),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("software_id", sa.String(255), nullable=True),
        sa.Column("software_version", sa.String(64), nullable=True),
        sa.Column("client_uri", sa.Text(), nullable=True),
        sa.Column("registered_by_ip", INET(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------
    # oauth_authorization_codes — single-use, ~10 min TTL
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_authorization_codes",
        sa.Column("code_hash", sa.String(64), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(64),
            sa.ForeignKey("oauth_clients.client_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("code_challenge", sa.Text(), nullable=False),
        sa.Column("code_challenge_method", sa.String(8), nullable=False),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("nonce", sa.String(128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_oauth_authorization_codes_client_id",
        "oauth_authorization_codes",
        ["client_id"],
    )
    op.create_index(
        "ix_oauth_authorization_codes_user_id",
        "oauth_authorization_codes",
        ["user_id"],
    )

    # ------------------------------------------------------------------
    # oauth_refresh_tokens — rotating w/ replay-detection chain
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_refresh_tokens",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(64),
            sa.ForeignKey("oauth_clients.client_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("parent_token_hash", sa.String(64), nullable=True),
        sa.Column("replaced_by", sa.String(64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_oauth_refresh_tokens_client_id",
        "oauth_refresh_tokens",
        ["client_id"],
    )
    op.create_index(
        "ix_oauth_refresh_tokens_user_id",
        "oauth_refresh_tokens",
        ["user_id"],
    )
    op.create_index(
        "ix_oauth_refresh_tokens_parent",
        "oauth_refresh_tokens",
        ["parent_token_hash"],
    )

    # ------------------------------------------------------------------
    # oauth_pending_sessions — in-flight /authorize while at Google
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_pending_sessions",
        sa.Column("session_id", sa.String(64), primary_key=True),
        sa.Column("client_id", sa.String(64), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("code_challenge", sa.Text(), nullable=False),
        sa.Column("code_challenge_method", sa.String(8), nullable=False),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("google_state", sa.String(64), nullable=False),
        sa.Column("google_nonce", sa.String(64), nullable=False),
        sa.Column("google_pkce_verifier", sa.String(128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # oauth_as_sessions — AS browser cookie → user
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_as_sessions",
        sa.Column("session_id", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_oauth_as_sessions_user_id",
        "oauth_as_sessions",
        ["user_id"],
    )

    # ------------------------------------------------------------------
    # oauth_signing_keys — RS256 keypair store, KEK-encrypted
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_signing_keys",
        sa.Column("kid", sa.String(64), primary_key=True),
        sa.Column("alg", sa.String(16), nullable=False, server_default="RS256"),
        sa.Column("public_jwk", JSONB(), nullable=False),
        sa.Column("private_pem_encrypted", BYTEA(), nullable=False),
        sa.Column(
            "not_before",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("not_after", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # oauth_token_audit — partial-indexed revocation list
    # ------------------------------------------------------------------
    op.create_table(
        "oauth_token_audit",
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("jti", sa.String(64), nullable=False),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.String(64),
            sa.ForeignKey("oauth_clients.client_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Partial index: only revoked rows participate. The bearer middleware
    # checks "is this jti revoked" on every request, so optimising for the
    # rare row count keeps it cheap.
    op.execute(
        "CREATE INDEX ix_oauth_token_audit_revoked_jti "
        "ON oauth_token_audit (jti) WHERE revoked_at IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_oauth_token_audit_revoked_jti")
    op.drop_table("oauth_token_audit")
    op.drop_table("oauth_signing_keys")
    op.drop_index("ix_oauth_as_sessions_user_id", table_name="oauth_as_sessions")
    op.drop_table("oauth_as_sessions")
    op.drop_table("oauth_pending_sessions")
    op.drop_index("ix_oauth_refresh_tokens_parent", table_name="oauth_refresh_tokens")
    op.drop_index("ix_oauth_refresh_tokens_user_id", table_name="oauth_refresh_tokens")
    op.drop_index("ix_oauth_refresh_tokens_client_id", table_name="oauth_refresh_tokens")
    op.drop_table("oauth_refresh_tokens")
    op.drop_index(
        "ix_oauth_authorization_codes_user_id",
        table_name="oauth_authorization_codes",
    )
    op.drop_index(
        "ix_oauth_authorization_codes_client_id",
        table_name="oauth_authorization_codes",
    )
    op.drop_table("oauth_authorization_codes")
    op.drop_table("oauth_clients")
