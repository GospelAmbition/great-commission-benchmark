"""Stdio MCP server: calls GET /api/runner/models on the GCB platform."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

mcp = FastMCP(
    "Great Commission Benchmark",
    instructions=(
        "Tools for the Great Commission Benchmark platform. "
        "list_active_models calls the authenticated runner API and returns "
        "active models (OpenRouter-style model_id values) plus metadata. "
        "compare_models compares GCB active models against OpenRouter's "
        "published model list. "
        "preview_archive_candidates and archive_missing_on_openrouter support "
        "archiving models no longer available on OpenRouter."
    ),
)


def _base_url() -> str:
    return os.environ.get(
        "GCB_API_BASE_URL", "https://greatcommissionbenchmark.ai"
    ).rstrip("/")


def _api_key() -> str:
    return os.environ.get("GCB_API_KEY", "").strip()


async def _fetch_gcb_active_models() -> dict[str, Any]:
    """Fetch active model payload from the GCB runner API."""
    key = _api_key()
    if not key:
        return {
            "error": "missing_api_key",
            "message": (
                "Set GCB_API_KEY to your dashboard API key "
                "(https://greatcommissionbenchmark.ai/dashboard/settings). "
                "Account needs admin or benchmark editor access."
            ),
        }

    url = f"{_base_url()}/api/runner/models"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers={"X-API-Key": key})
    except httpx.RequestError as exc:
        logger.exception("GCB models request failed")
        return {"error": "request_failed", "message": str(exc), "url": url}

    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {"raw": response.text}

    if response.is_success:
        return payload

    return {
        "error": "api_error",
        "status_code": response.status_code,
        "url": url,
        "detail": payload if isinstance(payload, dict) else response.text,
    }


async def _fetch_openrouter_model_ids() -> dict[str, Any]:
    """Fetch OpenRouter model ids."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(OPENROUTER_MODELS_URL)
    except httpx.RequestError as exc:
        logger.exception("OpenRouter models request failed")
        return {
            "error": "openrouter_request_failed",
            "message": str(exc),
            "url": OPENROUTER_MODELS_URL,
        }

    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {"raw": response.text}

    if not response.is_success:
        return {
            "error": "openrouter_api_error",
            "status_code": response.status_code,
            "url": OPENROUTER_MODELS_URL,
            "detail": payload if isinstance(payload, dict) else response.text,
        }

    openrouter_models_raw = payload.get("data", [])
    if not isinstance(openrouter_models_raw, list):
        return {
            "error": "openrouter_unexpected_payload",
            "message": "OpenRouter response missing list field `data`.",
            "detail": payload,
        }

    openrouter_model_ids = {
        item.get("id")
        for item in openrouter_models_raw
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    return {"ids": openrouter_model_ids, "total": len(openrouter_model_ids)}


def _archive_candidates(
    gcb_models_raw: list[dict[str, Any]], openrouter_model_ids: set[str]
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for item in gcb_models_raw:
        db_id = item.get("id")
        model_id = item.get("model_id")
        name = item.get("name")
        if (
            isinstance(db_id, str)
            and isinstance(model_id, str)
            and isinstance(name, str)
            and model_id not in openrouter_model_ids
        ):
            candidates.append({"id": db_id, "model_id": model_id, "name": name})
    return sorted(candidates, key=lambda candidate: candidate["model_id"])


@mcp.tool()
async def list_active_models() -> dict[str, Any]:
    """Return active benchmark models from the platform.

    Calls GET /api/runner/models. Each model includes id, model_id, name,
    provider, last_tested_version, and last_tested_at. The response also
    includes total and current_version.

    Environment:
        GCB_API_KEY: required. Dashboard API key (X-API-Key).
        GCB_API_BASE_URL: optional. Default https://greatcommissionbenchmark.ai

    The API key's user must have admin or benchmark editor (can_edit_benchmark)
    permission, same as the bulk tester / runner CLI.
    """
    return await _fetch_gcb_active_models()


@mcp.tool()
async def compare_models() -> dict[str, Any]:
    """Compare GCB active models against OpenRouter's model catalog.

    Fetches:
        - GCB: GET /api/runner/models (authenticated with GCB_API_KEY)
        - OpenRouter: GET https://openrouter.ai/api/v1/models

    Returns:
        - counts for each source
        - overlap count
        - gcb_not_on_openrouter (GCB model_ids missing from OpenRouter)
        - openrouter_not_on_gcb (OpenRouter ids not in GCB active set)
    """
    gcb_payload = await _fetch_gcb_active_models()
    if "error" in gcb_payload:
        return gcb_payload

    gcb_models_raw = gcb_payload.get("models", [])
    if not isinstance(gcb_models_raw, list):
        return {
            "error": "unexpected_payload",
            "message": "GCB response missing list field `models`.",
            "detail": gcb_payload,
        }

    gcb_model_ids = {
        item.get("model_id")
        for item in gcb_models_raw
        if isinstance(item, dict) and isinstance(item.get("model_id"), str)
    }

    openrouter_payload = await _fetch_openrouter_model_ids()
    if "error" in openrouter_payload:
        return openrouter_payload
    openrouter_model_ids = openrouter_payload["ids"]

    gcb_not_on_openrouter = sorted(gcb_model_ids - openrouter_model_ids)
    openrouter_not_on_gcb = sorted(openrouter_model_ids - gcb_model_ids)
    overlap = gcb_model_ids & openrouter_model_ids

    return {
        "gcb_total": len(gcb_model_ids),
        "openrouter_total": len(openrouter_model_ids),
        "overlap_total": len(overlap),
        "gcb_not_on_openrouter_total": len(gcb_not_on_openrouter),
        "gcb_not_on_openrouter": gcb_not_on_openrouter,
        "openrouter_not_on_gcb_total": len(openrouter_not_on_gcb),
        "openrouter_not_on_gcb_sample": openrouter_not_on_gcb[:50],
    }


@mcp.tool()
async def preview_archive_candidates() -> dict[str, Any]:
    """Preview active GCB models that are not in OpenRouter.

    Returns archive candidates including the GCB DB id used by the admin archive
    endpoint. This tool is read-only.
    """
    gcb_payload = await _fetch_gcb_active_models()
    if "error" in gcb_payload:
        return gcb_payload

    gcb_models_raw = gcb_payload.get("models", [])
    if not isinstance(gcb_models_raw, list):
        return {
            "error": "unexpected_payload",
            "message": "GCB response missing list field `models`.",
            "detail": gcb_payload,
        }

    openrouter_payload = await _fetch_openrouter_model_ids()
    if "error" in openrouter_payload:
        return openrouter_payload
    openrouter_model_ids = openrouter_payload["ids"]

    candidates = _archive_candidates(gcb_models_raw, openrouter_model_ids)
    return {
        "gcb_total": len(gcb_models_raw),
        "openrouter_total": openrouter_payload["total"],
        "archive_candidate_total": len(candidates),
        "candidates": candidates,
    }


@mcp.tool()
async def archive_missing_on_openrouter(
    dry_run: bool = False,
    max_to_archive: int = 100,
) -> dict[str, Any]:
    """Archive GCB-active models that are no longer listed by OpenRouter.

    Uses PATCH /api/admin/models/{model_id}/archive where model_id is the
    UUID id from GET /api/runner/models.
    """
    if max_to_archive < 1:
        return {"error": "invalid_argument", "message": "max_to_archive must be >= 1"}

    gcb_payload = await _fetch_gcb_active_models()
    if "error" in gcb_payload:
        return gcb_payload

    gcb_models_raw = gcb_payload.get("models", [])
    if not isinstance(gcb_models_raw, list):
        return {
            "error": "unexpected_payload",
            "message": "GCB response missing list field `models`.",
            "detail": gcb_payload,
        }

    openrouter_payload = await _fetch_openrouter_model_ids()
    if "error" in openrouter_payload:
        return openrouter_payload
    openrouter_model_ids = openrouter_payload["ids"]

    candidates = _archive_candidates(gcb_models_raw, openrouter_model_ids)
    planned = candidates[:max_to_archive]

    if dry_run:
        return {
            "dry_run": True,
            "archive_candidate_total": len(candidates),
            "planned_archive_total": len(planned),
            "planned": planned,
            "skipped_due_to_max": max(0, len(candidates) - len(planned)),
        }

    api_key = _api_key()
    base_url = _base_url()
    archived: list[dict[str, str]] = []
    failed: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for candidate in planned:
            url = f"{base_url}/api/admin/models/{candidate['id']}/archive"
            try:
                response = await client.patch(url, headers={"X-API-Key": api_key})
            except httpx.RequestError as exc:
                failed.append({**candidate, "error": str(exc)})
                continue

            if response.is_success:
                archived.append(candidate)
                continue

            try:
                detail = response.json()
            except json.JSONDecodeError:
                detail = response.text
            failed.append(
                {
                    **candidate,
                    "error": {
                        "status_code": response.status_code,
                        "detail": detail,
                    },
                }
            )

    return {
        "dry_run": False,
        "archive_candidate_total": len(candidates),
        "attempted_total": len(planned),
        "archived_total": len(archived),
        "failed_total": len(failed),
        "archived": archived,
        "failed": failed,
        "skipped_due_to_max": max(0, len(candidates) - len(planned)),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
