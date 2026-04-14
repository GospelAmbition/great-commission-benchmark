"""Async wrappers for the GCB /runner/blog/* API endpoints."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_API_BASE = "https://api.greatcommissionbenchmark.ai/api"


def _api_base() -> str:
    """Return the base URL for GCB runner API endpoints (ends in /api)."""
    env = os.environ.get("GCB_API_BASE_URL", "").strip().rstrip("/")
    if not env:
        return _DEFAULT_API_BASE
    # Redirect non-api domain to API subdomain
    if "api." not in env:
        env = env.replace("greatcommissionbenchmark.ai", "api.greatcommissionbenchmark.ai")
    if not env.endswith("/api"):
        env = f"{env}/api"
    return env


def _api_key() -> str:
    return os.environ.get("GCB_API_KEY", "").strip()


def _headers() -> dict[str, str]:
    return {
        "X-API-Key": _api_key(),
        "Content-Type": "application/json",
    }


def _blog_url(path: str) -> str:
    return f"{_api_base()}/runner/blog{path}"


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------


async def list_posts(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """List blog posts. status: 'draft' | 'published' | None (all)."""
    params: dict[str, Any] = {"limit": min(limit, 100), "offset": offset}
    if status:
        params["status"] = status

    url = _blog_url("/posts")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=_headers(), params=params)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def get_post(post_id: str) -> dict[str, Any]:
    """Fetch a single blog post by UUID, including full content."""
    url = _blog_url(f"/posts/{post_id}")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def create_post(
    title: str,
    content: str,
    excerpt: str | None = None,
    slug: str | None = None,
    featured_image_url: str | None = None,
    category_ids: list[str] | None = None,
    publish: bool = False,
) -> dict[str, Any]:
    """Create a blog post as draft (or publish immediately if publish=True)."""
    body: dict[str, Any] = {"title": title, "content": content}
    if excerpt:
        body["excerpt"] = excerpt
    if slug:
        body["slug"] = slug
    if featured_image_url:
        body["featured_image_url"] = featured_image_url
    if category_ids:
        body["category_ids"] = category_ids

    params = {"publish": "true"} if publish else {}
    url = _blog_url("/posts")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=_headers(), json=body, params=params)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def update_post(
    post_id: str,
    content: str | None = None,
    title: str | None = None,
    excerpt: str | None = None,
    featured_image_url: str | None = None,
    slug: str | None = None,
    category_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing blog post. Only supplied fields are changed."""
    body: dict[str, Any] = {}
    if content is not None:
        body["content"] = content
    if title is not None:
        body["title"] = title
    if excerpt is not None:
        body["excerpt"] = excerpt
    if featured_image_url is not None:
        body["featured_image_url"] = featured_image_url
    if slug is not None:
        body["slug"] = slug
    if category_ids is not None:
        body["category_ids"] = category_ids

    if not body:
        return {"error": "no_fields", "message": "No fields provided to update."}

    url = _blog_url(f"/posts/{post_id}")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.put(url, headers=_headers(), json=body)
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def publish_post(post_id: str) -> dict[str, Any]:
    """Publish a draft blog post."""
    url = _blog_url(f"/posts/{post_id}/publish")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def unpublish_post(post_id: str) -> dict[str, Any]:
    """Revert a published post to draft."""
    url = _blog_url(f"/posts/{post_id}/unpublish")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


async def delete_post(post_id: str) -> dict[str, Any]:
    """Delete a blog post permanently."""
    url = _blog_url(f"/posts/{post_id}")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.delete(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return {"deleted": True, "post_id": post_id}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


async def list_categories() -> dict[str, Any]:
    """List all blog categories."""
    url = _blog_url("/categories")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


# ---------------------------------------------------------------------------
# Image upload
# ---------------------------------------------------------------------------


async def upload_image(file_path: Path, content_type: str = "image/svg+xml") -> dict[str, Any]:
    """
    Upload an image (or SVG) to GCB storage.

    Returns: {url, filename, size, content_type}
    """
    if not _api_key():
        return {
            "error": "missing_api_key",
            "message": "GCB_API_KEY not set. Cannot upload image.",
        }

    if not file_path.exists():
        return {"error": "file_not_found", "message": str(file_path)}

    url = _blog_url("/upload-image")
    upload_headers = {"X-API-Key": _api_key()}  # no Content-Type — multipart sets it

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    url,
                    headers=upload_headers,
                    files={"file": (file_path.name, f, content_type)},
                )
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------


async def generate_slug(title: str) -> dict[str, Any]:
    """Generate and check uniqueness of a slug for the given title."""
    url = _blog_url("/generate-slug")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=_headers(), params={"title": title})
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def build_live_url(slug: str) -> str:
    """Return the public URL for a published blog post."""
    return f"https://greatcommissionbenchmark.ai/action/insights/{slug}"


# ---------------------------------------------------------------------------
# Remote test run export
# ---------------------------------------------------------------------------


async def fetch_remote_test_export(test_run_id: str) -> dict[str, Any]:
    """Fetch the full benchmark export JSON for any submitted test run.

    Calls GET /api/runner/test-runs/{test_run_id}/export — admin API key required.
    Returns the raw export payload (format_version, test_run, summary, responses).
    """
    if not _api_key():
        return {
            "error": "missing_api_key",
            "message": "GCB_API_KEY not set. Cannot retrieve remote test export.",
        }

    url = f"{_api_base()}/runner/test-runs/{test_run_id}/export"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url, headers=_headers())
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc)}

    if not resp.is_success:
        return _error_response(resp)

    return resp.json()
