"""Resolve GCB dashboard credentials the same way gcb-runner does.

The runner stores the platform API key and URL in ``~/.gcb-runner/config.json``
under ``platform.api_key`` and ``platform.url``. The MCP server historically
required duplicate env vars (``GCB_API_KEY``, ``GCB_API_BASE_URL``), which caused
confusing errors for users who had already run ``gcb-runner config``.

API key resolution order:

1. Active :class:`gcb_mcp.context.RequestContext` (per-request override).
2. ``GCB_API_KEY`` environment variable.
3. ``platform.api_key`` from ``~/.gcb-runner/config.json``.

API base URL resolution order:

1. Active :class:`gcb_mcp.context.RequestContext` ``api_base_url``.
2. ``GCB_API_BASE_URL`` environment variable.
3. ``platform.url`` from ``~/.gcb-runner/config.json``.
4. ``https://api.greatcommissionbenchmark.ai`` (public API host).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_GCB_API_BASE_URL = "https://api.greatcommissionbenchmark.ai"


def _read_runner_config() -> dict:
    """Load ~/.gcb-runner/config.json, returning {} on missing or invalid data."""
    config_path = Path.home() / ".gcb-runner" / "config.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_api_base_url(url: str) -> str:
    """Normalize a platform base URL for runner API calls (no ``/api`` suffix)."""
    normalized = url.strip().rstrip("/")
    if not normalized:
        return ""
    # Redirect non-api domain to API subdomain (matches blog.py / public_api.py).
    if "api." not in normalized:
        normalized = normalized.replace(
            "greatcommissionbenchmark.ai", "api.greatcommissionbenchmark.ai"
        )
    # platform.url is host-only; strip a trailing /api if present.
    if normalized.endswith("/api"):
        normalized = normalized[:-4]
    return normalized


def resolve_gcb_api_base_url() -> str:
    """Return the GCB platform base URL for runner HTTP calls (no trailing slash).

    Resolution order:
      1. Active :class:`gcb_mcp.context.RequestContext` ``api_base_url``.
      2. ``GCB_API_BASE_URL`` environment variable.
      3. ``platform.url`` from ``~/.gcb-runner/config.json``.
      4. :data:`DEFAULT_GCB_API_BASE_URL`.
    """
    try:
        from gcb_mcp.context import current as _current_ctx
    except Exception:  # pragma: no cover - defensive
        _current_ctx = None  # type: ignore[assignment]

    if _current_ctx is not None:
        ctx_url = _normalize_api_base_url(_current_ctx().api_base_url)
        if ctx_url:
            return ctx_url

    env_url = _normalize_api_base_url(os.environ.get("GCB_API_BASE_URL", ""))
    if env_url:
        return env_url

    platform = _read_runner_config().get("platform")
    if isinstance(platform, dict):
        config_url = _normalize_api_base_url(str(platform.get("url") or ""))
        if config_url:
            return config_url

    return DEFAULT_GCB_API_BASE_URL


def resolve_gcb_api_key() -> str:
    """Return the X-API-Key value for GCB runner HTTP calls, or empty string.

    Resolution order:
      1. Active :class:`gcb_mcp.context.RequestContext` (set by the
         OAuth-fronted HTTP server per request).
      2. ``GCB_API_KEY`` environment variable.
      3. ``platform.api_key`` from ``~/.gcb-runner/config.json``.
    """
    # Local import keeps the credentials module importable even if the
    # context module is unavailable during package bootstrap.
    try:
        from gcb_mcp.context import current as _current_ctx
    except Exception:  # pragma: no cover - defensive
        _current_ctx = None  # type: ignore[assignment]

    if _current_ctx is not None:
        ctx_key = _current_ctx().api_key.strip()
        if ctx_key:
            return ctx_key

    env_key = os.environ.get("GCB_API_KEY", "").strip()
    if env_key:
        return env_key

    platform = _read_runner_config().get("platform")
    if not isinstance(platform, dict):
        return ""

    return str(platform.get("api_key") or "").strip()


def missing_gcb_api_key_message() -> str:
    """Human-readable hint when no key is available."""
    return (
        "No GCB API key found. Either set environment variable GCB_API_KEY to your "
        "dashboard API key, or run `gcb-runner config` and save "
        "`platform.api_key` in ~/.gcb-runner/config.json (same key the CLI uses "
        "for uploads). Admin or benchmark-editor permission is required."
    )
