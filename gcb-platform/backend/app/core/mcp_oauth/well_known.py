"""RFC 9728 + RFC 8414 + JWKS metadata documents.

These three URLs MUST live at the top-level origin (no /api prefix) so
RFC 9728-compliant MCP clients (the iPhone Claude app, claude.ai, MCP
Inspector) can discover them via well-known paths. The router is
``include_router`` ed at app root in :mod:`main`.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.mcp_oauth.config import get_oauth_settings
from app.core.mcp_oauth.keys import public_jwks
from app.core.mcp_oauth.scopes import ALL_SCOPES

router = APIRouter(tags=["oauth-discovery"])


@router.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource_metadata() -> dict:
    """RFC 9728 protected resource metadata.

    The MCP transport at /mcp is the protected resource. Clients use
    this document to discover which authorization server(s) they can
    obtain tokens from.
    """
    s = get_oauth_settings()
    return {
        "resource": s.resource,
        "authorization_servers": [s.issuer],
        "scopes_supported": list(ALL_SCOPES),
        "bearer_methods_supported": ["header"],
        "resource_documentation": f"{s.issuer}/docs/mcp",
    }


@router.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server_metadata() -> dict:
    """RFC 8414 authorization server metadata."""
    s = get_oauth_settings()
    return {
        "issuer": s.issuer,
        "authorization_endpoint": s.authorization_endpoint,
        "token_endpoint": s.token_endpoint,
        "registration_endpoint": s.registration_endpoint,
        "revocation_endpoint": s.revocation_endpoint,
        "jwks_uri": s.jwks_uri,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": [
            "none",
            "client_secret_basic",
            "client_secret_post",
        ],
        "scopes_supported": list(ALL_SCOPES),
        "service_documentation": f"{s.issuer}/docs/mcp",
    }


@router.get("/.well-known/jwks.json")
async def jwks() -> dict:
    """Public RS256 keys used to verify access tokens."""
    return public_jwks()
