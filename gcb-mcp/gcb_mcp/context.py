"""Request-scoped context for GCB MCP tools.

Background
----------
The original stdio MCP resolved its credentials and base URL purely from
process environment / the gcb-runner config file. That's fine for a CLI
where one user owns the process. The HTTP/OAuth-fronted MCP, however,
serves multiple users from one process: the credentials, base URL, and
optional on-behalf-of metadata must vary per request.

Design
------
A single ``ContextVar`` carries a :class:`RequestContext` for the active
asyncio Task. Helpers across the package (``_api_base()``, ``_api_key()``,
``_base_url()``) consult :func:`current()` first and fall back to the
historical env-var / credentials.json behaviour, so stdio users see no
change.

The HTTP MCP entrypoint sets the ContextVar at the start of every
authenticated MCP request via :func:`bind` (returns a token to be reset
in a ``finally`` block — or use :func:`scope` as an async context
manager).

Tools must NEVER mutate the context object; build a new one if you need
different fields downstream.
"""

from __future__ import annotations

import contextlib
import contextvars
from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class RequestContext:
    """Per-request configuration consumed by GCB MCP tools.

    All fields are optional so a default-constructed context preserves
    the historical env-var fallback behaviour.

    Attributes
    ----------
    api_key:
        X-API-Key value sent on upstream calls to the GCB platform. If
        empty, callers fall back to ``credentials.resolve_gcb_api_key()``.
    api_base_url:
        Override for ``GCB_API_BASE_URL``. If empty, env var or built-in
        default is used.
    on_behalf_of_user_id:
        UUID of the OAuth-authenticated user this request is acting on
        behalf of. Sent as ``X-On-Behalf-Of`` to the platform when the
        platform is configured to honour it.
    on_behalf_of_email:
        Email of the OAuth user (telemetry / audit only).
    on_behalf_permissions:
        Permission flag names from the user's row, joined by comma. Sent
        as ``X-Behalf-Permissions`` for the platform to re-check.
    scopes:
        OAuth scopes granted on the active access token. Tools may
        consult this for additional gating; the primary scope check
        happens in the FastMCP tool wrapper.
    """

    api_key: str = ""
    api_base_url: str = ""
    on_behalf_of_user_id: str = ""
    on_behalf_of_email: str = ""
    on_behalf_permissions: tuple[str, ...] = field(default_factory=tuple)
    scopes: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_oauth_request(self) -> bool:
        return bool(self.on_behalf_of_user_id)


_EMPTY = RequestContext()

_CURRENT: contextvars.ContextVar[RequestContext] = contextvars.ContextVar(
    "gcb_mcp_request_context", default=_EMPTY
)


def current() -> RequestContext:
    """Return the active :class:`RequestContext`, or the empty default."""
    return _CURRENT.get()


def bind(ctx: RequestContext) -> contextvars.Token[RequestContext]:
    """Set ``ctx`` as the active context.

    Returns the token to pass to :func:`reset`. Prefer the :func:`scope`
    context manager when possible.
    """
    return _CURRENT.set(ctx)


def reset(token: contextvars.Token[RequestContext]) -> None:
    """Restore the prior :class:`RequestContext` for this Task."""
    _CURRENT.reset(token)


@contextlib.contextmanager
def scope(ctx: RequestContext) -> Iterator[RequestContext]:
    """Temporarily activate ``ctx`` for the lifetime of the ``with`` block."""
    token = bind(ctx)
    try:
        yield ctx
    finally:
        reset(token)


def behalf_headers() -> dict[str, str]:
    """Return ``X-On-Behalf-Of`` headers for the current request, if any.

    Returns an empty dict when the active context is the default empty
    one (e.g. stdio CLI invocations) so existing callers can simply
    ``headers.update(behalf_headers())``.
    """
    ctx = current()
    if not ctx.is_oauth_request:
        return {}
    headers: dict[str, str] = {"X-On-Behalf-Of": ctx.on_behalf_of_user_id}
    if ctx.on_behalf_of_email:
        headers["X-On-Behalf-Of-Email"] = ctx.on_behalf_of_email
    if ctx.on_behalf_permissions:
        headers["X-Behalf-Permissions"] = ",".join(ctx.on_behalf_permissions)
    return headers


