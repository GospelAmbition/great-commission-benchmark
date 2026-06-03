"""Readiness checks for GCB test prerequisites."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any

import httpx

logger = logging.getLogger(__name__)

LMSTUDIO_BASE_URL = "http://localhost:1234/v1"
JUDGE_MODEL = "openai/gpt-oss-20b"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
GCB_API_BASE_URL = "https://greatcommissionbenchmark.ai"

# How long to wait for LMStudio server to start, in seconds
_SERVER_START_TIMEOUT = 30
# How long to wait for model to load after lms load, in seconds
_MODEL_LOAD_TIMEOUT = 120


# ---------------------------------------------------------------------------
# LMStudio helpers
# ---------------------------------------------------------------------------


def _lms_binary() -> str | None:
    """Return path to the lms CLI, or None if not found."""
    return shutil.which("lms")


async def _probe_lmstudio_server(base_url: str = LMSTUDIO_BASE_URL) -> list[str] | None:
    """Return list of loaded model IDs from LMStudio, or None if not reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/models")
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("id", "") for m in data.get("data", [])]
    except Exception:
        pass
    return None


async def _wait_for_server(
    base_url: str = LMSTUDIO_BASE_URL, timeout: int = _SERVER_START_TIMEOUT
) -> bool:
    """Poll LMStudio until server responds, up to `timeout` seconds."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        models = await _probe_lmstudio_server(base_url)
        if models is not None:
            return True
        await asyncio.sleep(2)
    return False


async def _wait_for_model(
    model_id: str,
    base_url: str = LMSTUDIO_BASE_URL,
    timeout: int = _MODEL_LOAD_TIMEOUT,
) -> bool:
    """Poll LMStudio until the given model appears in the loaded list."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        models = await _probe_lmstudio_server(base_url)
        if models is not None and any(model_id in m for m in models):
            return True
        await asyncio.sleep(3)
    return False


def _run_lms(args: list[str]) -> tuple[int, str]:
    """Run an lms CLI command, return (returncode, combined output)."""
    lms = _lms_binary()
    if not lms:
        return -1, "lms CLI not found in PATH"
    try:
        result = subprocess.run(
            [lms] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, "lms command timed out"
    except Exception as exc:
        return -1, str(exc)


async def check_lmstudio(
    auto_launch: bool = True,
    base_url: str = LMSTUDIO_BASE_URL,
    judge_model: str = JUDGE_MODEL,
) -> dict[str, Any]:
    """
    Check LMStudio server and judge model availability.

    If auto_launch=True, attempts to:
    1. Start LMStudio server via `lms server start` if not reachable.
    2. Load the judge model via `lms load <model> --gpu max` if not loaded.
    """
    result: dict[str, Any] = {
        "ready": False,
        "server_running": False,
        "model_loaded": None,
        "auto_launched": False,
        "auto_loaded_model": False,
        "lms_available": _lms_binary() is not None,
        "error": None,
    }

    # Step 1: check if server is already running
    loaded_models = await _probe_lmstudio_server(base_url)

    if loaded_models is None:
        if not auto_launch:
            result["error"] = (
                "LMStudio server is not running. "
                "Start it manually or pass auto_launch=true."
            )
            return result

        lms = _lms_binary()
        if not lms:
            result["error"] = (
                "LMStudio server is not running and lms CLI was not found in PATH. "
                "Install LMStudio 0.2.22+ and run it once to set up the CLI."
            )
            return result

        logger.info("LMStudio not running; attempting lms server start")
        rc, out = _run_lms(["server", "start"])
        if rc != 0:
            result["error"] = f"lms server start failed (exit {rc}): {out}"
            return result

        logger.info("Waiting for LMStudio server to become available...")
        server_ok = await _wait_for_server(base_url, timeout=_SERVER_START_TIMEOUT)
        if not server_ok:
            result["error"] = (
                f"LMStudio server did not become reachable within "
                f"{_SERVER_START_TIMEOUT}s after lms server start."
            )
            return result

        result["auto_launched"] = True
        loaded_models = await _probe_lmstudio_server(base_url) or []
    else:
        result["server_running"] = True

    result["server_running"] = True

    # Step 2: verify judge model is loaded
    model_present = any(judge_model in m for m in loaded_models)

    if not model_present:
        if not auto_launch:
            result["error"] = (
                f"Judge model '{judge_model}' is not loaded in LMStudio. "
                "Load it manually or pass auto_launch=true."
            )
            return result

        lms = _lms_binary()
        if not lms:
            result["error"] = (
                f"Judge model '{judge_model}' is not loaded and lms CLI not found."
            )
            return result

        # Verify it's downloaded first
        rc_ls, out_ls = _run_lms(["ls"])
        if judge_model not in out_ls and rc_ls == 0:
            result["error"] = (
                f"Judge model '{judge_model}' does not appear to be downloaded in LMStudio. "
                "Please download it from the LMStudio model browser first."
            )
            return result

        logger.info("Loading judge model '%s' via lms load...", judge_model)
        rc, out = _run_lms(["load", judge_model, "--gpu", "max"])
        if rc != 0:
            result["error"] = f"lms load {judge_model} failed (exit {rc}): {out}"
            return result

        logger.info("Waiting for model to load (up to %ds)...", _MODEL_LOAD_TIMEOUT)
        model_ok = await _wait_for_model(judge_model, base_url, timeout=_MODEL_LOAD_TIMEOUT)
        if not model_ok:
            result["error"] = (
                f"Model '{judge_model}' did not appear in loaded models within "
                f"{_MODEL_LOAD_TIMEOUT}s."
            )
            return result

        result["auto_loaded_model"] = True
        result["model_loaded"] = judge_model
    else:
        result["model_loaded"] = judge_model

    result["ready"] = True
    return result


# ---------------------------------------------------------------------------
# OpenRouter check
# ---------------------------------------------------------------------------


async def check_openrouter(api_key: str | None = None) -> dict[str, Any]:
    """Verify OpenRouter API key and connectivity."""
    key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        # Also try reading from gcb-runner config
        key = _gcb_runner_openrouter_key()

    result: dict[str, Any] = {"ready": False, "error": None}

    if not key:
        result["error"] = (
            "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
            "or configure it in gcb-runner (gcb-runner config)."
        )
        return result

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                OPENROUTER_MODELS_URL,
                headers={"Authorization": f"Bearer {key}"},
            )
        if resp.is_success:
            result["ready"] = True
        else:
            result["error"] = (
                f"OpenRouter API returned HTTP {resp.status_code}. "
                "Check that the API key is valid."
            )
    except httpx.RequestError as exc:
        result["error"] = f"Could not reach OpenRouter: {exc}"

    return result


