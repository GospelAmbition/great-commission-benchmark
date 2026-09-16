"""Tests for GCB credential and API base URL resolution."""

from __future__ import annotations

import json

from gcb_mcp.context import RequestContext, scope
from gcb_mcp.credentials import (
    DEFAULT_GCB_API_BASE_URL,
    resolve_gcb_api_base_url,
    resolve_gcb_api_key,
)
import gcb_mcp.server as server


def test_resolve_gcb_api_base_url_defaults_without_config(monkeypatch) -> None:
    monkeypatch.delenv("GCB_API_BASE_URL", raising=False)
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {},
    )

    assert resolve_gcb_api_base_url() == DEFAULT_GCB_API_BASE_URL


def test_resolve_gcb_api_base_url_uses_runner_config(monkeypatch) -> None:
    monkeypatch.delenv("GCB_API_BASE_URL", raising=False)
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {
            "platform": {
                "url": "https://gcb-platform.up.railway.app",
                "api_key": "runner-key",
            }
        },
    )

    assert resolve_gcb_api_base_url() == "https://gcb-platform.up.railway.app"


def test_resolve_gcb_api_base_url_env_overrides_runner_config(monkeypatch) -> None:
    monkeypatch.setenv("GCB_API_BASE_URL", "https://env.example.com")
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {"platform": {"url": "https://config.example.com"}},
    )

    assert resolve_gcb_api_base_url() == "https://env.example.com"


def test_resolve_gcb_api_base_url_context_overrides_env(monkeypatch) -> None:
    monkeypatch.setenv("GCB_API_BASE_URL", "https://env.example.com")
    ctx = RequestContext(api_base_url="https://ctx.example.com")

    with scope(ctx):
        assert resolve_gcb_api_base_url() == "https://ctx.example.com"


def test_resolve_gcb_api_base_url_rewrites_frontend_domain(monkeypatch) -> None:
    monkeypatch.delenv("GCB_API_BASE_URL", raising=False)
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {"platform": {"url": "https://greatcommissionbenchmark.ai"}},
    )

    assert resolve_gcb_api_base_url() == "https://api.greatcommissionbenchmark.ai"


def test_resolve_gcb_api_base_url_strips_trailing_api_suffix(monkeypatch) -> None:
    monkeypatch.setenv("GCB_API_BASE_URL", "https://api.example.com/api/")

    assert resolve_gcb_api_base_url() == "https://api.example.com"


def test_resolve_gcb_api_key_uses_runner_config(monkeypatch) -> None:
    monkeypatch.delenv("GCB_API_KEY", raising=False)
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {"platform": {"api_key": "runner-key"}},
    )

    assert resolve_gcb_api_key() == "runner-key"


def test_server_base_url_uses_runner_config(monkeypatch) -> None:
    monkeypatch.delenv("GCB_API_BASE_URL", raising=False)
    monkeypatch.setattr(
        "gcb_mcp.credentials._read_runner_config",
        lambda: {
            "platform": {
                "url": "https://gcb-platform.up.railway.app",
                "api_key": "runner-key",
            }
        },
    )

    assert server._base_url() == "https://gcb-platform.up.railway.app"


def test_resolve_gcb_api_base_url_reads_real_runner_config(tmp_path, monkeypatch) -> None:
    config_dir = tmp_path / ".gcb-runner"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "platform": {
                    "url": "https://railway.example.com",
                    "api_key": "secret-key",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("gcb_mcp.credentials.Path.home", lambda: tmp_path)
    monkeypatch.delenv("GCB_API_BASE_URL", raising=False)

    assert resolve_gcb_api_base_url() == "https://railway.example.com"
    assert resolve_gcb_api_key() == "secret-key"
