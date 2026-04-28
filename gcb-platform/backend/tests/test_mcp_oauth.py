"""Unit tests for the MCP OAuth Authorization Server building blocks.

Covers the pure-logic pieces that don't need DB or HTTP:

* PKCE S256 verification + downgrade rejection
* Scope ↔ permission-flag mapping (incl. admin cascade)
* Redirect URI allowlist enforcement (loopback, claude.ai, https-only)
* Scope manifest covers every registered gcb_mcp tool

The full authorize → token → /mcp flow is intentionally not exercised
here; it requires Postgres-specific column types (ARRAY/INET/BYTEA) and
a Google OIDC mock. End-to-end coverage lives in the manual MCP
Inspector check documented in the deployment plan.
"""
from __future__ import annotations

import pytest

from app.core.mcp_oauth.endpoints import _redirect_uri_allowed
from app.core.mcp_oauth.pkce import PKCEError, S256, assert_supported_method, verify_s256
from app.core.mcp_oauth.scopes import (
    ALL_SCOPES,
    SCOPE_ADMIN,
    SCOPE_BLOG,
    SCOPE_NEWSLETTER,
    SCOPE_READ,
    SCOPE_WRITE,
    grant_scopes,
    parse_scope_string,
    user_permitted_scopes,
)


# ---------------------------------------------------------------------------
# PKCE
# ---------------------------------------------------------------------------


class TestPKCE:
    def test_s256_round_trip(self):
        # Real PKCE pair: verifier of 64 chars, challenge from sha256+b64url.
        import base64
        import hashlib

        verifier = "a" * 64
        digest = hashlib.sha256(verifier.encode()).digest()
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        assert verify_s256(verifier, challenge) is True

    def test_s256_rejects_wrong_verifier(self):
        assert verify_s256("nope", "anything") is False

    def test_s256_rejects_short_verifier(self):
        # RFC 7636 §4.1: min 43 chars.
        assert verify_s256("a" * 10, "anything") is False

    def test_s256_rejects_long_verifier(self):
        assert verify_s256("a" * 200, "anything") is False

    def test_plain_method_rejected(self):
        with pytest.raises(PKCEError):
            assert_supported_method("plain")

    def test_missing_method_rejected(self):
        with pytest.raises(PKCEError):
            assert_supported_method(None)

    def test_s256_method_accepted(self):
        # Should not raise.
        assert_supported_method(S256)


# ---------------------------------------------------------------------------
# Scopes
# ---------------------------------------------------------------------------


class _FakeUser:
    """Minimal stand-in for app.db.models.user.User used in pure logic tests."""

    def __init__(self, **flags):
        self.can_view_benchmark = flags.get("can_view_benchmark", False)
        self.can_edit_benchmark = flags.get("can_edit_benchmark", False)
        self.can_moderate = flags.get("can_moderate", False)
        self.can_manage_blog = flags.get("can_manage_blog", False)
        self.can_admin = flags.get("can_admin", False)


class TestScopes:
    def test_basic_user_only_has_read(self):
        user = _FakeUser()
        assert user_permitted_scopes(user) == {SCOPE_READ}

    def test_blog_manager_gets_blog_and_newsletter(self):
        user = _FakeUser(can_manage_blog=True)
        permitted = user_permitted_scopes(user)
        assert SCOPE_READ in permitted
        assert SCOPE_BLOG in permitted
        assert SCOPE_NEWSLETTER in permitted
        assert SCOPE_WRITE not in permitted
        assert SCOPE_ADMIN not in permitted

    def test_benchmark_editor_gets_write(self):
        user = _FakeUser(can_edit_benchmark=True)
        assert SCOPE_WRITE in user_permitted_scopes(user)

    def test_admin_cascades_to_all_scopes(self):
        user = _FakeUser(can_admin=True)
        assert user_permitted_scopes(user) == set(ALL_SCOPES)

    def test_grant_scopes_intersects_requested_with_permitted(self):
        # User has only blog/newsletter perms; asks for write+blog → only blog.
        user = _FakeUser(can_manage_blog=True)
        granted = grant_scopes([SCOPE_WRITE, SCOPE_BLOG], user)
        assert SCOPE_BLOG in granted
        assert SCOPE_WRITE not in granted
        # mcp:read is always implicitly added for authenticated users.
        assert SCOPE_READ in granted

    def test_grant_scopes_always_includes_read(self):
        granted = grant_scopes([], _FakeUser())
        assert SCOPE_READ in granted

    def test_parse_scope_string_drops_unknown(self):
        assert parse_scope_string("mcp:read garbage mcp:admin") == [
            SCOPE_READ,
            SCOPE_ADMIN,
        ]

    def test_parse_scope_string_handles_none_and_empty(self):
        assert parse_scope_string(None) == []
        assert parse_scope_string("") == []


# ---------------------------------------------------------------------------
# Redirect URI allowlist
# ---------------------------------------------------------------------------


class TestRedirectUriAllowed:
    @pytest.fixture
    def hosts(self):
        return ["claude.ai", "claude.com"]

    def test_https_to_claude_ai_allowed(self, hosts):
        assert _redirect_uri_allowed("https://claude.ai/api/mcp/auth_callback", hosts)

    def test_https_subdomain_of_allowlisted_allowed(self, hosts):
        assert _redirect_uri_allowed("https://app.claude.ai/cb", hosts)

    def test_loopback_http_allowed(self, hosts):
        assert _redirect_uri_allowed("http://127.0.0.1:8765/cb", hosts)
        assert _redirect_uri_allowed("http://localhost:8765/cb", hosts)

    def test_non_loopback_http_rejected(self, hosts):
        assert not _redirect_uri_allowed("http://evil.example/cb", hosts)
        # Even the allowlisted host: only HTTPS is acceptable for it.
        assert not _redirect_uri_allowed("http://claude.ai/cb", hosts)

    def test_unrelated_https_rejected(self, hosts):
        assert not _redirect_uri_allowed("https://attacker.example/cb", hosts)

    def test_javascript_scheme_rejected(self, hosts):
        assert not _redirect_uri_allowed("javascript:alert(1)", hosts)

    def test_bare_url_rejected(self, hosts):
        assert not _redirect_uri_allowed("not-a-url", hosts)


# ---------------------------------------------------------------------------
# Tool scope manifest is exhaustive
# ---------------------------------------------------------------------------


def test_scope_manifest_matches_registered_tools():
    """Every gcb_mcp tool has a scope mapping; no orphans on either side."""
    from gcb_mcp import mcp
    from gcb_mcp.context import TOOL_SCOPES

    registered = {t.name for t in mcp._tool_manager.list_tools()}
    assert registered == set(TOOL_SCOPES.keys()), (
        f"missing in manifest: {sorted(registered - TOOL_SCOPES.keys())}; "
        f"extra in manifest: {sorted(TOOL_SCOPES.keys() - registered)}"
    )


def test_every_scope_in_manifest_is_known():
    """Catch typos like 'mcp:writez' that would silently fail-closed."""
    from gcb_mcp.context import TOOL_SCOPES

    for tool_name, scopes in TOOL_SCOPES.items():
        for s in scopes:
            assert s in ALL_SCOPES, f"{tool_name} references unknown scope {s!r}"
