"""Build the MCP ASGI app mounted at ``/mcp`` by :mod:`main`.

Strategy
--------
We do **not** instantiate a fresh ``FastMCP``: we import the one already
configured in :mod:`gcb_mcp` (33 tools registered). The backend then
intercepts :meth:`FastMCP.call_tool` to:

1. Read the ``mcp_auth`` bundle the bearer middleware stashed on the
   ASGI scope.
2. Check the tool's required OAuth scopes (``gcb_mcp.context.TOOL_SCOPES``).
3. Bind a per-request :class:`gcb_mcp.context.RequestContext` so the
   tool implementations talk to the local backend on the user's behalf.
4. Defer to the original handler.

This keeps the 33 tool sites untouched while still enforcing OAuth.
"""
from __future__ import annotations

import logging
from typing import Any, Sequence

from app.core.config import settings as app_settings
from app.core.mcp_oauth.config import get_oauth_settings
from gcb_mcp import RequestContext as GcbRequestContext
from gcb_mcp import mcp as gcb_mcp_instance
from gcb_mcp import scope as gcb_request_scope
from gcb_mcp.context import required_scopes as gcb_required_scopes

logger = logging.getLogger(__name__)


class InsufficientScope(Exception):
    """Raised inside ``call_tool`` to surface a clear error message."""


def _resolve_auth_from_request_context() -> dict | None:
    """Pull the bearer middleware bundle off the ASGI scope.

    FastMCP exposes the original Starlette ``Request`` via
    ``mcp.get_context().request_context.request``; the bearer middleware
    placed our auth bundle under ``scope["state"]["mcp_auth"]``.
    """
    try:
        ctx = gcb_mcp_instance.get_context()
        request = getattr(ctx.request_context, "request", None)
        if request is None:
            return None
        state = getattr(request, "scope", {}).get("state", {}) or {}
        return state.get("mcp_auth")
    except Exception:  # pragma: no cover - defensive
        return None


def _internal_api_base() -> str:
    """Return the URL gcb_mcp tools should hit for upstream calls.

    When running in-process inside the platform backend, we point the
    gcb_mcp HTTP helpers at our own loopback URL so they exercise the
    same FastAPI handlers the dashboard uses. The backend's
    ``BACKEND_PUBLIC_URL`` setting already points at the right place
    for both local dev and Railway.
    """
    return (app_settings.BACKEND_PUBLIC_URL or "http://localhost:8001").rstrip("/")


def _install_scope_enforcement() -> None:
    """Wrap ``FastMCP.call_tool`` once with auth + scope + context binding."""
    if getattr(gcb_mcp_instance, "_gcb_oauth_wrapped", False):
        return  # idempotent

    original_call_tool = gcb_mcp_instance.call_tool

    async def call_tool_with_auth(
        name: str, arguments: dict[str, Any]
    ) -> Sequence[Any] | dict[str, Any]:
        auth = _resolve_auth_from_request_context()
        if auth is None:
            # Should be impossible — the bearer middleware always runs
            # before FastMCP. Fail loudly.
            raise InsufficientScope("missing_auth_bundle")

        granted: frozenset[str] = auth.get("scopes", frozenset())
        needed = gcb_required_scopes(name)
        missing = [s for s in needed if s not in granted]
        if missing:
            raise InsufficientScope(
                f"insufficient_scope: tool '{name}' requires {needed}; "
                f"missing {missing}"
            )

        ctx = GcbRequestContext(
            api_base_url=_internal_api_base(),
            on_behalf_of_user_id=auth.get("user_id", ""),
            on_behalf_of_email=auth.get("user_email", ""),
            on_behalf_permissions=tuple(auth.get("user_permissions", ())),
            scopes=granted,
        )
        with gcb_request_scope(ctx):
            return await original_call_tool(name, arguments)

    gcb_mcp_instance.call_tool = call_tool_with_auth  # type: ignore[assignment]
    gcb_mcp_instance._gcb_oauth_wrapped = True  # type: ignore[attr-defined]
    logger.info(
        "Installed MCP scope enforcement on shared gcb_mcp instance "
        "(issuer=%s)",
        get_oauth_settings().issuer,
    )


def build_mcp_app():
    """Return the streamable-http ASGI app for mounting at ``/mcp``."""
    _install_scope_enforcement()
    return gcb_mcp_instance.streamable_http_app()
