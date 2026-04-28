"""ASGI middleware verifying RS256 bearer tokens for the /mcp mount.

Sits between the FastAPI app and FastMCP's streamable-http ASGI app.
Verifies tokens, loads the GCB ``User`` row, and stashes auth metadata
on the ASGI scope so downstream MCP tool dispatch can read it without
another DB round-trip.
"""
from __future__ import annotations

import logging
import uuid
from typing import Awaitable, Callable

from app.core.mcp_oauth.config import get_oauth_settings
from app.core.mcp_oauth.jwt import TokenError, verify_access_token
from app.db.base import SessionLocal
from app.db.models.user import User

logger = logging.getLogger(__name__)

ASGIApp = Callable[[dict, Callable[[], Awaitable[dict]], Callable[[dict], Awaitable[None]]], Awaitable[None]]


def bearer_auth_asgi(inner_app: ASGIApp) -> ASGIApp:
    """Wrap ``inner_app`` (the FastMCP streamable-http ASGI app)."""

    async def app(scope: dict, receive, send) -> None:
        if scope.get("type") != "http":
            return await inner_app(scope, receive, send)

        token = _extract_bearer(scope.get("headers", []))
        if not token:
            return await _send_unauthorized(send, error="invalid_request")

        # Fresh DB session per request — closed in a finally so the auth
        # path never leaks connections under exception.
        db = SessionLocal()
        try:
            try:
                claims = verify_access_token(token, db)
            except TokenError as exc:
                logger.info("MCP auth rejected: %s", exc)
                return await _send_unauthorized(send, error="invalid_token")

            try:
                user = (
                    db.query(User)
                    .filter(User.id == uuid.UUID(claims.sub))
                    .first()
                )
            except Exception:
                user = None
            if user is None:
                return await _send_unauthorized(send, error="invalid_token")

            # Attach the auth bundle for the FastMCP dispatcher.
            scope.setdefault("state", {})
            scope["state"]["mcp_auth"] = {
                "user_id": str(user.id),
                "user_email": user.email or "",
                "user_permissions": _collect_permissions(user),
                "scopes": frozenset(claims.scopes),
                "jti": claims.jti,
                "client_id": claims.client_id,
            }
            return await inner_app(scope, receive, send)
        finally:
            db.close()

    return app


def _extract_bearer(headers: list[tuple[bytes, bytes]]) -> str:
    for name, value in headers:
        if name.lower() == b"authorization":
            decoded = value.decode("latin-1")
            if decoded.lower().startswith("bearer "):
                return decoded[7:].strip()
    return ""


def _collect_permissions(user: User) -> tuple[str, ...]:
    perms: list[str] = []
    if getattr(user, "can_view_benchmark", False):
        perms.append("can_view_benchmark")
    if getattr(user, "can_edit_benchmark", False):
        perms.append("can_edit_benchmark")
    if getattr(user, "can_moderate", False):
        perms.append("can_moderate")
    if getattr(user, "can_manage_blog", False):
        perms.append("can_manage_blog")
    if getattr(user, "can_admin", False):
        perms.append("can_admin")
    return tuple(perms)


async def _send_unauthorized(send, *, error: str) -> None:
    settings_ = get_oauth_settings()
    challenge = (
        f'Bearer realm="gcb-mcp", error="{error}", '
        f'resource_metadata="{settings_.issuer}/.well-known/oauth-protected-resource"'
    )
    await send(
        {
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", challenge.encode("latin-1")),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b'{"error":"' + error.encode("ascii") + b'"}',
        }
    )
