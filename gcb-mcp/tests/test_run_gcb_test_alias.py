"""Tests for the natural-language GCB test alias."""

from __future__ import annotations

import asyncio

from gcb_mcp.context import required_scopes
import gcb_mcp.server as server


def test_run_gcb_test_requires_write_scope() -> None:
    assert required_scopes("run_gcb_test") == ("mcp:write",)


def test_run_gcb_test_starts_when_openrouter_ready(monkeypatch) -> None:
    async def fake_ready(auto_launch: bool = True) -> dict:
        assert auto_launch is True
        return {
            "ready": True,
            "openrouter": {"ready": True},
            "gcb_api": {"ready": True},
            "judge_backend": "openrouter",
            "judge_model": "openai/gpt-oss-20b",
        }

    async def fake_start(model_id: str) -> dict:
        assert model_id == "microsoft/wizardlm-2-8x22b"
        return {
            "job_id": "job-1",
            "model_id": model_id,
            "status": "running",
            "log_path": "/tmp/job-1.log",
        }

    monkeypatch.setattr(server, "check_ready_for_testing", fake_ready)
    monkeypatch.setattr(server, "start_gcb_test", fake_start)

    result = asyncio.run(server.run_gcb_test("microsoft/wizardlm-2-8x22b"))

    assert result["job_id"] == "job-1"
    assert result["status"] == "running"
    assert result["model_id"] == "microsoft/wizardlm-2-8x22b"
    assert result["log_path"] == "/tmp/job-1.log"
    assert "warning" not in result


def test_run_gcb_test_blocks_when_openrouter_not_ready(monkeypatch) -> None:
    started = False

    async def fake_ready(auto_launch: bool = True) -> dict:
        return {
            "ready": False,
            "openrouter": {"ready": False, "error": "missing key"},
            "gcb_api": {"ready": True},
        }

    async def fake_start(_model_id: str) -> dict:
        nonlocal started
        started = True
        return {}

    monkeypatch.setattr(server, "check_ready_for_testing", fake_ready)
    monkeypatch.setattr(server, "start_gcb_test", fake_start)

    result = asyncio.run(server.run_gcb_test("microsoft/wizardlm-2-8x22b"))

    assert result["error"] == "not_ready"
    assert started is False


def test_run_gcb_test_warns_when_upload_api_not_ready(monkeypatch) -> None:
    async def fake_ready(auto_launch: bool = True) -> dict:
        return {
            "ready": False,
            "openrouter": {"ready": True},
            "gcb_api": {"ready": False, "error": "missing GCB key"},
            "judge_backend": "openrouter",
            "judge_model": "openai/gpt-oss-20b",
        }

    async def fake_start(model_id: str) -> dict:
        return {
            "job_id": "job-2",
            "model_id": model_id,
            "status": "running",
            "log_path": "/tmp/job-2.log",
        }

    monkeypatch.setattr(server, "check_ready_for_testing", fake_ready)
    monkeypatch.setattr(server, "start_gcb_test", fake_start)

    result = asyncio.run(server.run_gcb_test(" microsoft/wizardlm-2-8x22b "))

    assert result["job_id"] == "job-2"
    assert result["model_id"] == "microsoft/wizardlm-2-8x22b"
    assert "uploading the result may fail" in result["warning"]
