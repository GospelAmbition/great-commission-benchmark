"""OAuth 2.1 + OIDC Authorization Server backing the MCP resource at /mcp.

This package implements the server-side machinery required for the MCP
2025-06-18 spec on top of the existing FastAPI backend:

* RFC 9728 protected-resource metadata
* RFC 8414 authorization-server metadata
* RFC 7591 dynamic client registration
* RFC 7636 PKCE S256
* RFC 6749 authorization code + refresh token grants with rotation
* RFC 8707 resource indicator binding (the ``aud`` claim)
* RFC 7009 token revocation

User authentication federates to Google OIDC, reusing the same Google
OAuth client already configured for the NextAuth-fronted web UI. The
issuer signs RS256 JWT access tokens; refresh tokens are opaque and
hashed at rest.
"""
