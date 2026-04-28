"""OAuth 2.1 + OIDC endpoint handlers.

Mounted at ``/oauth/*`` from :mod:`main`. Each route is intentionally
short — the heavy lifting (PKCE verification, token issuance, key
material) lives in sibling modules so this file reads as a flow
checklist rather than a kitchen sink.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.core.mcp_oauth.config import get_oauth_settings
from app.core.mcp_oauth.consent import render_consent_html
from app.core.mcp_oauth.google import (
    begin_google_oidc,
    complete_google_oidc,
    find_or_create_user_from_google_claims,
)
from app.core.mcp_oauth.jwt import (
    generate_refresh_token,
    hash_authorization_code,
    hash_client_secret,
    hash_refresh_token,
    issue_access_token,
)
from app.core.mcp_oauth.models import (
    OAuthASSession,
    OAuthAuthorizationCode,
    OAuthClient,
    OAuthPendingSession,
    OAuthRefreshToken,
    OAuthTokenAudit,
)
from app.core.mcp_oauth.pkce import PKCEError, assert_supported_method, verify_s256
from app.core.mcp_oauth.scopes import (
    format_scope_string,
    grant_scopes,
    parse_scope_string,
    user_permitted_scopes,
)
from app.db.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oauth", tags=["oauth"])

# Cookies
_AS_COOKIE = "gcb_mcp_sid"
_PENDING_COOKIE = "gcb_mcp_pending"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _sign_csrf(session_id: str) -> str:
    secret = (get_oauth_settings().OAUTH_SESSION_COOKIE_SECRET or "").encode()
    if not secret:
        # Falls back to an instance-derived value so missing config
        # produces a clear runtime error instead of silent disabling.
        raise HTTPException(500, "OAUTH_SESSION_COOKIE_SECRET not configured")
    return hmac.new(secret, session_id.encode(), hashlib.sha256).hexdigest()


def _verify_csrf(session_id: str, token: str) -> bool:
    return hmac.compare_digest(_sign_csrf(session_id), token)


def _redirect_uri_allowed(uri: str, allowed_hosts: List[str]) -> bool:
    """Allow registered hosts and loopback only."""
    try:
        parsed = urlparse(uri)
    except Exception:
        return False
    if parsed.scheme == "http":
        host = (parsed.hostname or "").lower()
        return host in {"127.0.0.1", "localhost", "::1"}
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if host in allowed_hosts:
        return True
    # Allow exact subdomains of an allowed host (claude.ai → app.claude.ai)
    return any(host.endswith(f".{base}") for base in allowed_hosts)


def _client_or_400(db: Session, client_id: str) -> OAuthClient:
    client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    if not client or not client.is_approved:
        raise HTTPException(400, {"error": "invalid_client"})
    return client


# ---------------------------------------------------------------------------
# Dynamic Client Registration (RFC 7591)
# ---------------------------------------------------------------------------


@router.post("/register")
async def register_client(request: Request, db: Session = Depends(get_db)) -> dict:
    settings_ = get_oauth_settings()
    if not settings_.MCP_ANONYMOUS_DCR_ENABLED:
        raise HTTPException(403, {"error": "registration_disabled"})

    body = await request.json()
    client_name = (body.get("client_name") or "Unnamed MCP Client").strip()[:255]
    redirect_uris = body.get("redirect_uris") or []
    if not isinstance(redirect_uris, list) or not redirect_uris:
        raise HTTPException(400, {"error": "invalid_redirect_uri"})

    allowed_hosts = settings_.allowed_redirect_uri_hosts
    for uri in redirect_uris:
        if not isinstance(uri, str) or not _redirect_uri_allowed(uri, allowed_hosts):
            raise HTTPException(400, {"error": "invalid_redirect_uri", "detail": uri})

    grant_types = body.get("grant_types") or ["authorization_code", "refresh_token"]
    response_types = body.get("response_types") or ["code"]
    auth_method = (body.get("token_endpoint_auth_method") or "none").strip()
    if auth_method not in {"none", "client_secret_basic", "client_secret_post"}:
        raise HTTPException(400, {"error": "invalid_token_endpoint_auth_method"})

    client_id = secrets.token_urlsafe(24)
    secret_plain: Optional[str] = None
    secret_hash: Optional[str] = None
    if auth_method != "none":
        secret_plain = secrets.token_urlsafe(40)
        secret_hash = hash_client_secret(secret_plain)

    row = OAuthClient(
        client_id=client_id,
        client_secret_hash=secret_hash,
        client_name=client_name,
        redirect_uris=list(redirect_uris),
        grant_types=list(grant_types),
        response_types=list(response_types),
        token_endpoint_auth_method=auth_method,
        scope=body.get("scope"),
        software_id=body.get("software_id"),
        software_version=body.get("software_version"),
        client_uri=body.get("client_uri"),
        registered_by_ip=request.client.host if request.client else None,
    )
    db.add(row)
    db.commit()

    response: dict = {
        "client_id": client_id,
        "client_name": client_name,
        "redirect_uris": list(redirect_uris),
        "grant_types": list(grant_types),
        "response_types": list(response_types),
        "token_endpoint_auth_method": auth_method,
        "client_id_issued_at": int(_now().timestamp()),
    }
    if secret_plain:
        response["client_secret"] = secret_plain
        response["client_secret_expires_at"] = 0  # never
    if row.scope:
        response["scope"] = row.scope
    return response


# ---------------------------------------------------------------------------
# Authorize (PKCE + Google federation + consent)
# ---------------------------------------------------------------------------


@router.get("/authorize")
async def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str = "plain",
    scope: Optional[str] = None,
    state: Optional[str] = None,
    resource: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Response:
    if response_type != "code":
        raise HTTPException(400, {"error": "unsupported_response_type"})
    try:
        assert_supported_method(code_challenge_method)
    except PKCEError as exc:
        raise HTTPException(400, {"error": "invalid_request", "detail": str(exc)})

    client = _client_or_400(db, client_id)
    if redirect_uri not in (client.redirect_uris or []):
        # Strict exact-match (open-redirect prevention).
        raise HTTPException(400, {"error": "invalid_redirect_uri"})

    requested_scopes = parse_scope_string(scope)

    # Reuse the AS browser session if it is still valid.
    sid = request.cookies.get(_AS_COOKIE)
    user: Optional[User] = None
    if sid:
        as_session = (
            db.query(OAuthASSession)
            .filter(
                OAuthASSession.session_id == sid,
                OAuthASSession.expires_at > _now(),
            )
            .first()
        )
        if as_session is not None:
            user = db.query(User).filter(User.id == as_session.user_id).first()

    if user is None:
        # Fresh login: bounce to Google.
        return _redirect_to_google(
            db=db,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=" ".join(requested_scopes),
            state=state or "",
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            resource=resource,
        )

    # Authenticated already: render consent immediately.
    granted = grant_scopes(requested_scopes, user)
    pending_id = _create_pending_for_consent(
        db=db,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=" ".join(granted),
        state=state or "",
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        resource=resource,
    )
    return HTMLResponse(
        render_consent_html(
            client_name=client.client_name,
            granted_scopes=granted,
            user_email=user.email or "",
            pending_session_id=pending_id,
            csrf_token=_sign_csrf(pending_id),
        )
    )


def _redirect_to_google(
    *,
    db: Session,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str,
    resource: Optional[str],
) -> Response:
    settings_ = get_oauth_settings()
    start = begin_google_oidc()
    session_id = secrets.token_urlsafe(32)
    db.add(
        OAuthPendingSession(
            session_id=session_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            resource=resource,
            google_state=start.state,
            google_nonce=start.nonce,
            google_pkce_verifier=start.code_verifier,
            expires_at=_now()
            + timedelta(seconds=settings_.OAUTH_PENDING_SESSION_TTL_SECONDS),
        )
    )
    db.commit()

    response = RedirectResponse(start.authorize_url, status_code=302)
    response.set_cookie(
        _PENDING_COOKIE,
        session_id,
        max_age=settings_.OAUTH_PENDING_SESSION_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/oauth",
    )
    return response


def _create_pending_for_consent(
    *,
    db: Session,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str,
    resource: Optional[str],
) -> str:
    """Create a pending session that already has the user but awaits consent."""
    settings_ = get_oauth_settings()
    session_id = secrets.token_urlsafe(32)
    db.add(
        OAuthPendingSession(
            session_id=session_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            resource=resource,
            google_state="",
            google_nonce="",
            google_pkce_verifier="",
            expires_at=_now()
            + timedelta(seconds=settings_.OAUTH_PENDING_SESSION_TTL_SECONDS),
        )
    )
    db.commit()
    return session_id


# ---------------------------------------------------------------------------
# Google OIDC callback
# ---------------------------------------------------------------------------


@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
) -> Response:
    settings_ = get_oauth_settings()
    pending_cookie = request.cookies.get(_PENDING_COOKIE)
    if not pending_cookie:
        raise HTTPException(400, {"error": "missing_pending_session"})
    pending = (
        db.query(OAuthPendingSession)
        .filter(
            OAuthPendingSession.session_id == pending_cookie,
            OAuthPendingSession.expires_at > _now(),
        )
        .first()
    )
    if pending is None or pending.google_state != state:
        raise HTTPException(400, {"error": "state_mismatch"})

    identity = await complete_google_oidc(
        code=code,
        code_verifier=pending.google_pkce_verifier,
        expected_nonce=pending.google_nonce,
    )
    user = find_or_create_user_from_google_claims(db, identity)

    # Issue/refresh the AS browser session cookie.
    as_sid = secrets.token_urlsafe(32)
    db.add(
        OAuthASSession(
            session_id=as_sid,
            user_id=user.id,
            expires_at=_now() + timedelta(seconds=settings_.OAUTH_AS_SESSION_TTL_SECONDS),
        )
    )

    # Lock the granted scopes now that we know the user.
    requested_scopes = parse_scope_string(pending.scope)
    granted = grant_scopes(requested_scopes, user)
    pending.scope = format_scope_string(granted)
    db.commit()

    client = _client_or_400(db, pending.client_id)
    response = HTMLResponse(
        render_consent_html(
            client_name=client.client_name,
            granted_scopes=granted,
            user_email=user.email or "",
            pending_session_id=pending.session_id,
            csrf_token=_sign_csrf(pending.session_id),
        )
    )
    response.set_cookie(
        _AS_COOKIE,
        as_sid,
        max_age=settings_.OAUTH_AS_SESSION_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(_PENDING_COOKIE, path="/oauth")
    return response


# ---------------------------------------------------------------------------
# Consent submission
# ---------------------------------------------------------------------------


@router.post("/authorize/consent")
async def authorize_consent(
    request: Request,
    session_id: str = Form(...),
    csrf_token: str = Form(...),
    action: str = Form(...),
    db: Session = Depends(get_db),
) -> Response:
    if not _verify_csrf(session_id, csrf_token):
        raise HTTPException(400, {"error": "csrf_invalid"})
    pending = (
        db.query(OAuthPendingSession)
        .filter(
            OAuthPendingSession.session_id == session_id,
            OAuthPendingSession.expires_at > _now(),
        )
        .first()
    )
    if pending is None:
        raise HTTPException(400, {"error": "expired_pending_session"})

    sid = request.cookies.get(_AS_COOKIE)
    as_session = (
        db.query(OAuthASSession)
        .filter(
            OAuthASSession.session_id == sid,
            OAuthASSession.expires_at > _now(),
        )
        .first()
        if sid
        else None
    )
    if as_session is None:
        raise HTTPException(400, {"error": "no_user_session"})

    redirect_to = pending.redirect_uri
    if action != "approve":
        # Cancel: redirect back with error.
        params = {"error": "access_denied"}
        if pending.state:
            params["state"] = pending.state
        db.delete(pending)
        db.commit()
        return RedirectResponse(f"{redirect_to}?{urlencode(params)}", status_code=302)

    settings_ = get_oauth_settings()
    code = secrets.token_urlsafe(32)
    db.add(
        OAuthAuthorizationCode(
            code_hash=hash_authorization_code(code),
            client_id=pending.client_id,
            user_id=as_session.user_id,
            redirect_uri=pending.redirect_uri,
            scope=pending.scope,
            code_challenge=pending.code_challenge,
            code_challenge_method=pending.code_challenge_method,
            resource=pending.resource,
            expires_at=_now()
            + timedelta(seconds=settings_.OAUTH_AUTHORIZATION_CODE_TTL_SECONDS),
        )
    )
    db.delete(pending)
    db.commit()

    params = {"code": code}
    if pending.state:
        params["state"] = pending.state
    return RedirectResponse(f"{redirect_to}?{urlencode(params)}", status_code=302)


# ---------------------------------------------------------------------------
# Token (authorization_code + refresh_token)
# ---------------------------------------------------------------------------


@router.post("/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    resource: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    settings_ = get_oauth_settings()

    # Resolve client (basic auth header or form fields).
    auth_header = request.headers.get("authorization", "")
    basic_id, basic_secret = _parse_basic_auth(auth_header)
    cid = client_id or basic_id
    csec = client_secret or basic_secret
    if not cid:
        return _token_error("invalid_client", 401)
    client = (
        db.query(OAuthClient).filter(OAuthClient.client_id == cid).first()
    )
    if client is None or not client.is_approved:
        return _token_error("invalid_client", 401)
    if client.token_endpoint_auth_method != "none":
        if not csec or hash_client_secret(csec) != client.client_secret_hash:
            return _token_error("invalid_client", 401)

    if grant_type == "authorization_code":
        return await _grant_authorization_code(
            db=db,
            client=client,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            resource=resource,
        )
    if grant_type == "refresh_token":
        return await _grant_refresh_token(
            db=db,
            client=client,
            refresh_token=refresh_token,
            requested_scope=scope,
        )
    return _token_error("unsupported_grant_type", 400)


def _token_error(code: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse({"error": code}, status_code=status_code)


def _parse_basic_auth(header: str) -> tuple[Optional[str], Optional[str]]:
    import base64

    if not header.lower().startswith("basic "):
        return None, None
    try:
        raw = base64.b64decode(header.split(None, 1)[1]).decode("utf-8")
    except Exception:
        return None, None
    if ":" not in raw:
        return None, None
    cid, csec = raw.split(":", 1)
    return cid, csec


async def _grant_authorization_code(
    *,
    db: Session,
    client: OAuthClient,
    code: Optional[str],
    redirect_uri: Optional[str],
    code_verifier: Optional[str],
    resource: Optional[str],
) -> JSONResponse:
    if not code or not redirect_uri or not code_verifier:
        return _token_error("invalid_request")
    code_row = (
        db.query(OAuthAuthorizationCode)
        .filter(OAuthAuthorizationCode.code_hash == hash_authorization_code(code))
        .first()
    )
    if code_row is None:
        return _token_error("invalid_grant")
    if code_row.consumed_at is not None:
        # Replay: revoke entire family of refresh tokens issued from this code
        _revoke_refresh_chain_by_code(db, code_row.code_hash)
        return _token_error("invalid_grant")
    if code_row.expires_at <= _now():
        return _token_error("invalid_grant")
    if code_row.client_id != client.client_id:
        return _token_error("invalid_grant")
    if code_row.redirect_uri != redirect_uri:
        return _token_error("invalid_grant")
    if not verify_s256(code_verifier, code_row.code_challenge):
        return _token_error("invalid_grant")
    if resource and code_row.resource and resource != code_row.resource:
        return _token_error("invalid_target")

    # Mark code consumed.
    code_row.consumed_at = _now()
    db.commit()

    user = db.query(User).filter(User.id == code_row.user_id).first()
    if user is None:
        return _token_error("invalid_grant")

    return _issue_token_pair(
        db=db,
        client=client,
        user=user,
        scopes=code_row.scope.split(),
        resource=code_row.resource,
        parent_refresh_hash=None,
    )


def _revoke_refresh_chain_by_code(db: Session, code_hash: str) -> None:
    """Revoke any refresh token issued from a now-replayed authorization code.

    Conservative best-effort: we don't track the link directly, so we
    simply revoke all non-revoked refresh tokens for the same user/
    client. This trips on rare false positives but is the standard
    detection-and-mitigation for code replay (RFC 6819 §5.2.1.1).
    """
    code_row = (
        db.query(OAuthAuthorizationCode)
        .filter(OAuthAuthorizationCode.code_hash == code_hash)
        .first()
    )
    if code_row is None:
        return
    rows = (
        db.query(OAuthRefreshToken)
        .filter(
            OAuthRefreshToken.client_id == code_row.client_id,
            OAuthRefreshToken.user_id == code_row.user_id,
            OAuthRefreshToken.revoked_at.is_(None),
        )
        .all()
    )
    now = _now()
    for r in rows:
        r.revoked_at = now
    db.commit()


async def _grant_refresh_token(
    *,
    db: Session,
    client: OAuthClient,
    refresh_token: Optional[str],
    requested_scope: Optional[str],
) -> JSONResponse:
    if not refresh_token:
        return _token_error("invalid_request")
    token_hash = hash_refresh_token(refresh_token)
    row = (
        db.query(OAuthRefreshToken)
        .filter(OAuthRefreshToken.token_hash == token_hash)
        .first()
    )
    if row is None:
        return _token_error("invalid_grant")
    if row.client_id != client.client_id:
        return _token_error("invalid_grant")
    if row.expires_at <= _now():
        return _token_error("invalid_grant")
    if row.revoked_at is not None:
        # Replay of a rotated token — revoke the whole chain.
        _revoke_refresh_chain(db, row)
        return _token_error("invalid_grant")

    user = db.query(User).filter(User.id == row.user_id).first()
    if user is None:
        return _token_error("invalid_grant")

    # Optional scope down-narrowing: requested ⊆ original.
    original_scopes = set(row.scope.split())
    if requested_scope:
        requested = set(parse_scope_string(requested_scope))
        if not requested.issubset(original_scopes):
            return _token_error("invalid_scope")
        granted_scopes = sorted(requested | {"mcp:read"})
    else:
        granted_scopes = sorted(original_scopes)

    # Re-check user permissions in case admin revoked flags since issue.
    permitted = user_permitted_scopes(user)
    granted_scopes = [s for s in granted_scopes if s in permitted]

    # Rotate: revoke this token, issue new pair.
    row.revoked_at = _now()
    db.commit()
    return _issue_token_pair(
        db=db,
        client=client,
        user=user,
        scopes=granted_scopes,
        resource=None,
        parent_refresh_hash=row.token_hash,
    )


def _revoke_refresh_chain(db: Session, token_row: OAuthRefreshToken) -> None:
    """Revoke a refresh token and every descendant in its rotation chain."""
    visited: set[str] = set()
    queue: List[str] = [token_row.token_hash]
    now = _now()
    while queue:
        h = queue.pop()
        if h in visited:
            continue
        visited.add(h)
        row = (
            db.query(OAuthRefreshToken)
            .filter(OAuthRefreshToken.token_hash == h)
            .first()
        )
        if row is None:
            continue
        if row.revoked_at is None:
            row.revoked_at = now
        if row.replaced_by:
            queue.append(row.replaced_by)
    db.commit()


def _issue_token_pair(
    *,
    db: Session,
    client: OAuthClient,
    user: User,
    scopes: List[str],
    resource: Optional[str],
    parent_refresh_hash: Optional[str],
) -> JSONResponse:
    settings_ = get_oauth_settings()
    access_token, claims = issue_access_token(
        db=db,
        user_id=str(user.id),
        user_email=user.email or "",
        client_id=client.client_id,
        scopes=scopes,
        resource=resource,
    )
    refresh_plain, refresh_hash = generate_refresh_token()
    db.add(
        OAuthRefreshToken(
            token_hash=refresh_hash,
            client_id=client.client_id,
            user_id=user.id,
            scope=" ".join(scopes),
            parent_token_hash=parent_refresh_hash,
            expires_at=_now()
            + timedelta(seconds=settings_.OAUTH_REFRESH_TOKEN_TTL_SECONDS),
        )
    )
    if parent_refresh_hash:
        parent = (
            db.query(OAuthRefreshToken)
            .filter(OAuthRefreshToken.token_hash == parent_refresh_hash)
            .first()
        )
        if parent is not None:
            parent.replaced_by = refresh_hash
    client.last_used_at = _now()
    db.commit()

    return JSONResponse(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings_.OAUTH_ACCESS_TOKEN_TTL_SECONDS,
            "refresh_token": refresh_plain,
            "scope": " ".join(scopes),
        }
    )


# ---------------------------------------------------------------------------
# Revocation (RFC 7009)
# ---------------------------------------------------------------------------


@router.post("/revoke")
async def revoke_token(
    request: Request,
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> Response:
    auth_header = request.headers.get("authorization", "")
    basic_id, _ = _parse_basic_auth(auth_header)
    cid = client_id or basic_id
    if not cid:
        # RFC 7009 §2.2: invalid token requests return 200.
        return Response(status_code=200)

    # Try refresh first, then access token jti.
    rh = hash_refresh_token(token)
    refresh_row = (
        db.query(OAuthRefreshToken)
        .filter(
            OAuthRefreshToken.token_hash == rh,
            OAuthRefreshToken.client_id == cid,
        )
        .first()
    )
    if refresh_row is not None and refresh_row.revoked_at is None:
        refresh_row.revoked_at = _now()
        db.commit()
        return Response(status_code=200)

    # Access token: parse JTI from the raw JWT and revoke by jti.
    try:
        from jose import jwt as jose_jwt

        unverified = jose_jwt.get_unverified_claims(token)
        jti = unverified.get("jti")
    except Exception:
        jti = None
    if jti:
        audit = (
            db.query(OAuthTokenAudit)
            .filter(OAuthTokenAudit.jti == jti)
            .first()
        )
        if audit is not None and audit.revoked_at is None:
            audit.revoked_at = _now()
            db.commit()
    return Response(status_code=200)
