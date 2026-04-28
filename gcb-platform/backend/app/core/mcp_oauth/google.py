"""Google OIDC federation for the MCP Authorization Server.

The MCP AS does not own user credentials. It bounces the user to Google
for authentication, verifies the returned ``id_token``, then maps the
Google ``sub`` claim onto a row in the existing ``users`` table —
auto-provisioning if necessary, exactly like
:func:`app.core.auth.get_current_user` does for the NextAuth path.

Reusing the existing GOOGLE_CLIENT_ID/SECRET means no new Google
client; only a new redirect URI is registered in Google Cloud Console:

    {MCP_ISSUER_URL}/oauth/callback/google
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.core.mcp_oauth.config import get_oauth_settings
from app.db.models.user import User

logger = logging.getLogger(__name__)

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"


@dataclass(frozen=True)
class GoogleAuthStart:
    """Ephemeral state needed to validate the callback."""

    authorize_url: str
    state: str
    nonce: str
    code_verifier: str


def begin_google_oidc() -> GoogleAuthStart:
    """Return the URL to redirect the user to + state to persist."""
    settings_ = get_oauth_settings()
    if not settings_.GOOGLE_CLIENT_ID:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("ascii")).digest()
        )
        .rstrip(b"=")
        .decode("ascii")
    )
    params = {
        "client_id": settings_.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": settings_.google_callback_url,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "online",
        "prompt": "select_account",
    }
    return GoogleAuthStart(
        authorize_url=f"{GOOGLE_AUTHORIZE_URL}?{urlencode(params)}",
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
    )


@dataclass(frozen=True)
class GoogleIdentity:
    sub: str
    email: str
    name: str
    email_verified: bool


async def complete_google_oidc(
    *, code: str, code_verifier: str, expected_nonce: str
) -> GoogleIdentity:
    """Exchange ``code`` for tokens and verify the ``id_token``."""
    settings_ = get_oauth_settings()
    if not settings_.GOOGLE_CLIENT_ID or not settings_.GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Google client credentials are not configured")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings_.GOOGLE_CLIENT_ID,
                "client_secret": settings_.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings_.google_callback_url,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            },
            headers={"Accept": "application/json"},
        )
    if resp.status_code != 200:
        logger.warning("Google token exchange failed: %s %s", resp.status_code, resp.text)
        raise RuntimeError("google_token_exchange_failed")

    body = resp.json()
    id_token = body.get("id_token")
    if not id_token:
        raise RuntimeError("google_no_id_token")
    return await _verify_id_token(id_token, expected_nonce=expected_nonce)


async def _verify_id_token(id_token: str, *, expected_nonce: str) -> GoogleIdentity:
    """Verify Google's ID token signature, audience, issuer, and nonce.

    We fetch Google's JWKS lazily; ``python-jose`` handles RS256
    verification for us. A future optimisation could cache the JWKS in
    process memory keyed on the ``Cache-Control`` header.
    """
    from jose import jwt as jose_jwt
    from jose.utils import base64url_decode  # noqa: F401  (forces lazy import)

    settings_ = get_oauth_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        jwks_resp = await client.get(GOOGLE_JWKS_URL)
    jwks_resp.raise_for_status()
    jwks = jwks_resp.json()

    headers = jose_jwt.get_unverified_header(id_token)
    kid = headers.get("kid")
    matching = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if matching is None:
        raise RuntimeError("google_unknown_kid")

    payload = jose_jwt.decode(
        id_token,
        matching,
        algorithms=["RS256"],
        audience=settings_.GOOGLE_CLIENT_ID,
        issuer=("https://accounts.google.com", "accounts.google.com"),
    )

    if expected_nonce and payload.get("nonce") != expected_nonce:
        raise RuntimeError("google_nonce_mismatch")

    return GoogleIdentity(
        sub=str(payload.get("sub")),
        email=str(payload.get("email") or ""),
        name=str(payload.get("name") or ""),
        email_verified=bool(payload.get("email_verified", False)),
    )


def find_or_create_user_from_google_claims(
    db: Session, identity: GoogleIdentity
) -> User:
    """Mirror the auto-provisioning behaviour of NextAuth's path.

    Looks up by ``users.auth0_id == google.sub`` (the platform's existing
    convention; the column was named pre-NextAuth-migration) and inserts
    a new row with all permission flags ``False`` if missing.
    """
    user = db.query(User).filter(User.auth0_id == identity.sub).first()
    if user is not None:
        # Refresh email/name in case the user changed them at Google.
        changed = False
        if identity.email and user.email != identity.email:
            user.email = identity.email
            changed = True
        if identity.name and user.name != identity.name:
            user.name = identity.name
            changed = True
        if changed:
            db.commit()
        return user

    user = User(
        auth0_id=identity.sub,
        email=identity.email,
        name=identity.name,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Auto-provisioned MCP user %s via Google OIDC", user.id)
    return user
