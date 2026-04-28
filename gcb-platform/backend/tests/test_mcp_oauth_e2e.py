"""End-to-end smoke tests for the MCP OAuth integration.

These exercise the full ASGI stack via FastAPI's TestClient — discovery
metadata, JWKS, DCR, /mcp 401 with WWW-Authenticate. They use the
SQLite shims from conftest plus a fresh KEK so signing-key generation
works.

Full Google OIDC + token exchange is still not covered (would require
mocking httpx against accounts.google.com); those paths are unit-tested
in test_mcp_oauth.py.
"""
from __future__ import annotations

import base64
import os
import secrets
from urllib.parse import urlparse

import pytest


@pytest.fixture(scope="module", autouse=True)
def _oauth_env():
    """Ensure the OAuth subsystem has the env it needs to start."""
    kek = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    cookie = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    keys_to_set = {
        "OAUTH_KEY_ENCRYPTION_KEY": kek,
        "OAUTH_SESSION_COOKIE_SECRET": cookie,
        "MCP_ISSUER_URL": "http://test",
        "GOOGLE_CLIENT_ID": "test-client-id",
        "GOOGLE_CLIENT_SECRET": "test-client-secret",
        "NEXTAUTH_SECRET": "test-nextauth",
    }
    saved = {k: os.environ.get(k) for k in keys_to_set}
    os.environ.update(keys_to_set)
    # Force pydantic-settings to re-read env.
    from app.core.mcp_oauth.config import get_oauth_settings

    get_oauth_settings.cache_clear()
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    get_oauth_settings.cache_clear()


@pytest.fixture
def mcp_client(client, db_session):
    """TestClient with signing keys hydrated for the OAuth subsystem."""
    from app.core.mcp_oauth.keys import ensure_signing_key, reload_keys

    ensure_signing_key(db_session)
    reload_keys(db_session)
    return client


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_protected_resource_metadata(mcp_client):
    resp = mcp_client.get("/.well-known/oauth-protected-resource")
    assert resp.status_code == 200
    body = resp.json()
    assert body["resource"] == "http://test"
    assert body["authorization_servers"] == ["http://test"]
    assert "mcp:read" in body["scopes_supported"]
    assert "mcp:admin" in body["scopes_supported"]
    assert body["bearer_methods_supported"] == ["header"]


def test_authorization_server_metadata(mcp_client):
    resp = mcp_client.get("/.well-known/oauth-authorization-server")
    assert resp.status_code == 200
    body = resp.json()
    assert body["issuer"] == "http://test"
    assert body["authorization_endpoint"] == "http://test/oauth/authorize"
    assert body["token_endpoint"] == "http://test/oauth/token"
    assert body["registration_endpoint"] == "http://test/oauth/register"
    assert body["jwks_uri"] == "http://test/.well-known/jwks.json"
    assert "S256" in body["code_challenge_methods_supported"]
    assert "plain" not in body["code_challenge_methods_supported"]
    assert "authorization_code" in body["grant_types_supported"]
    assert "refresh_token" in body["grant_types_supported"]


def test_jwks_returns_current_key(mcp_client):
    resp = mcp_client.get("/.well-known/jwks.json")
    assert resp.status_code == 200
    keys = resp.json().get("keys", [])
    assert len(keys) >= 1
    key = keys[0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert key["use"] == "sig"
    assert key["n"] and key["e"] and key["kid"]


# ---------------------------------------------------------------------------
# Dynamic Client Registration
# ---------------------------------------------------------------------------


def test_register_public_client_for_loopback(mcp_client):
    resp = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "MCP Inspector",
            "redirect_uris": ["http://127.0.0.1:8765/cb"],
            "token_endpoint_auth_method": "none",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_id"]
    assert body["client_name"] == "MCP Inspector"
    # Public client → no client_secret in response.
    assert "client_secret" not in body
    assert body["token_endpoint_auth_method"] == "none"


def test_register_rejects_disallowed_redirect_uri(mcp_client):
    resp = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "Phisher",
            "redirect_uris": ["https://attacker.example/cb"],
            "token_endpoint_auth_method": "none",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "invalid_redirect_uri"


def test_register_rejects_javascript_uri(mcp_client):
    resp = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "Bad",
            "redirect_uris": ["javascript:alert(1)"],
            "token_endpoint_auth_method": "none",
        },
    )
    assert resp.status_code == 400


def test_register_confidential_client_returns_secret_once(mcp_client):
    resp = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "Confidential",
            "redirect_uris": ["https://claude.ai/cb"],
            "token_endpoint_auth_method": "client_secret_basic",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_secret"]
    assert body["client_secret_expires_at"] == 0


# ---------------------------------------------------------------------------
# /mcp behaves as a Resource Server: 401 + WWW-Authenticate when no token
# ---------------------------------------------------------------------------


def test_mcp_endpoint_requires_bearer(mcp_client):
    resp = mcp_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 401
    challenge = resp.headers.get("www-authenticate", "")
    assert challenge.startswith("Bearer ")
    assert 'realm="gcb-mcp"' in challenge
    # RFC 9728: 401 must carry a resource_metadata pointer so MCP
    # clients can find the AS without out-of-band knowledge.
    assert "/.well-known/oauth-protected-resource" in challenge


def test_mcp_endpoint_rejects_garbage_bearer(mcp_client):
    resp = mcp_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={
            "content-type": "application/json",
            "authorization": "Bearer not-a-real-token",
        },
    )
    assert resp.status_code == 401
    assert "invalid_token" in resp.headers.get("www-authenticate", "")


# ---------------------------------------------------------------------------
# Authorize entry-point sanity checks
# ---------------------------------------------------------------------------


def test_authorize_rejects_plain_pkce(mcp_client):
    # First register a client to authorize against.
    reg = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "x",
            "redirect_uris": ["https://claude.ai/cb"],
            "token_endpoint_auth_method": "none",
        },
    ).json()

    resp = mcp_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": reg["client_id"],
            "redirect_uri": "https://claude.ai/cb",
            "code_challenge": "abc",
            "code_challenge_method": "plain",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "invalid_request"


def test_authorize_rejects_unknown_client(mcp_client):
    resp = mcp_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": "does-not-exist",
            "redirect_uri": "https://claude.ai/cb",
            "code_challenge": "abc",
            "code_challenge_method": "S256",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "invalid_client"


def test_authorize_rejects_unregistered_redirect_uri(mcp_client):
    reg = mcp_client.post(
        "/oauth/register",
        json={
            "client_name": "x",
            "redirect_uris": ["https://claude.ai/cb"],
            "token_endpoint_auth_method": "none",
        },
    ).json()

    resp = mcp_client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": reg["client_id"],
            "redirect_uri": "https://other.example/cb",  # not registered
            "code_challenge": "abc",
            "code_challenge_method": "S256",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "invalid_redirect_uri"
