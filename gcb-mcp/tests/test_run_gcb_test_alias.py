"""Tests for the natural-language GCB test alias."""

from __future__ import annotations

import asyncio
from datetime import datetime

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

    async def fake_start(model_id: str, allow_excluded: bool = False) -> dict:
        assert model_id == "microsoft/wizardlm-2-8x22b"
        assert allow_excluded is False
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

    async def fake_start(_model_id: str, allow_excluded: bool = False) -> dict:
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

    async def fake_start(model_id: str, allow_excluded: bool = False) -> dict:
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


def test_run_gcb_test_blocks_excluded_model_before_readiness(monkeypatch) -> None:
    readiness_checked = False

    async def fake_ready(auto_launch: bool = True) -> dict:
        nonlocal readiness_checked
        readiness_checked = True
        return {"openrouter": {"ready": True}}

    monkeypatch.setattr(server, "check_ready_for_testing", fake_ready)

    result = asyncio.run(server.run_gcb_test("meta/muse-spark-1.3-contributor"))

    assert result["error"] == "model_excluded"
    assert result["model_id"] == "meta/muse-spark-1.3-contributor"
    assert readiness_checked is False


def test_model_exclusion_rules_cover_registry_and_openrouter_variants() -> None:
    assert server._model_exclusion_reason("sakana/sakana-namazu")
    assert server._model_exclusion_reason("provider/model:batch")
    assert server._model_exclusion_reason("provider/model:free")
    assert server._model_exclusion_reason("~provider/model-latest")
    assert server._model_exclusion_reason("provider/model") is None


def test_suggestions_omit_excluded_models_and_variants(monkeypatch) -> None:
    created = datetime.now().timestamp()

    async def fake_gcb_models() -> dict:
        return {"models": [], "total": 0}

    async def fake_openrouter_models() -> dict:
        def model(model_id: str) -> dict:
            return {
                "id": model_id,
                "name": model_id,
                "created": created,
                "architecture": {"output_modalities": ["text"]},
            }

        models = [
            model("meta/muse-spark-1.3-contributor"),
            model("provider/model:free"),
            model("provider/good-model"),
        ]
        return {"models": models, "total": len(models)}

    monkeypatch.setattr(server, "_fetch_gcb_active_models", fake_gcb_models)
    monkeypatch.setattr(server, "_fetch_openrouter_models_full", fake_openrouter_models)

    result = asyncio.run(server.suggest_models_to_test())

    assert [item["model_id"] for item in result["suggestions"]] == [
        "provider/good-model"
    ]
    assert result["new_in_period"] == 3
    assert result["text_models_found"] == 1
