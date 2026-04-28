"""MCP-OAuth specific configuration.

Lives alongside :mod:`app.core.config` rather than in it so that adding
the OAuth feature does not couple every Settings consumer to the new
fields. Values default to local-development friendly placeholders and
are overridden via environment variables in deployed environments.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPOAuthSettings(BaseSettings):
    """Settings for the MCP OAuth Authorization + Resource Server."""

    # --- Issuer / resource identity ----------------------------------------
    # Stable URL the iPhone Claude app connects to. The /mcp endpoint and
    # the /.well-known/* metadata documents are served from this origin.
    MCP_ISSUER_URL: str = Field(
        default="http://localhost:8001",
        description="Base URL the AS advertises (also the resource URL for "
        "MCP requests). Override per-environment.",
    )

    # --- Google OIDC federation -------------------------------------------
    # Google credentials are reused from the platform's existing NextAuth
    # client. Only the redirect URI is new; register
    #   {MCP_ISSUER_URL}/oauth/callback/google
    # in Google Cloud Console.
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # --- Cryptographic material -------------------------------------------
    # 32-byte url-safe-base64 key used to AES-GCM encrypt RS256 private
    # keys at rest in oauth_signing_keys. Rotate carefully — see the
    # runbook docstring in keys.py.
    OAUTH_KEY_ENCRYPTION_KEY: str = ""

    # HMAC secret used to sign the AS session cookie (HTTP-only) that
    # links a browser visit to a row in oauth_pending_sessions.
    OAUTH_SESSION_COOKIE_SECRET: str = ""

    # --- Client policy ----------------------------------------------------
    # Hosts (without scheme) that may appear in registered redirect URIs.
    # Loopback (127.0.0.1, localhost) is always allowed regardless of
    # this list to keep MCP Inspector and CLI tools functional.
    MCP_ALLOWED_REDIRECT_URI_HOSTS: str = "claude.ai,claude.com"

    # When false, /oauth/register requires admin approval before tokens
    # are issued. Default true so the iPhone app + claude.ai can self-
    # register without an out-of-band step.
    MCP_ANONYMOUS_DCR_ENABLED: bool = True

    # --- Token lifetimes --------------------------------------------------
    # Short-lived access JWT, long-lived rotating refresh token.
    OAUTH_ACCESS_TOKEN_TTL_SECONDS: int = 3600       # 1 hour
    OAUTH_REFRESH_TOKEN_TTL_SECONDS: int = 30 * 24 * 3600  # 30 days
    OAUTH_AUTHORIZATION_CODE_TTL_SECONDS: int = 600  # 10 minutes
    OAUTH_PENDING_SESSION_TTL_SECONDS: int = 600     # 10 minutes
    OAUTH_AS_SESSION_TTL_SECONDS: int = 7 * 24 * 3600  # AS browser cookie

    # --- DCR rate limiting ------------------------------------------------
    OAUTH_REGISTER_RATE_LIMIT_PER_HOUR: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------

    @property
    def issuer(self) -> str:
        return self.MCP_ISSUER_URL.rstrip("/")

    @property
    def resource(self) -> str:
        # The MCP transport lives at {issuer}/mcp. We treat the issuer
        # origin itself as the resource identifier — that is what the
        # ``aud`` claim will encode and what RFC 9728 metadata reports.
        return self.issuer

    @property
    def authorization_endpoint(self) -> str:
        return f"{self.issuer}/oauth/authorize"

    @property
    def token_endpoint(self) -> str:
        return f"{self.issuer}/oauth/token"

    @property
    def registration_endpoint(self) -> str:
        return f"{self.issuer}/oauth/register"

    @property
    def revocation_endpoint(self) -> str:
        return f"{self.issuer}/oauth/revoke"

    @property
    def jwks_uri(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"

    @property
    def google_callback_url(self) -> str:
        return f"{self.issuer}/oauth/callback/google"

    @property
    def allowed_redirect_uri_hosts(self) -> List[str]:
        return [
            h.strip().lower()
            for h in self.MCP_ALLOWED_REDIRECT_URI_HOSTS.split(",")
            if h.strip()
        ]


@lru_cache(maxsize=1)
def get_oauth_settings() -> MCPOAuthSettings:
    """Singleton accessor — pydantic re-validates on each call otherwise."""
    return MCPOAuthSettings()