# ---------------------------------------------------------------------------
# Scope manifest
# ---------------------------------------------------------------------------
#
# Single source of truth mapping each registered MCP tool to the OAuth
# scope(s) required to invoke it. The stdio CLI ignores this manifest
# (it has no notion of OAuth); the HTTP server consults it inside the
# ``call_tool`` dispatch path to short-circuit before executing the
# tool body. Keeping the manifest co-located with :class:`RequestContext`
# avoids a circular import between ``server`` and the backend mount.
#
# Naming convention:
#   mcp:read         — discovery / read-only views, granted to every authed user
#   mcp:write        — model + job + upload mutations (can_edit_benchmark)
#   mcp:blog         — blog CRUD + model-review draft (can_manage_blog)
#   mcp:newsletter   — newsletter draft / preview / test recipients (can_manage_blog)
#   mcp:admin        — admin-only sends + privileged operations (can_admin)

TOOL_SCOPES: dict[str, tuple[str, ...]] = {
    # Discovery / readonly
    "list_active_models": ("mcp:read",),
    "compare_models": ("mcp:read",),
    "suggest_models_to_test": ("mcp:read",),
    "preview_archive_candidates": ("mcp:read",),
    "check_ready_for_testing": ("mcp:read",),
    "list_jobs": ("mcp:read",),
    "get_job_status": ("mcp:read",),
    "get_job_logs": ("mcp:read",),
    "list_published_models": ("mcp:read",),
    "get_model_test_result": ("mcp:read",),
    "resolve_model_highlight_context": ("mcp:read",),
    "list_blog_posts": ("mcp:read",),
    "get_blog_post": ("mcp:read",),
    "list_blog_categories": ("mcp:read",),
    "get_local_test_json": ("mcp:read",),
    "get_remote_test_json": ("mcp:read",),
    # Mutations on benchmark data
    "archive_missing_on_openrouter": ("mcp:write",),
    "run_gcb_test": ("mcp:write",),
    "start_gcb_test": ("mcp:write",),
    "upload_json": ("mcp:write",),
    "upload_runner_json": ("mcp:write",),
    "upload_result": ("mcp:write",),
    "generate_and_upload_header": ("mcp:write",),
    "generate_and_upload_highlight_header": ("mcp:write",),
    "generate_and_upload_highlight_chart": ("mcp:write",),
    # Blog
    "create_blog_draft": ("mcp:blog",),
    "update_blog_post": ("mcp:blog",),
    "publish_blog_post": ("mcp:blog",),
    "create_model_review_draft": ("mcp:blog",),
    "create_model_highlight_draft": ("mcp:blog",),
    # Newsletter
    "create_monthly_newsletter_draft": ("mcp:newsletter",),
    "render_newsletter_email_html": ("mcp:newsletter",),
    "render_highlight_email_html": ("mcp:newsletter",),
    "list_newsletter_test_recipients": ("mcp:newsletter",),
    "add_newsletter_test_recipient": ("mcp:newsletter",),
    "update_newsletter_test_recipient": ("mcp:newsletter",),
    "remove_newsletter_test_recipient": ("mcp:newsletter",),
    "generate_and_upload_newsletter_header": ("mcp:newsletter",),
    # Admin-only
    "send_newsletter_to_subscribers": ("mcp:admin",),
    "send_highlight_to_subscribers": ("mcp:admin",),
}

#: Tools every authenticated user can call without explicit grants beyond
#: ``mcp:read``. Useful for the consent UI to display the always-on set.
ALWAYS_READ_TOOLS = frozenset(
    name for name, scopes in TOOL_SCOPES.items() if scopes == ("mcp:read",)
)


def required_scopes(tool_name: str) -> tuple[str, ...]:
    """Return the OAuth scopes required to invoke ``tool_name``.

    Unknown tools default to ``("mcp:admin",)`` — fail closed.
    """
    return TOOL_SCOPES.get(tool_name, ("mcp:admin",))


__all__ = [
    "ALWAYS_READ_TOOLS",
    "RequestContext",
    "TOOL_SCOPES",
    "behalf_headers",
    "bind",
    "current",
    "required_scopes",
    "reset",
    "scope",
]