# ---------------------------------------------------------------------------
# GCB platform check
# ---------------------------------------------------------------------------


async def check_gcb_api(api_key: str | None = None) -> dict[str, Any]:
    """Verify GCB platform API key for upload capability."""
    from gcb_mcp.credentials import missing_gcb_api_key_message, resolve_gcb_api_key

    key = (api_key or "").strip() or resolve_gcb_api_key()
    result: dict[str, Any] = {"ready": False, "error": None}

    if not key:
        result["error"] = missing_gcb_api_key_message()
        return result

    try:
        from gcb_mcp.context import current as _current_ctx

        ctx_url = _current_ctx().api_base_url.strip().rstrip("/")
    except Exception:  # pragma: no cover - defensive
        ctx_url = ""
    base_url = (
        ctx_url
        or os.environ.get("GCB_API_BASE_URL", GCB_API_BASE_URL).rstrip("/")
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{base_url}/api/runner/models",
                headers={"X-API-Key": key},
            )
        if resp.is_success:
            result["ready"] = True
        elif resp.status_code == 401:
            result["error"] = "GCB_API_KEY is invalid or lacks benchmark editor permission."
        else:
            result["error"] = f"GCB platform API returned HTTP {resp.status_code}."
    except httpx.RequestError as exc:
        result["error"] = f"Could not reach GCB platform: {exc}"

    return result


# ---------------------------------------------------------------------------
# Combined check
# ---------------------------------------------------------------------------


async def check_all_ready(
    auto_launch: bool = True,
    lmstudio_base_url: str = LMSTUDIO_BASE_URL,
    judge_model: str = JUDGE_MODEL,
) -> dict[str, Any]:
    """Run readiness checks concurrently. Returns combined status.

    The benchmark and judge both use OpenRouter. The LMStudio parameters are
    retained for API compatibility with older callers and are intentionally
    ignored.
    """
    _ = (auto_launch, lmstudio_base_url, judge_model)
    openrouter_result, gcb_result = await asyncio.gather(
        check_openrouter(),
        check_gcb_api(),
    )

    overall_ready = (
        openrouter_result["ready"]
        and gcb_result["ready"]
    )

    return {
        "ready": overall_ready,
        "openrouter": openrouter_result,
        "gcb_api": gcb_result,
        "judge_backend": "openrouter",
        "judge_model": JUDGE_MODEL,
    }


# ---------------------------------------------------------------------------
# Helper: read OpenRouter key from gcb-runner config
# ---------------------------------------------------------------------------


def _gcb_runner_openrouter_key() -> str:
    """Try to read OpenRouter API key from gcb-runner's config.json."""
    try:
        import os as _os

        config_path = (
            _os.path.expanduser("~") + "/.gcb-runner/config.json"
            if _os.name != "nt"
            else _os.path.expanduser("~") + "\\.gcb-runner\\config.json"
        )
        with open(config_path) as f:
            data = json.load(f)
        return (
            data.get("backends", {})
            .get("openrouter", {})
            .get("api_key", "")
            or ""
        )
    except Exception:
        return ""
