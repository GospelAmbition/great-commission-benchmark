"""Scope ↔ permission-flag mapping for the MCP OAuth Authorization Server.

The MCP server exposes a small fixed scope vocabulary; each scope maps
to one of the existing :class:`User` permission flags. Scope grants are
computed at ``/oauth/authorize`` time as the intersection of:

    requested_scopes ∩ user_permitted_scopes(user)

This keeps the platform's existing role/permission model as the single
source of truth — no new privilege ladder.
"""
from __future__ import annotations

from typing import Iterable, List, Set

from app.db.models.user import User

# Public mcp:read is always granted to any authenticated user.
SCOPE_READ = "mcp:read"
SCOPE_WRITE = "mcp:write"
SCOPE_BLOG = "mcp:blog"
SCOPE_NEWSLETTER = "mcp:newsletter"
SCOPE_ADMIN = "mcp:admin"

ALL_SCOPES: tuple[str, ...] = (
    SCOPE_READ,
    SCOPE_WRITE,
    SCOPE_BLOG,
    SCOPE_NEWSLETTER,
    SCOPE_ADMIN,
)

# Scope → required permission attribute on User. ``mcp:read`` is granted
# to any authed user so it has no required flag.
_SCOPE_PERMISSION_MAP: dict[str, str] = {
    SCOPE_WRITE: "can_edit_benchmark",
    SCOPE_BLOG: "can_manage_blog",
    SCOPE_NEWSLETTER: "can_manage_blog",
    SCOPE_ADMIN: "can_admin",
}


def user_permitted_scopes(user: User) -> Set[str]:
    """Return the set of scopes that may be granted to ``user``.

    ``can_admin`` cascades to all scopes (matches
    :func:`app.core.auth.get_user_permissions` semantics).
    """
    if not user:
        return set()
    if getattr(user, "can_admin", False):
        return set(ALL_SCOPES)

    granted: Set[str] = {SCOPE_READ}
    for scope, perm in _SCOPE_PERMISSION_MAP.items():
        if getattr(user, perm, False):
            granted.add(scope)
    return granted


def parse_scope_string(raw: str | None) -> List[str]:
    """Parse a space-delimited OAuth ``scope`` parameter into a list.

    Unknown scope tokens are silently dropped — the AS will refuse to
    grant them anyway and a 400 from us would surprise generic clients.
    """
    if not raw:
        return []
    seen: Set[str] = set()
    out: List[str] = []
    for token in raw.split():
        if token in ALL_SCOPES and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def grant_scopes(requested: Iterable[str], user: User) -> List[str]:
    """Compute granted scopes = requested ∩ user_permitted.

    Always implicitly includes :data:`SCOPE_READ` for authed users so a
    "no scope requested" connector still gets a useful token.
    """
    permitted = user_permitted_scopes(user)
    requested_set = set(requested) if requested else {SCOPE_READ}
    granted = (requested_set & permitted) | {SCOPE_READ}
    # Preserve a deterministic order for predictable token claims.
    return [s for s in ALL_SCOPES if s in granted]


def format_scope_string(scopes: Iterable[str]) -> str:
    return " ".join(scopes)
