"""Authenticated calls to GCB admin HTTP endpoints (same X-API-Key as runner)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from gcb_mcp.blog import _api_base, _headers

logger = logging.getLogger(__name__)


def _admin_url(path: str) -> str:
    base = _api_base().rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    return f"{base}/admin{p}"


def _error_response(resp: httpx.Response) -> dict[str, Any]:
    try:
        detail = resp.json()
    except Exception:
        detail = resp.text
    return {
        "error": "api_error",
        "status_code": resp.status_code,
        "detail": detail,
    }


async def preview_newsletter_html(post_id: str) -> dict[str, Any]:
    url = _admin_url("/newsletter/preview-html")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                url,
                headers=_headers(),
                params={"post_id": post_id},
            )
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def send_newsletter_campaign(post_id: str, dry_run: bool) -> dict[str, Any]:
    url = _admin_url("/newsletter/send")
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                url,
                headers=_headers(),
                json={
                    "post_id": post_id,
                    "dry_run": dry_run,
                    "audience": "test",
                    "confirm_production_send": False,
                    "force_resend": False,
                },
            )
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def send_newsletter_campaign_v2(
    *,
    post_id: str,
    dry_run: bool,
    audience: str = "test",
    confirm_production_send: bool = False,
    force_resend: bool = False,
    campaign_type: str = "newsletter",
) -> dict[str, Any]:
    url = _admin_url("/newsletter/send")
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                url,
                headers=_headers(),
                json={
                    "post_id": post_id,
                    "dry_run": dry_run,
                    "audience": audience,
                    "confirm_production_send": confirm_production_send,
                    "force_resend": force_resend,
                    "campaign_type": campaign_type,
                },
            )
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def list_newsletter_test_recipients(
    *,
    status: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    url = _admin_url("/newsletter/test-recipients")
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
    if search:
        params["search"] = search

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=_headers(), params=params)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)
    return resp.json()


async def create_newsletter_test_recipient(
    *,
    email: str,
    name: str | None = None,
    notes: str | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    url = _admin_url("/newsletter/test-recipients")
    payload: dict[str, Any] = {
        "email": email,
        "is_active": is_active,
    }
    if name is not None:
        payload["name"] = name
    if notes is not None:
        payload["notes"] = notes

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=_headers(), json=payload)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)
    return resp.json()


async def update_newsletter_test_recipient(
    *,
    recipient_id: str,
    email: str | None = None,
    name: str | None = None,
    notes: str | None = None,
    is_active: bool | None = None,
) -> dict[str, Any]:
    url = _admin_url(f"/newsletter/test-recipients/{recipient_id}")
    payload: dict[str, Any] = {}
    if email is not None:
        payload["email"] = email
    if name is not None:
        payload["name"] = name
    if notes is not None:
        payload["notes"] = notes
    if is_active is not None:
        payload["is_active"] = is_active

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.patch(url, headers=_headers(), json=payload)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)
    return resp.json()


async def delete_newsletter_test_recipient(*, recipient_id: str) -> dict[str, Any]:
    url = _admin_url(f"/newsletter/test-recipients/{recipient_id}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.delete(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)
    return resp.json()
