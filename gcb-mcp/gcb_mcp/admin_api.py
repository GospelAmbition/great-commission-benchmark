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
                json={"post_id": post_id, "dry_run": dry_run},
            )
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()
