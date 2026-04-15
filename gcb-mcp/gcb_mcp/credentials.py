"""Resolve GCB dashboard credentials the same way gcb-runner does.

The runner stores the platform API key in ``~/.gcb-runner/config.json`` under
``platform.api_key``. The MCP server historically required a duplicate
``GCB_API_KEY`` environment variable, which caused confusing "missing key"
errors for users who had already run ``gcb-runner config``.

Resolution order:

1. ``GCB_API_KEY`` environment variable (if non-empty), so explicit MCP
   configuration still wins.
2. ``platform.api_key`` from ``~/.gcb-runner/config.json``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def resolve_gcb_api_key() -> str:
    """Return the X-API-Key value for GCB runner HTTP calls, or empty string."""
    env_key = os.environ.get("GCB_API_KEY", "").strip()
    if env_key:
        return env_key

    config_path = Path.home() / ".gcb-runner" / "config.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    platform = data.get("platform")
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
