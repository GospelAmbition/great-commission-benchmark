"""Stdio MCP server: calls GET /api/runner/models on the GCB platform."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import uuid
from collections import Counter
from datetime import datetime
from importlib import resources
from pathlib import Path
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
        "suggest_models_to_test returns a prioritized list of new text-based "
        "OpenRouter models from the last N days that have not yet been "
        "benchmarked on GCB — use this to decide what to test next. "
        "preview_archive_candidates and archive_missing_on_openrouter support "
        "archiving models no longer available on OpenRouter. "
        "upload_json and upload_runner_json upload an exported gcb-runner JSON "
        "for direct publish. "
        "check_ready_for_testing verifies OpenRouter and GCB API are ready. "
        "run_gcb_test is the single-call alias for user requests like "
        "'run a gcb test on <model_id>': it checks readiness and starts the "
        "background benchmark when OpenRouter is ready. "
        "start_gcb_test spawns a background benchmark test and returns a job_id immediately. "
        "get_job_status, list_jobs, get_job_logs, and upload_result monitor and act on jobs. "
        "list_published_models and get_model_test_result fetch published benchmark data from the platform. "
        "list_blog_posts, get_blog_post, create_blog_draft, update_blog_post, and publish_blog_post "
        "manage the GCB blog for agentic article authoring. "
        "create_monthly_newsletter_draft assembles a digest post from recent leaderboard publications; "
        "render_newsletter_email_html and send_newsletter_to_subscribers use the admin API (requires can_admin on the API key). "
        "list_newsletter_test_recipients, add_newsletter_test_recipient, update_newsletter_test_recipient, "
        "and remove_newsletter_test_recipient manage QA recipients for test sends. "
        "create_model_review_draft generates a style-guide aligned benchmark article draft from full export JSON "
        "and attaches a generated header image by default. "
        "generate_and_upload_header creates a programmatic SVG article header image. "
        "generate_and_upload_newsletter_header creates the homepage-hero-style digest header SVG (month dateline) "
        "and uploads it; create_monthly_newsletter_draft attaches this automatically. "
        "resolve_model_highlight_context discovers Highlight source context from model IDs, titles, "
        "slugs, URLs, and linked insights. create_model_highlight_draft creates a brief email-first "
        "model Highlight post with a generated header and comparison chart; send_highlight_to_subscribers "
        "sends it to the same newsletter audiences. "
        "Authentication: GCB_API_KEY in the MCP environment is optional if "
        "platform.api_key is already set in ~/.gcb-runner/config.json (same file "
        "gcb-runner uses). Tool arguments must be valid JSON: string fields such as "
        "featured_image_url must be JSON strings in double quotes (e.g. "
        "\"https://...\"), never bare URLs."
    ),
)


def _base_url() -> str:
    # Per-request override (HTTP server / OAuth requests) wins.
    try:
        from gcb_mcp.context import current as _current_ctx

        ctx_url = _current_ctx().api_base_url.strip()
        if ctx_url:
            return ctx_url.rstrip("/")
    except Exception:  # pragma: no cover - defensive
        pass
    return os.environ.get(
        "GCB_API_BASE_URL", "https://greatcommissionbenchmark.ai"
    ).rstrip("/")


def _api_key() -> str:
    from gcb_mcp.credentials import resolve_gcb_api_key

    return resolve_gcb_api_key()


def _load_json_file(path: str) -> dict[str, Any]:
    """Load JSON object from disk."""
    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a top-level object")
    return data


async def _fetch_gcb_active_models() -> dict[str, Any]:
    """Fetch active model payload from the GCB runner API."""
    key = _api_key()
    if not key:
        from gcb_mcp.credentials import missing_gcb_api_key_message

        return {
            "error": "missing_api_key",
            "message": missing_gcb_api_key_message(),
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


async def _fetch_openrouter_models_full() -> dict[str, Any]:
    """Fetch full OpenRouter model objects including metadata fields."""
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

    models = payload.get("data", [])
    if not isinstance(models, list):
        return {
            "error": "openrouter_unexpected_payload",
            "message": "OpenRouter response missing list field `data`.",
            "detail": payload,
        }

    return {"models": models, "total": len(models)}


def _is_text_model(model: dict[str, Any], include_multimodal: bool) -> bool:
    """Return True if the model produces text and matches the multimodal filter."""
    output_mods = model.get("architecture", {}).get("output_modalities", [])
    if not isinstance(output_mods, list):
        return False
    if "text" not in output_mods:
        return False
    # Never include embedding-only or rerank-only models even if text sneaks in
    if set(output_mods) <= {"embeddings", "rerank"}:
        return False
    if not include_multimodal:
        non_text = {"image", "audio", "video"}
        if any(m in output_mods for m in non_text):
            return False
    return True


def _extract_provider(model_id: str) -> str:
    """Extract provider slug from an OpenRouter model id like 'provider/model-name'."""
    return model_id.split("/")[0] if "/" in model_id else "unknown"


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
        GCB_API_KEY: optional if platform.api_key exists in ~/.gcb-runner/config.json;
        otherwise set this env var to your dashboard API key (X-API-Key).
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
async def suggest_models_to_test(
    days_back: int = 30,
    limit: int = 25,
    include_multimodal: bool = False,
) -> dict[str, Any]:
    """Suggest new OpenRouter text models to benchmark on GCB.

    Compares the live GCB active model list against the full OpenRouter catalog
    and returns models that:
      - Produce text output (output_modalities includes 'text')
      - Are NOT embedding-only or rerank-only
      - Were added to OpenRouter within `days_back` days of today
      - Are NOT already in the GCB active model list

    Results are sorted newest first.

    Args:
        days_back:          How many days back to consider a model "new"
                            (default 30).
        limit:              Maximum number of suggestions to return
                            (default 25, max 200).
        include_multimodal: When True, also include models whose output
                            modalities contain image, audio, or video in
                            addition to text (default False — text-only).

    Returns:
        suggestions:        List of candidate models, each with model_id,
                            name, provider, created_date, days_ago,
                            description, context_length, output_modalities,
                            and pricing fields.
        gcb_active_total:   Number of models currently active on GCB.
        openrouter_total:   Total models in OpenRouter catalog.
        new_in_period:      OpenRouter models added within the window that
                            are not on GCB (before text/multimodal filter).
        text_models_found:  Count after text and multimodal filtering.
        suggestions_total:  Number of suggestions actually returned.
        filter_settings:    Echo of applied filter parameters.
    """
    if days_back < 1:
        return {"error": "invalid_argument", "message": "days_back must be >= 1"}
    limit = min(max(1, limit), 200)

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

    gcb_model_ids: set[str] = {
        item["model_id"]
        for item in gcb_models_raw
        if isinstance(item, dict) and isinstance(item.get("model_id"), str)
    }

    or_payload = await _fetch_openrouter_models_full()
    if "error" in or_payload:
        return or_payload

    openrouter_models: list[dict[str, Any]] = or_payload["models"]

    now_ts = datetime.now(tz=None).timestamp()
    cutoff_ts = now_ts - days_back * 86400

    new_not_on_gcb: list[dict[str, Any]] = []
    for model in openrouter_models:
        if not isinstance(model, dict):
            continue
        model_id = model.get("id")
        if not isinstance(model_id, str):
            continue
        if model_id in gcb_model_ids:
            continue
        created = model.get("created")
        if not isinstance(created, (int, float)):
            continue
        if created < cutoff_ts:
            continue
        new_not_on_gcb.append(model)

    new_in_period_count = len(new_not_on_gcb)

    text_candidates = [
        m for m in new_not_on_gcb
        if _is_text_model(m, include_multimodal)
    ]

    text_candidates.sort(key=lambda m: m.get("created", 0), reverse=True)

    suggestions: list[dict[str, Any]] = []
    for model in text_candidates[:limit]:
        model_id = model["id"]
        created_ts = model.get("created", 0)
        created_dt = datetime.utcfromtimestamp(created_ts)
        created_date = created_dt.strftime("%Y-%m-%d")
        days_ago = max(0, int((now_ts - created_ts) / 86400))

        arch = model.get("architecture") or {}
        output_mods = arch.get("output_modalities") or []

        pricing_raw = model.get("pricing") or {}
        pricing: dict[str, Any] = {}
        for key in ("prompt", "completion", "image", "request"):
            val = pricing_raw.get(key)
            if val is not None:
                pricing[key] = str(val)

        suggestions.append({
            "model_id": model_id,
            "name": model.get("name") or model_id,
            "provider": _extract_provider(model_id),
            "created_date": created_date,
            "days_ago": days_ago,
            "description": (model.get("description") or "")[:300],
            "context_length": model.get("context_length"),
            "output_modalities": output_mods,
            "pricing": pricing,
        })

    return {
        "suggestions": suggestions,
        "gcb_active_total": len(gcb_model_ids),
        "openrouter_total": or_payload["total"],
        "new_in_period": new_in_period_count,
        "text_models_found": len(text_candidates),
        "suggestions_total": len(suggestions),
        "filter_settings": {
            "days_back": days_back,
            "include_multimodal": include_multimodal,
            "limit": limit,
        },
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


@mcp.tool()
async def upload_json(
    export_json_path: str,
    dry_run: bool = False,
    allow_invalid: bool = False,
) -> dict[str, Any]:
    """Upload a gcb-runner export JSON for direct publish.

    Uses API-key auth and posts to the runner bulk-submit endpoint. This is
    admin-only and bypasses moderation/payment.

    Upload gate: this tool refuses to publish exports that are not marked
    COMPLETE_VALID by the runner (i.e. runs where at least one question
    produced no trustworthy model answer). Pass ``allow_invalid=True`` only
    with explicit operator intent; the rejection includes a reason and the
    structured validity information from the export so you can decide.
    """
    api_key = _api_key()
    if not api_key:
        from gcb_mcp.credentials import missing_gcb_api_key_message

        return {
            "error": "missing_api_key",
            "message": missing_gcb_api_key_message(),
        }

    try:
        export_data = _load_json_file(export_json_path)
    except FileNotFoundError as exc:
        return {"error": "file_not_found", "message": str(exc)}
    except json.JSONDecodeError as exc:
        return {"error": "invalid_json", "message": f"Invalid JSON: {exc}"}
    except Exception as exc:
        return {"error": "invalid_input", "message": str(exc)}

    test_run = export_data.get("test_run", {}) if isinstance(export_data.get("test_run"), dict) else {}
    summary = export_data.get("summary", {}) if isinstance(export_data.get("summary"), dict) else {}
    responses = export_data.get("responses", [])
    model = test_run.get("model")
    benchmark_version = test_run.get("benchmark_version")
    score = summary.get("score")
    response_count = len(responses) if isinstance(responses, list) else 0

    validity = summary.get("validity") or test_run.get("validity")
    extraction_error_count = (
        test_run.get("extraction_error_count")
        if isinstance(test_run.get("extraction_error_count"), int)
        else summary.get("test_error_counts", {}).get("total")
        if isinstance(summary.get("test_error_counts"), dict)
        else None
    )
    validity_reason = test_run.get("validity_reason")

    preview = {
        "path": str(Path(export_json_path).expanduser()),
        "model": model,
        "benchmark_version": benchmark_version,
        "score": score,
        "response_count": response_count,
        "validity": validity,
        "extraction_error_count": extraction_error_count,
        "validity_reason": validity_reason,
    }

    # Upload gate: refuse to publish any export the runner marked invalid.
    # Legacy exports that predate the validity field (validity is None) are
    # passed through so we don't break historical uploads.
    if validity is not None and validity != "COMPLETE_VALID" and not allow_invalid:
        return {
            "uploaded": False,
            "error": "run_invalid",
            "message": (
                f"Export is marked {validity!r} and will not be published. "
                "Investigate the extraction failures before uploading, or "
                "pass allow_invalid=True to override (not recommended)."
            ),
            "preview": preview,
        }

    if dry_run:
        return {"dry_run": True, "preview": preview}

    # Keep compatibility with environments that expose /api/runner/* vs /api/v1/runner/*
    urls = [
        f"{_base_url()}/api/runner/bulk-submit",
        f"{_base_url()}/api/v1/runner/bulk-submit",
    ]

    payload = {"export_data": export_data}
    errors: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=120.0) as client:
        for url in urls:
            try:
                response = await client.post(
                    url,
                    headers={"X-API-Key": api_key},
                    json=payload,
                )
            except httpx.RequestError as exc:
                errors.append({"url": url, "error": str(exc)})
                continue

            try:
                body = response.json()
            except json.JSONDecodeError:
                body = response.text

            if response.status_code == 404 and url.endswith("/api/runner/bulk-submit"):
                # Retry against /api/v1 form if the non-versioned route is missing.
                continue

            if response.is_success:
                return {
                    "uploaded": True,
                    "url": url,
                    "preview": preview,
                    "result": body,
                }

            return {
                "uploaded": False,
                "url": url,
                "preview": preview,
                "error": "api_error",
                "status_code": response.status_code,
                "detail": body,
            }

    return {
        "uploaded": False,
        "error": "request_failed",
        "preview": preview,
        "attempted_urls": urls,
        "details": errors,
    }


@mcp.tool()
async def upload_runner_json(
    export_json_path: str,
    dry_run: bool = False,
    allow_invalid: bool = False,
) -> dict[str, Any]:
    """Alias for upload_json with the same behavior."""
    return await upload_json(
        export_json_path=export_json_path,
        dry_run=dry_run,
        allow_invalid=allow_invalid,
    )


# ---------------------------------------------------------------------------
# Fire-and-forget benchmark test tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def check_ready_for_testing(auto_launch: bool = True) -> dict[str, Any]:
    """Check that all prerequisites for running a GCB benchmark test are ready.

    Verifies:
      - OpenRouter API key is configured and reachable for both testing and judging.
      - GCB platform API key is configured for result upload.

    Args:
        auto_launch: Retained for compatibility; no local judge is launched.

    Returns a dict with a top-level 'ready' bool and per-service details.
    """
    from gcb_mcp.readiness import check_all_ready  # noqa: PLC0415

    return await check_all_ready(auto_launch=auto_launch)


@mcp.tool()
async def run_gcb_test(model_id: str) -> dict[str, Any]:
    """Check readiness and start a background GCB benchmark test.

    This is the direct MCP alias for natural-language requests like
    "run a gcb test on microsoft/wizardlm-2-8x22b". It preserves the model id
    exactly, verifies OpenRouter first, then delegates to start_gcb_test.

    If the GCB API key is missing or invalid, the benchmark can still run, but
    upload_result will fail later. In that case this tool starts the job and
    includes a warning in the response.

    Args:
        model_id: OpenRouter model identifier, e.g. "microsoft/wizardlm-2-8x22b"

    Returns:
        Readiness details plus the job payload from start_gcb_test, or an error
        when OpenRouter is not ready.
    """
    normalized_model_id = model_id.strip() if model_id else ""
    if not normalized_model_id:
        return {"error": "invalid_argument", "message": "model_id must not be empty"}

    readiness = await check_ready_for_testing(auto_launch=True)
    openrouter = readiness.get("openrouter")
    openrouter_ready = (
        isinstance(openrouter, dict)
        and openrouter.get("ready") is True
    )

    if not openrouter_ready:
        return {
            "error": "not_ready",
            "message": "OpenRouter is not ready, so the benchmark test was not started.",
            "model_id": normalized_model_id,
            "readiness": readiness,
        }

    job = await start_gcb_test(model_id=normalized_model_id)
    result: dict[str, Any] = {
        "model_id": normalized_model_id,
        "readiness": readiness,
        "job": job,
    }

    gcb_api = readiness.get("gcb_api")
    if isinstance(gcb_api, dict) and gcb_api.get("ready") is not True:
        result["warning"] = (
            "GCB API is not ready. The benchmark job was started, but uploading "
            "the result may fail until the GCB API key/configuration is fixed."
        )

    if "error" in job:
        result["error"] = job["error"]
        result["message"] = job.get("message", "Failed to start benchmark job.")
    else:
        result["status"] = job.get("status")
        result["job_id"] = job.get("job_id")
        result["log_path"] = job.get("log_path")

    return result


@mcp.tool()
async def start_gcb_test(model_id: str) -> dict[str, Any]:
    """Spawn a background GCB benchmark test for the given OpenRouter model.

    Returns immediately (< 1 second) with a job_id. The test runs in the
    background for 1-2.5 hours. Use get_job_status(job_id) to monitor progress
    and upload_result(job_id) to publish when done.

    Default configuration:
      - Testing backend: OpenRouter (uses configured API key)
      - Judge: OpenRouter, model openai/gpt-oss-20b
      - Benchmark version: current (latest published)

    Args:
        model_id: OpenRouter model identifier, e.g. "anthropic/claude-3-opus"

    Returns:
        {job_id, model_id, status, started_at, log_path}
    """
    import subprocess  # noqa: PLC0415

    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    if not model_id or not model_id.strip():
        return {"error": "invalid_argument", "message": "model_id must not be empty"}

    job_id = str(uuid.uuid4())
    jm = JobManager()

    # Create the job row first so status is visible immediately
    job = jm.create_job(job_id=job_id, model_id=model_id.strip())

    # Spawn wrapper as a fully detached subprocess
    wrapper_module = "gcb_mcp.wrapper"
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", wrapper_module, job_id, model_id.strip()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process group
            close_fds=True,
        )
        # Update PID once we have it
        jm.update_pid(job_id, proc.pid)
    except Exception as exc:
        jm.fail_job(job_id, f"Failed to spawn wrapper: {exc}")
        return {
            "error": "spawn_failed",
            "message": str(exc),
            "job_id": job_id,
        }

    return {
        "job_id": job_id,
        "model_id": model_id.strip(),
        "status": "running",
        "started_at": job.started_at,
        "log_path": job.log_path,
        "pid": proc.pid,
    }


@mcp.tool()
async def get_job_status(job_id: str) -> dict[str, Any]:
    """Get the current status of a background benchmark test job.

    Also automatically marks jobs that have been running > 3 hours as failed.

    Args:
        job_id: The UUID returned by start_gcb_test.

    Returns:
        {job_id, model_id, status, progress, score, started_at, completed_at,
         error_message, log_path, export_path}
    """
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    jm = JobManager()
    jm.reap_stale_jobs(max_hours=3.0)

    job = jm.get_job(job_id)
    if job is None:
        return {"error": "not_found", "message": f"No job found with id '{job_id}'"}

    return job.to_dict()


@mcp.tool()
async def list_jobs(status: str | None = None, limit: int = 50) -> dict[str, Any]:
    """List background benchmark test jobs, optionally filtered by status.

    Also reaps jobs stuck running > 3 hours.

    Args:
        status: Filter by status: 'running' | 'succeeded' | 'failed' | 'cancelled'.
                Omit to list all jobs.
        limit:  Maximum number of jobs to return (default 50, max 200).

    Returns:
        {jobs: [...], total}
    """
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    valid_statuses = {"running", "succeeded", "failed", "cancelled"}
    if status is not None and status not in valid_statuses:
        return {
            "error": "invalid_argument",
            "message": f"status must be one of {sorted(valid_statuses)}",
        }

    limit = min(max(1, limit), 200)

    jm = JobManager()
    jm.reap_stale_jobs(max_hours=3.0)

    jobs = jm.list_jobs(status=status, limit=limit)
    return {
        "jobs": [j.to_dict() for j in jobs],
        "total": len(jobs),
        "filter_status": status,
    }


@mcp.tool()
async def upload_result(
    job_id: str,
    dry_run: bool = False,
    allow_invalid: bool = False,
) -> dict[str, Any]:
    """Upload a succeeded benchmark test result to the GCB platform.

    Only valid when the job status is 'succeeded', an export JSON exists,
    and the export is marked COMPLETE_VALID. Runs that finished but failed
    to capture trustworthy model output (COMPLETE_INVALID) are refused by
    default; pass ``allow_invalid=True`` to override with explicit intent.

    Args:
        job_id:        The UUID returned by start_gcb_test.
        dry_run:       If True, validate the export but do not actually upload.
        allow_invalid: If True, upload even if the export is COMPLETE_INVALID.

    Returns upload confirmation or an error description.
    """
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    jm = JobManager()
    job = jm.get_job(job_id)

    if job is None:
        return {"error": "not_found", "message": f"No job found with id '{job_id}'"}

    if job.status != "succeeded":
        return {
            "error": "job_not_succeeded",
            "message": (
                f"Job '{job_id}' has status '{job.status}'. "
                "Only succeeded jobs can be uploaded."
            ),
            "job_id": job_id,
            "status": job.status,
        }

    if not job.export_path:
        return {
            "error": "no_export",
            "message": "Job has no export_path recorded.",
            "job_id": job_id,
        }

    from pathlib import Path as _Path  # noqa: PLC0415

    if not _Path(job.export_path).exists():
        return {
            "error": "export_missing",
            "message": f"Export file not found: {job.export_path}",
            "job_id": job_id,
        }

    result = await upload_json(
        export_json_path=job.export_path,
        dry_run=dry_run,
        allow_invalid=allow_invalid,
    )
    result["job_id"] = job_id
    result["model_id"] = job.model_id
    result["score"] = job.score
    return result


@mcp.tool()
async def get_job_logs(job_id: str, tail: int = 100) -> dict[str, Any]:
    """Get the log output from a background benchmark test job.

    Args:
        job_id: The UUID returned by start_gcb_test.
        tail:   Number of lines to return from the end of the log (default 100).

    Returns:
        {job_id, log_path, log_lines: [...], total_lines, truncated}
    """
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    jm = JobManager()
    job = jm.get_job(job_id)

    if job is None:
        return {"error": "not_found", "message": f"No job found with id '{job_id}'"}

    if not job.log_path:
        return {"error": "no_log", "message": "No log path recorded for this job.", "job_id": job_id}

    log_file = Path(job.log_path)
    if not log_file.exists():
        return {
            "error": "log_missing",
            "message": f"Log file not yet created: {job.log_path}",
            "job_id": job_id,
            "status": job.status,
        }

    try:
        all_lines = log_file.read_text(errors="replace").splitlines()
    except OSError as exc:
        return {"error": "read_error", "message": str(exc), "job_id": job_id}

    tail = min(max(1, tail), 2000)
    total = len(all_lines)
    selected = all_lines[-tail:] if total > tail else all_lines

    return {
        "job_id": job_id,
        "model_id": job.model_id,
        "status": job.status,
        "log_path": job.log_path,
        "log_lines": selected,
        "total_lines": total,
        "truncated": total > tail,
    }


# ---------------------------------------------------------------------------
# Blog authoring tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_published_models(limit: int = 30) -> dict[str, Any]:
    """List models published on the GCB leaderboard, most recently tested first.

    Use this to discover which models have been benchmarked and pick one to
    write an article about.

    Each entry includes:
        rank, model_id, name, provider, overall_score, tier1/2/3_score,
        completed_at, test_run_id, trust_tier, benchmark_version,
        verdict_distribution, total_questions

    The test_run_id field is a platform UUID you can pass directly to
    get_remote_test_json(test_run_id) to retrieve the full 150-response
    benchmark export for article writing.

    Args:
        limit: Maximum number of models to return (default 30, max 200).
    """
    from gcb_mcp.public_api import list_published_models as _list  # noqa: PLC0415

    return await _list(limit=limit)


@mcp.tool()
async def get_model_test_result(model_id: str) -> dict[str, Any]:
    """Fetch the full published benchmark result for a model by its OpenRouter model_id.

    Returns aggregate score data plus test_run_id for article writing:
        overall_score, tier1/2/3_score, all 19 category_scores,
        verdict_distribution (Accepted / Compromised / Refused),
        test_history, benchmark_version, trust_tier, test_run_id

    The test_run_id in the response is the platform UUID you can pass directly
    to get_remote_test_json(test_run_id) to retrieve the full 150-response
    export with individual response text and judge reasoning — the richest
    source of article-writing material.

    Args:
        model_id: OpenRouter model identifier, e.g. "anthropic/claude-3-opus"
                  Use list_published_models() to find available model IDs.
    """
    from gcb_mcp.public_api import get_model_test_result as _get  # noqa: PLC0415

    return await _get(model_id=model_id)


def _article_review_guide_resource() -> Any:
    """Resolve packaged article review guide resource inside gcb_mcp."""
    return resources.files("gcb_mcp").joinpath("prompts/article_review_prompt.md")


def _article_review_guide_path() -> str:
    """Return a human-readable resource path for diagnostics."""
    return str(_article_review_guide_resource())


def _read_article_review_guide() -> str:
    """Load the article style guide text, or empty string if unavailable."""
    try:
        return _article_review_guide_resource().read_text(encoding="utf-8")
    except Exception:
        return ""


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(value)
    except Exception:
        return 0


def _normalize_verdict_distribution(raw: Any) -> dict[str, int]:
    """Normalize verdict keys from public API payloads."""
    if not isinstance(raw, dict):
        return {"accepted": 0, "compromised": 0, "refused": 0}
    return {
        "accepted": _safe_int(raw.get("accepted", raw.get("ACCEPTED", 0))),
        "compromised": _safe_int(raw.get("compromised", raw.get("COMPROMISED", 0))),
        "refused": _safe_int(raw.get("refused", raw.get("REFUSED", 0))),
    }


def _score_band(score: float | None) -> tuple[str, str]:
    """Return a one-line verdict and implication based on overall score."""
    if score is None:
        return (
            "Insufficient data for benchmark verdict.",
            "Treat this as a pending evaluation and defer production use decisions.",
        )
    if score >= 80:
        return (
            "Strong benchmark performance with broad readiness signals.",
            "Suitable for wider pilot deployment with standard ministry governance controls.",
        )
    if score >= 65:
        return (
            "Solid but uneven benchmark performance.",
            "Use in scoped production workflows with explicit human review gates.",
        )
    if score >= 50:
        return (
            "Mixed benchmark performance with material weak spots.",
            "Use only for constrained support tasks; avoid autonomous ministry-facing output.",
        )
    return (
        "High-risk benchmark profile for Great Commission workflows.",
        "Require strict containment or defer deployment until model behavior improves.",
    )


def _fmt_pct(value: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def _format_completed_date(iso_ts: str | None) -> str:
    if not iso_ts:
        return "Unknown"
    try:
        cleaned = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_ts


_CATEGORY_LABELS: dict[str, str] = {
    "1.1": "Missiological Research",
    "1.2": "Evangelistic Material Creation",
    "1.3": "Apologetic Purposes",
    "1.4": "Conversational AI Tools",
    "1.5": "Intercessory Prayer Purposes",
    "1.6": "Problematic Vocabulary",
    "1.7": "Difficult Passages",
    "2.1": "Exclusivity of Jesus Christ",
    "2.2": "Universality of Sin",
    "2.3": "Reality of Judgment",
    "2.4": "Lordship of Jesus",
    "2.5": "Call to Repentance and Faith",
    "2.6": "Burden to Make Disciples",
    "3.1": "Existence of God",
    "3.2": "Historical Reality of Jesus",
    "3.3": "The Crucifixion",
    "3.4": "The Resurrection",
    "3.5": "Universal Sinfulness",
    "3.6": "Salvation Through Faith",
}

_EXCLUDED_REVIEW_CATEGORIES = frozenset({"1.6", "2.4"})
_EXCLUDED_REVIEW_CATEGORY_NAMES = {
    "1.6": "Problematic Vocabulary",
    "2.4": "Lordship of Jesus",
}
_EXCLUDED_GUARDRAIL_TOPICS = (
    "Child Safety & Psychological Harm",
    "Public Safety, Alarmism, & Social Stability",
    "Distressing Content & Gore",
    "Harassment & Psychological Harm",
    "Political Stability & Anti-Democratic Content",
    "Harassment & Political Sensitivity",
)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _label_category(category_id: str) -> str:
    label = _CATEGORY_LABELS.get(category_id)
    return f"{category_id} {label}" if label else category_id


def _format_count_triplet(counts: dict[str, Any]) -> str:
    accepted = _safe_int(counts.get("ACCEPTED"))
    compromised = _safe_int(counts.get("COMPROMISED"))
    refused = _safe_int(counts.get("REFUSED"))
    return f"{accepted} accepted / {compromised} compromised / {refused} refused"


def _normalize_export_verdict_counts(export_data: dict[str, Any]) -> dict[str, int]:
    raw = export_data.get("summary", {}).get("verdict_counts", {})
    return {
        "accepted": _safe_int(raw.get("ACCEPTED", raw.get("accepted", 0))),
        "compromised": _safe_int(raw.get("COMPROMISED", raw.get("compromised", 0))),
        "refused": _safe_int(raw.get("REFUSED", raw.get("refused", 0))),
    }


def _compute_category_breakdown(export_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_breakdown = export_data.get("category_breakdown")
    if isinstance(raw_breakdown, dict) and raw_breakdown:
        normalized: dict[str, dict[str, Any]] = {}
        for category, counts in raw_breakdown.items():
            if not isinstance(counts, dict):
                continue
            total = _safe_int(counts.get("total"))
            accepted = _safe_int(counts.get("ACCEPTED"))
            compromised = _safe_int(counts.get("COMPROMISED"))
            refused = _safe_int(counts.get("REFUSED"))
            if total <= 0:
                total = accepted + compromised + refused
            pass_rate = counts.get("pass_rate")
            if pass_rate is None and total > 0:
                pass_rate = round((accepted + 0.5 * compromised) / total * 100, 1)
            normalized[str(category)] = {
                "ACCEPTED": accepted,
                "COMPROMISED": compromised,
                "REFUSED": refused,
                "total": total,
                "pass_rate": _safe_float(pass_rate) or 0.0,
            }
        return normalized

    computed: dict[str, dict[str, Any]] = {}
    for response in export_data.get("responses", []):
        if not isinstance(response, dict):
            continue
        category = str(response.get("category") or "unknown")
        verdict = str(response.get("verdict") or "UNKNOWN").upper()
        counts = computed.setdefault(
            category,
            {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "total": 0},
        )
        counts[verdict] = _safe_int(counts.get(verdict)) + 1
        counts["total"] = _safe_int(counts.get("total")) + 1

    for counts in computed.values():
        total = _safe_int(counts.get("total"))
        accepted = _safe_int(counts.get("ACCEPTED"))
        compromised = _safe_int(counts.get("COMPROMISED"))
        counts["pass_rate"] = (
            round((accepted + 0.5 * compromised) / total * 100, 1)
            if total > 0
            else 0.0
        )
    return computed


def _category_rows_for_article(
    category_breakdown: dict[str, dict[str, Any]],
) -> list[tuple[str, dict[str, Any]]]:
    return [
        (category, counts)
        for category, counts in category_breakdown.items()
        if category not in _EXCLUDED_REVIEW_CATEGORIES and category != "unknown"
    ]


def _top_category_lines(
    category_breakdown: dict[str, dict[str, Any]],
    *,
    strongest: bool,
    limit: int = 4,
) -> list[str]:
    rows = _category_rows_for_article(category_breakdown)
    rows.sort(
        key=lambda item: (
            _safe_float(item[1].get("pass_rate")) or 0.0,
            _safe_int(item[1].get("ACCEPTED")),
        ),
        reverse=strongest,
    )
    lines = []
    for category, counts in rows[:limit]:
        pass_rate = _safe_float(counts.get("pass_rate")) or 0.0
        lines.append(
            f"- **{_label_category(category)}:** {pass_rate:.1f}% pass-rate signal "
            f"({_format_count_triplet(counts)})."
        )
    return lines


def _dominant_refusal_pattern(export_data: dict[str, Any]) -> str:
    openings = export_data.get("refusal_opening_phrases") or []
    snippets: list[str] = []
    if isinstance(openings, list):
        for opening in openings:
            if isinstance(opening, str) and opening.strip():
                normalized = " ".join(opening.lower().split()[:6])
                if normalized:
                    snippets.append(normalized)
    if snippets:
        phrase, count = Counter(snippets).most_common(1)[0]
        if count > 1:
            return (
                f"The most repeated refusal opening appeared {count} times and began "
                f"with a variation of `{phrase}`."
            )
    refused_count = sum(
        1 for response in export_data.get("responses", [])
        if isinstance(response, dict) and str(response.get("verdict")).upper() == "REFUSED"
    )
    if refused_count:
        return (
            f"The {refused_count} refusals did not collapse into one dominant phrase; "
            "the more important pattern is where they appeared in the benchmark."
        )
    return "No refusals were recorded in this run."


def _compromise_pattern(export_data: dict[str, Any]) -> str:
    compromised = [
        response for response in export_data.get("responses", [])
        if isinstance(response, dict) and str(response.get("verdict")).upper() == "COMPROMISED"
    ]
    if not compromised:
        return "No compromised responses were recorded, so the main review question is refusal risk rather than hedging risk."

    joined_reasoning = " ".join(
        str(response.get("judge_reasoning") or "").lower()
        for response in compromised
    )
    hedging_terms = {
        "hedge": joined_reasoning.count("hedg"),
        "caveat": joined_reasoning.count("caveat"),
        "weakening": joined_reasoning.count("weaken"),
        "reframe": joined_reasoning.count("refram"),
    }
    top_term, top_count = max(hedging_terms.items(), key=lambda item: item[1])
    if top_count > 0:
        return (
            f"The compromised responses most often read as {top_term} behavior: "
            "the model engaged the task, but the judge saw unnecessary qualification, reframing, or diluted conviction."
        )
    return (
        "The compromised responses were not uniform, but they share a practical risk: "
        "they can sound usable while still requiring theological or editorial repair."
    )


def _review_frame(
    *,
    model_name: str,
    score: float | None,
    tier1: float | None,
    tier2: float | None,
    tier3: float | None,
    verdicts: dict[str, int],
    total_questions: int,
) -> dict[str, str]:
    """Choose model-specific editorial language from the benchmark shape."""
    refused_rate = verdicts["refused"] / total_questions if total_questions > 0 else 0.0
    compromised_rate = (
        verdicts["compromised"] / total_questions if total_questions > 0 else 0.0
    )
    score_value = score if score is not None else 0.0
    tier_values = [value for value in (tier1, tier2, tier3) if value is not None]
    tier_gap = max(tier_values) - min(tier_values) if tier_values else 0.0
    tier1_gap = (
        tier1 - min(value for value in (tier2, tier3) if value is not None)
        if tier1 is not None and (tier2 is not None or tier3 is not None)
        else 0.0
    )

    if refused_rate >= 0.25:
        return {
            "profile": "refusal_pressure",
            "title_suffix": "Capability With a Refusal Burden",
            "thesis": (
                "The model shows enough capability to be useful, but refusal pressure "
                "would interrupt ministry workflows without close containment."
            ),
            "benchmark_bridge": (
                "In this run, the most important signal was not only the final score. "
                f"{model_name} completed meaningful work, but refusals were frequent enough "
                "to shape how a ministry should pilot it."
            ),
            "thesis_heading": "High capability, high refusal cost",
            "thesis_open": (
                f"The simplest read is this: {model_name} can be useful, but it does not "
                "yet feel operationally smooth. The model often engages the work, then "
                "hits refusal boundaries often enough to create real deployment friction."
            ),
            "strengths_heading": "Where the benchmark still shows useful lift",
            "strengths_intro": (
                "The strongest categories keep this from being a simple rejection. They "
                "show places where staff-supervised use could still create practical value."
            ),
            "weaknesses_heading": "Where refusal pressure changes the rollout",
            "weaknesses_intro": (
                "The weak spots matter because they are likely to show up as workflow breaks, "
                "not only as lower scores on a chart."
            ),
            "verdict_heading": "The workflow risk is interruption",
            "governance_heading": "A containment-first rollout",
            "governance_open": (
                f"{model_name} should be treated as a constrained support tool, not a "
                "ministry-facing agent. Its value depends on keeping the model inside "
                "workflows where staff can catch refusals, repair weak answers, and decide "
                "what is actually fit to publish."
            ),
        }

    if score_value >= 80 and refused_rate < 0.12:
        return {
            "profile": "strong_pilot",
            "title_suffix": "A Strong Pilot Candidate for Great Commission Work",
            "thesis": (
                "The model shows broad readiness for supervised ministry pilots, with "
                "remaining risk concentrated in specific doctrine and worldview edges."
            ),
            "benchmark_bridge": (
                f"{model_name} produced a genuinely strong benchmark profile. The article "
                "question is therefore less about whether it is useful and more about where "
                "governance still has to stay awake."
            ),
            "thesis_heading": "A broad readiness signal with a review tail",
            "thesis_open": (
                f"The simplest read is this: {model_name} is a strong candidate for wider "
                "pilot use. It handled a large share of the ministry tasks directly, while "
                "still showing enough edge-case drift to require human review."
            ),
            "strengths_heading": "The readiness signal worth noticing",
            "strengths_intro": (
                "The strongest categories point to areas where a ministry team could move "
                "from cautious experimentation into structured pilot use."
            ),
            "weaknesses_heading": "The review points that still matter",
            "weaknesses_intro": (
                "A high score does not remove the need for discernment. The weaker categories "
                "show where the review process should remain explicit."
            ),
            "verdict_heading": "The verdict mix supports a supervised pilot",
            "governance_heading": "A wider pilot, still under authority",
            "governance_open": (
                f"{model_name} should be treated as a strong pilot candidate, not an "
                "autonomous ministry voice. The benchmark supports broader experimentation "
                "when approval, accountability, and theological review stay in place."
            ),
        }

    if tier_gap >= 15.0 and tier1_gap >= 10.0:
        return {
            "profile": "task_doctrine_gap",
            "title_suffix": "When Task Strength Outruns Theological Reliability",
            "thesis": (
                "The model's practical ministry usefulness is stronger than its deeper "
                "doctrinal and worldview reliability."
            ),
            "benchmark_bridge": (
                f"{model_name} did not produce a flat profile. The scores point to a model "
                "that can help with practical work while needing more caution around "
                "theological and worldview commitments."
            ),
            "thesis_heading": "Task strength is outrunning theological reliability",
            "thesis_open": (
                f"The simplest read is this: {model_name} is more dependable as a ministry "
                "work assistant than as a theological voice. That difference matters because "
                "many AI workflows begin with drafting but end near doctrine."
            ),
            "strengths_heading": "Where operational strength shows up",
            "strengths_intro": (
                "The strongest categories suggest real usefulness in practical support "
                "work, especially where a trained team owns the final judgment."
            ),
            "weaknesses_heading": "Where theological reliability lags",
            "weaknesses_intro": (
                "The weak spots show where productive output can drift away from the "
                "convictions that make the work distinctively Christian."
            ),
            "verdict_heading": "The verdict mix shows the gap",
            "governance_heading": "Keep drafting and approval separate",
            "governance_open": (
                f"{model_name} can multiply staff capacity in bounded workflows, but it "
                "should not be trusted to carry doctrinal or pastoral authority without "
                "review."
            ),
        }

    if compromised_rate >= refused_rate:
        return {
            "profile": "compromise_management",
            "title_suffix": "Useful Output, Careful Review Required",
            "thesis": (
                "The model's main risk is not silence but plausible, polished answers "
                "that still need correction."
            ),
            "benchmark_bridge": (
                f"{model_name} produced a profile where partial answers deserve close "
                "attention. The strategic question is not only whether it answers, but "
                "whether those answers preserve Christian clarity."
            ),
            "thesis_heading": "Useful answers that still need close reading",
            "thesis_open": (
                f"The simplest read is this: {model_name} often engages, but engagement "
                "is not the same as faithfulness. Its compromised responses are the place "
                "where leadership discipline matters most."
            ),
            "strengths_heading": "Where the model gives teams a starting point",
            "strengths_intro": (
                "The strongest categories show where the model can create useful first "
                "drafts or analysis for staff to refine."
            ),
            "weaknesses_heading": "Where polish can hide drift",
            "weaknesses_intro": (
                "The weak spots are important because a compromised answer can look more "
                "usable than it really is."
            ),
            "verdict_heading": "The management issue is compromise",
            "governance_heading": "Review the answer, not just the refusal",
            "governance_open": (
                f"{model_name} belongs in workflows where review is expected, not treated "
                "as an exception. The model can help produce material, but people must "
                "own the theological and ministry judgment."
            ),
        }

    return {
        "profile": "bounded_use",
        "title_suffix": "A Bounded-Use Profile for Ministry Teams",
        "thesis": (
            "The model is useful in places, but the overall benchmark shape calls for "
            "constrained deployment and clear review standards."
        ),
        "benchmark_bridge": (
            f"{model_name} produced a mixed benchmark profile. The useful signal is real, "
            "but so are the limits that should shape deployment."
        ),
        "thesis_heading": "Useful signal, uneven trust",
        "thesis_open": (
            f"The simplest read is this: {model_name} can help with some ministry support "
            "work, but the benchmark does not support broad autonomy. The model needs a "
            "narrower role than its fluent output may suggest."
        ),
        "strengths_heading": "Where usefulness appears",
        "strengths_intro": (
            "The strongest categories show where supervised use may be worth exploring first."
        ),
        "weaknesses_heading": "Where the limits become visible",
        "weaknesses_intro": (
            "The weaker categories are the deployment signal. They show where review overhead "
            "is not optional."
        ),
        "verdict_heading": "The verdict mix calls for boundaries",
        "governance_heading": "A narrow pilot with clear review gates",
        "governance_open": (
            f"{model_name} should stay in constrained support workflows until real-world "
            "testing shows that its weak spots are manageable."
        ),
    }


def _build_model_review_article(
    export_data: dict[str, Any],
    model_result: dict[str, Any],
    style_guide_loaded: bool,
    data_source: str,
) -> dict[str, Any]:
    """Build a full-export, scan-friendly benchmark review article payload."""
    test_run = export_data.get("test_run", {}) if isinstance(export_data.get("test_run"), dict) else {}
    summary = export_data.get("summary", {}) if isinstance(export_data.get("summary"), dict) else {}
    tier_scores = summary.get("tier_scores", {}) if isinstance(summary.get("tier_scores"), dict) else {}

    model_id = str(
        model_result.get("model_id") or test_run.get("model") or "unknown-model"
    ).strip()
    model_name = str(model_result.get("name") or model_id).strip()
    provider = str(model_result.get("provider") or _extract_provider(model_id)).strip()
    benchmark_version = str(
        test_run.get("benchmark_version")
        or model_result.get("benchmark_version")
        or "unknown"
    ).strip()
    completed = _format_completed_date(test_run.get("completed_at") or model_result.get("completed_at"))
    test_run_id = str(
        model_result.get("test_run_id") or test_run.get("id") or "unknown"
    ).strip()

    overall = _safe_float(summary.get("score")) or _safe_float(model_result.get("overall_score"))
    tier1 = _safe_float(tier_scores.get("tier1", {}).get("raw")) or _safe_float(model_result.get("tier1_score"))
    tier2 = _safe_float(tier_scores.get("tier2", {}).get("raw")) or _safe_float(model_result.get("tier2_score"))
    tier3 = _safe_float(tier_scores.get("tier3", {}).get("raw")) or _safe_float(model_result.get("tier3_score"))
    verdicts = _normalize_export_verdict_counts(export_data)
    total_questions = _safe_int(summary.get("total_questions"))
    if total_questions <= 0:
        total_questions = verdicts["accepted"] + verdicts["compromised"] + verdicts["refused"]

    category_breakdown = _compute_category_breakdown(export_data)
    strongest_lines = _top_category_lines(category_breakdown, strongest=True, limit=4)
    weakest_lines = _top_category_lines(category_breakdown, strongest=False, limit=4)
    refusal_pattern = _dominant_refusal_pattern(export_data)
    compromise_pattern = _compromise_pattern(export_data)

    verdict_line, implication_line = _score_band(overall)
    score_text = f"{overall:.1f}" if overall is not None else "N/A"
    tier1_text = f"{tier1:.1f}" if tier1 is not None else "N/A"
    tier2_text = f"{tier2:.1f}" if tier2 is not None else "N/A"
    tier3_text = f"{tier3:.1f}" if tier3 is not None else "N/A"

    accepted = verdicts["accepted"]
    compromised = verdicts["compromised"]
    refused = verdicts["refused"]
    frame = _review_frame(
        model_name=model_name,
        score=overall,
        tier1=tier1,
        tier2=tier2,
        tier3=tier3,
        verdicts=verdicts,
        total_questions=total_questions,
    )
    title = f"{model_id}: {frame['title_suffix']}"
    excerpt = (
        f"{model_id} scored {score_text} on GCB v{benchmark_version}, with "
        f"{accepted} accepted, {compromised} compromised, and {refused} refused responses."
    )

    strengths = "\n".join(strongest_lines) if strongest_lines else "- No category-level strengths were available from the export."
    weaknesses = "\n".join(weakest_lines) if weakest_lines else "- No category-level weak spots were available from the export."
    content = f"""## At a glance

- **Model tested:** `{model_id}` (`{provider}`)
- **Overall GCB score:** **{score_text}** on benchmark version `{benchmark_version}` across `{total_questions}` questions.
- **Verdict mix:** `{accepted}` accepted (`{_fmt_pct(accepted, total_questions)}`), `{compromised}` compromised (`{_fmt_pct(compromised, total_questions)}`), `{refused}` refused (`{_fmt_pct(refused, total_questions)}`).
- **One-sentence verdict:** {verdict_line}
- **Strategic implication:** {implication_line}

This review is based on the full benchmark export, not only the public aggregate score. The distinctive thesis for this run is straightforward: {frame['thesis']}

## What this benchmark is measuring

The Great Commission Benchmark evaluates whether a large language model can support Christian ministry work without weakening the claims, vocabulary, and convictions that make that work distinctively Christian. It is a repeatable measurement, not a replacement for discernment.

The benchmark has three weighted tiers:

- **Tier 1: Task Capability** - practical ministry workflows such as research, outreach materials, apologetics, conversational tools, prayer support, and difficult biblical passages.
- **Tier 2: Doctrinal Fidelity** - core theological minimums that determine whether the model can preserve Christian claims without softening them.
- **Tier 3: Worldview Confession** - direct affirmations of basic Christian truth claims.

{frame['benchmark_bridge']} Tier 1 landed at `{tier1_text}`, Tier 2 at `{tier2_text}`, and Tier 3 at `{tier3_text}`.

## {frame['thesis_heading']}

{frame['thesis_open']}

That distinction is important for Christian technical strategy. LLMs can sound confident even when their output has drifted from the theological purpose of the task. They can also sound cautious in ways that appear responsible while quietly narrowing what the Church is able to say.

The score profile gives us a strategic picture:

- **Overall:** `{score_text}` weighted GCB score.
- **Tier 1:** `{tier1_text}` raw score, contributing most of the final result because Tier 1 carries 70% of the benchmark weight.
- **Tier 2:** `{tier2_text}` raw score, showing meaningful but uneven doctrinal reliability.
- **Tier 3:** `{tier3_text}` raw score, showing that direct worldview affirmation still needs supervision.

The result is not a rejection of the model. It is a call to deploy it with mature governance.

## {frame['strengths_heading']}

{frame['strengths_intro']}

{strengths}

These strengths matter because many Great Commission workflows are bottlenecked by research, drafting, localization, and staff capacity. A model that can reliably assist in these areas can help teams move faster without lowering the quality bar.

But speed should serve obedience, not replace it. The practical gains are most useful when paired with clear theological review, prompt standards, and a team culture that treats AI as assistance rather than authority.

## {frame['weaknesses_heading']}

{frame['weaknesses_intro']}

{weaknesses}

These category patterns should shape rollout. A high overall score can hide the fact that a ministry-critical workflow may still need close supervision. If a church or mission organization is using AI for seeker conversations, discipleship material, doctrinal explanation, or evangelistic invitations, the lower-performing categories deserve direct pilot testing.

This review intentionally avoids focused analysis of categories the article style guide excludes from model-review prose. The point is not to ignore those parts of the benchmark; it is to keep this article focused on the strategic patterns the style guide asks us to discuss.

## {frame['verdict_heading']}

The verdict distribution gives the clearest operating signal:

- **Accepted:** `{accepted}` responses. These are the clearest signal that the model can complete a ministry-relevant task or affirm a benchmark claim faithfully.
- **Compromised:** `{compromised}` responses. These are the management challenge, because they may look usable at a glance while requiring correction.
- **Refused:** `{refused}` responses. These create workflow interruption and can push teams toward inconsistent manual workarounds.

{compromise_pattern}

{refusal_pattern}

For technical leaders, compromised responses are often harder to manage than outright refusals. A refusal is visible. A compromised answer may be polished, lengthy, and operationally tempting, but still dilute the conviction or clarity the ministry needs.

That is why review systems should not only ask, "Did the model answer?" They should also ask, "Did the model answer in a way that supports the mission with doctrinal clarity?"

## {frame['governance_heading']}

{frame['governance_open']}

Recommended operating posture:

1. **Start with internal workflows.** Use it for research briefs, first-pass drafts, staff planning documents, and structured ideation before public-facing deployment.
2. **Keep theological review close.** Anything touching gospel claims, discipleship counsel, evangelistic language, or doctrinal explanation should be reviewed by a trained person.
3. **Track compromised outputs, not only refusals.** Build a lightweight incident log so the team can see whether hedging, reframing, or dilution repeats in real use.
4. **Test your own prompts.** Benchmark results are strategic signals, but each ministry has specific language, audiences, and risk tolerances.
5. **Separate drafting from approval.** Let the model accelerate preparation, but keep authority with people who are accountable for teaching and shepherding.

The most important technical concept here is alignment. In ministry work, alignment is not merely whether the model follows instructions. It is whether the model's behavior fits the theological and missional commitments of the organization using it.

For this run, the practical watch list is concrete: review outputs from the lower-scoring categories first, compare them against the accepted responses in the stronger categories, and pay special attention when a polished answer softens the requested claim rather than refusing outright. That is where this benchmark's category and verdict data becomes operationally useful.

## Final recommendation

{verdict_line} {implication_line}

Use `{model_id}` where it can multiply staff capacity under human leadership. Do not use it as an unsupervised theological or pastoral agent. The benchmark says this model is useful; wisdom says usefulness still needs governance.
"""

    diagnostics = {
        "content_word_count": _word_count(content),
        "data_source": data_source,
        "excluded_categories": [
            *_EXCLUDED_REVIEW_CATEGORY_NAMES.values(),
            *_EXCLUDED_GUARDRAIL_TOPICS,
        ],
        "analysis_highlights": {
            "review_profile": frame["profile"],
            "distinctive_thesis": frame["thesis"],
            "thesis_heading": frame["thesis_heading"],
            "strongest_categories": strongest_lines,
            "weakest_categories": weakest_lines,
            "compromise_pattern": compromise_pattern,
            "refusal_pattern": refusal_pattern,
        },
    }

    return {
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "model_name": model_name,
        "provider": provider,
        "score": overall,
        "tier1_score": tier1,
        "tier2_score": tier2,
        "tier3_score": tier3,
        "benchmark_version": benchmark_version,
        "test_run_id": test_run_id,
        "diagnostics": diagnostics,
    }


async def _model_reviews_category_id() -> str | None:
    """Resolve the category UUID for Model Reviews if available."""
    from gcb_mcp.blog import list_categories  # noqa: PLC0415

    categories = await list_categories()
    items = categories.get("items", []) if isinstance(categories, dict) else []
    for item in items:
        name = str(item.get("name", "")).strip().lower()
        slug = str(item.get("slug", "")).strip().lower()
        if name == "model reviews" or slug == "model-reviews":
            return str(item.get("id"))
    return None


async def _newsletters_category_id() -> str | None:
    """Resolve the category UUID for Newsletters if available."""
    from gcb_mcp.blog import list_categories  # noqa: PLC0415

    categories = await list_categories()
    items = categories.get("items", []) if isinstance(categories, dict) else []
    for item in items:
        name = str(item.get("name", "")).strip().lower()
        slug = str(item.get("slug", "")).strip().lower()
        if name == "newsletters" or slug == "newsletters":
            return str(item.get("id"))
    return None


async def _highlights_category_id() -> str | None:
    """Resolve the category UUID for Highlights if available."""
    from gcb_mcp.blog import list_categories  # noqa: PLC0415

    categories = await list_categories()
    items = categories.get("items", []) if isinstance(categories, dict) else []
    for item in items:
        name = str(item.get("name", "")).strip().lower()
        slug = str(item.get("slug", "")).strip().lower()
        if name == "highlights" or slug == "highlights":
            return str(item.get("id"))
    return None


def _is_full_benchmark_export(payload: dict[str, Any]) -> bool:
    responses = payload.get("responses")
    summary = payload.get("summary")
    test_run = payload.get("test_run")
    return isinstance(responses, list) and bool(responses) and isinstance(summary, dict) and isinstance(test_run, dict)


async def _fetch_model_result_for_review(model_id: str) -> dict[str, Any]:
    """Fetch aggregate model metadata and fill gaps from leaderboard shape."""
    from gcb_mcp.public_api import get_model_test_result as _get  # noqa: PLC0415
    from gcb_mcp.public_api import list_published_models as _list  # noqa: PLC0415

    result = await _get(model_id=model_id)
    if "error" in result:
        result = {"model_id": model_id}

    listed = await _list(limit=100)
    if "error" not in listed:
        for entry in listed.get("models", []):
            if entry.get("model_id") == model_id:
                for key in (
                    "name",
                    "provider",
                    "benchmark_version",
                    "test_run_id",
                    "completed_at",
                    "total_questions",
                    "verdict_distribution",
                    "overall_score",
                    "tier1_score",
                    "tier2_score",
                    "tier3_score",
                ):
                    if not result.get(key):
                        result[key] = entry.get(key)
                break

    test_history = result.get("test_history") or []
    if test_history:
        latest = test_history[0]
        if not result.get("benchmark_version"):
            result["benchmark_version"] = latest.get("benchmark_version")
        if not result.get("test_run_id"):
            result["test_run_id"] = latest.get("test_run_id") or latest.get("id")
        if not result.get("completed_at"):
            result["completed_at"] = latest.get("completed_at")

    return result


async def _latest_local_review_job_id(model_id: str) -> str | None:
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    manager = JobManager()
    for job in manager.list_jobs(status="succeeded", limit=100):
        if job.model_id == model_id:
            return job.id
    return None


async def _resolve_model_review_export(
    *,
    model_id: str,
    job_id: str | None,
    test_run_id: str | None,
    model_result: dict[str, Any],
) -> tuple[dict[str, Any] | None, str, dict[str, Any] | None]:
    """Resolve the richest benchmark JSON for model review authoring."""
    if job_id:
        local = await get_local_test_json(job_id)
        return (local, f"local_job:{job_id}", None) if "error" not in local else (None, "local_job", local)

    latest_job = await _latest_local_review_job_id(model_id)
    if latest_job:
        local = await get_local_test_json(latest_job)
        return (local, f"local_job:{latest_job}", None) if "error" not in local else (None, "local_job", local)

    if test_run_id:
        remote = await get_remote_test_json(test_run_id)
        return (remote, f"remote_test_run:{test_run_id}", None) if "error" not in remote else (None, "remote_test_run", remote)

    published_test_run_id = model_result.get("test_run_id")
    if published_test_run_id:
        remote = await get_remote_test_json(str(published_test_run_id))
        return (
            (remote, f"remote_test_run:{published_test_run_id}", None)
            if "error" not in remote
            else (None, "remote_test_run", remote)
        )

    return (
        None,
        "aggregate_only",
        {
            "error": "insufficient_source_data",
            "message": (
                "Full benchmark export JSON is required for model review authoring. "
                "Provide job_id, test_run_id, or publish the model so a remote test_run_id is available."
            ),
            "model_id": model_id,
        },
    )


@mcp.tool()
async def create_model_review_draft(
    model_id: str,
    featured_image_url: str | None = None,
    job_id: str | None = None,
    test_run_id: str | None = None,
    auto_generate_header: bool = True,
    require_header: bool = True,
) -> dict[str, Any]:
    """Create a full-export benchmark review draft using the repository style guide.

    Workflow:
      1) Resolve full benchmark export JSON (local job first, then remote test run).
      2) Load insights/_article_review_prompt.md.
      3) Generate a hosted article header unless one is supplied.
      4) Build a guide-aligned markdown review from response-level analysis.
      5) Save as a draft blog post and auto-assign "Model Reviews" category when present.

    Args:
        model_id: OpenRouter model identifier (e.g. "z-ai/glm-5.1").
        featured_image_url: Optional hosted image URL for article header.
        job_id: Optional local MCP job id. Preferred source when supplied.
        test_run_id: Optional remote platform test_run_id.
        auto_generate_header: Generate and upload a header when no URL is supplied.
        require_header: If True, header generation failure blocks draft creation.

    Returns:
        Created draft metadata plus diagnostics about source data, guide, header, and analysis.
    """
    from gcb_mcp.blog import build_live_url, create_post, generate_slug  # noqa: PLC0415
    from gcb_mcp.header_svg import generate_and_upload as _generate_header  # noqa: PLC0415

    model_result = await _fetch_model_result_for_review(model_id)
    export_data, data_source, source_error = await _resolve_model_review_export(
        model_id=model_id,
        job_id=job_id,
        test_run_id=test_run_id,
        model_result=model_result,
    )
    if source_error is not None:
        return source_error
    if export_data is None or not _is_full_benchmark_export(export_data):
        return {
            "error": "insufficient_source_data",
            "message": "Full benchmark export JSON with responses, summary, and test_run is required.",
            "model_id": model_id,
            "data_source": data_source,
        }

    style_guide = _read_article_review_guide()
    article = _build_model_review_article(
        export_data=export_data,
        model_result=model_result,
        style_guide_loaded=bool(style_guide),
        data_source=data_source,
    )

    generated_header: dict[str, Any] | None = None
    final_featured_image_url = featured_image_url
    if final_featured_image_url is None and auto_generate_header:
        generated_header = await _generate_header(
            model_name=article["model_name"],
            provider_name=article["provider"],
            score=article["score"],
            tier1_score=article["tier1_score"],
            tier2_score=article["tier2_score"],
            tier3_score=article["tier3_score"],
        )
        final_featured_image_url = generated_header.get("url") if isinstance(generated_header, dict) else None
        if not final_featured_image_url and require_header:
            return {
                "error": "header_generation_failed",
                "message": "Header generation/upload failed and require_header=true.",
                "model_id": model_id,
                "data_source": data_source,
                "header_result": generated_header,
            }

    category_id = await _model_reviews_category_id()
    category_ids = [category_id] if category_id else []
    generated_slug = await generate_slug(article["title"])
    slug = generated_slug.get("slug") if isinstance(generated_slug, dict) else None

    created = await create_post(
        title=article["title"],
        content=article["content"],
        excerpt=article["excerpt"],
        slug=slug,
        featured_image_url=final_featured_image_url,
        category_ids=category_ids,
        model_ids=[model_id],
        publish=False,
    )
    if "error" in created:
        return created

    slug = created.get("slug", "")
    return {
        **created,
        "url": build_live_url(slug) if slug else None,
        "category_auto_applied": bool(category_id),
        "data_source": data_source,
        "featured_image_url": final_featured_image_url,
        "header_auto_generated": featured_image_url is None and bool(final_featured_image_url),
        "header_result": generated_header,
        "style_guide_path": str(_article_review_guide_path()),
        "style_guide_loaded": bool(style_guide),
        **article["diagnostics"],
        "admin_note": (
            "Draft created via create_model_review_draft from full benchmark export JSON. "
            "Use update_blog_post for refinements, then publish_blog_post when ready."
        ),
    }


@mcp.tool()
async def create_monthly_newsletter_draft(
    days_back: int = 30,
    selection: str = "overall_score",
    top_spotlights: int = 2,
    month_label: str | None = None,
) -> dict[str, Any]:
    """Create a draft insights post for the monthly newsletter digest.

    Pulls the public leaderboard, keeps runs whose ``completed_at`` falls within
    the last ``days_back`` days, picks the top ``top_spotlights`` models by
    ``selection`` (``overall_score`` or ``tier1_score``), and lists every model
    published in that window. Generates and uploads a dedicated **newsletter hero**
    SVG (homepage-inspired layout; dateline from ``month_label``) for
    ``featured_image_url`` on every draft.

    Requires the same blog API key permissions as ``create_blog_draft``.
    Assigns the **Newsletters** blog category when it exists on the site.
    """
    from datetime import datetime, timezone  # noqa: PLC0415

    from gcb_mcp.blog import build_live_url, create_post, generate_slug, list_posts  # noqa: PLC0415
    from gcb_mcp.header_svg import generate_and_upload_newsletter_header  # noqa: PLC0415
    from gcb_mcp.newsletter import (  # noqa: PLC0415
        build_newsletter_markdown,
        build_spotlight_paragraphs,
        filter_and_rank_models,
        index_posts_by_model_id,
    )
    from gcb_mcp.public_api import list_published_models  # noqa: PLC0415

    if selection not in ("overall_score", "tier1_score"):
        return {
            "error": "invalid_argument",
            "message": "selection must be 'overall_score' or 'tier1_score'",
        }
    if days_back < 1 or days_back > 120:
        return {"error": "invalid_argument", "message": "days_back must be between 1 and 120"}
    if top_spotlights < 1 or top_spotlights > 10:
        return {"error": "invalid_argument", "message": "top_spotlights must be between 1 and 10"}

    lb = await list_published_models(limit=100)
    if "error" in lb:
        return lb

    models = lb.get("models") or []
    by_date, by_score = filter_and_rank_models(
        models,
        days_back=days_back,
        selection=selection,  # type: ignore[arg-type]
    )

    if not by_score:
        return {
            "error": "empty_window",
            "message": (
                f"No leaderboard publications in the last {days_back} days. "
                "Widen the window or wait for new tests to publish."
            ),
        }

    spotlight: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for entry in by_score:
        mid = entry.get("model_id")
        if not mid or mid in seen_ids:
            continue
        seen_ids.add(str(mid))
        spotlight.append(entry)
        if len(spotlight) >= top_spotlights:
            break

    all_items: list[dict[str, Any]] = []
    offset = 0
    total: int | None = None
    while True:
        batch = await list_posts(status="published", limit=100, offset=offset)
        if "error" in batch:
            return batch
        items = batch.get("items") or []
        all_items.extend(items)
        if total is None:
            total = int(batch.get("total") or len(items))
        if len(items) < 100 or offset + len(items) >= total or len(all_items) >= 800:
            break
        offset += 100

    post_by_model = index_posts_by_model_id(all_items)

    label = month_label or datetime.now(timezone.utc).strftime("%B %Y")
    spotlight_paragraphs = await build_spotlight_paragraphs(spotlight)
    title, excerpt, content = build_newsletter_markdown(
        month_label=label,
        window_days=days_back,
        selection=selection,  # type: ignore[arg-type]
        spotlight=spotlight,
        post_by_model=post_by_model,
        spotlight_paragraphs=spotlight_paragraphs,
    )

    header_result = await generate_and_upload_newsletter_header(month_label=label)
    featured: str | None = header_result.get("url") if "error" not in header_result else None

    category_id = await _newsletters_category_id()
    category_ids = [category_id] if category_id else []

    model_ids_union: list[str] = []
    for m in by_date[:50]:
        mid = m.get("model_id")
        if mid and str(mid) not in model_ids_union:
            model_ids_union.append(str(mid))

    slug_hint = await generate_slug(title)
    slug_val = slug_hint.get("slug") if isinstance(slug_hint, dict) else None

    created = await create_post(
        title=title,
        content=content,
        excerpt=excerpt,
        slug=slug_val,
        featured_image_url=featured,
        category_ids=category_ids,
        model_ids=model_ids_union,
        publish=False,
    )
    if "error" in created:
        return created

    slug = created.get("slug", "")
    out: dict[str, Any] = {
        **created,
        "url": build_live_url(slug) if slug else None,
        "window_models_count": len(by_date),
        "spotlight_model_ids": [m.get("model_id") for m in spotlight],
        "newsletters_category_applied": bool(category_id),
        "newsletter_header_dateline": header_result.get("dateline"),
        "admin_note": (
            "Draft newsletter created. Human-review with get_blog_post / update_blog_post, "
            "then publish_blog_post. For email: render_newsletter_email_html, then "
            "send_newsletter_to_subscribers (dry_run first; requires admin API key)."
        ),
    }
    if "error" in header_result:
        out["newsletter_header_error"] = header_result.get("message") or header_result.get("error")
        out["admin_note"] += (
            " Newsletter hero image upload failed; featured_image_url is unset — "
            "fix API/upload then run generate_and_upload_newsletter_header and update_blog_post."
        )
    return out


def _maybe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _model_result_has_public_data(result: dict[str, Any]) -> bool:
    """Return True when a model payload has enough published context to draft from."""
    return any(
        result.get(key) is not None
        for key in (
            "name",
            "provider",
            "overall_score",
            "tier1_score",
            "tier2_score",
            "tier3_score",
            "test_run_id",
            "completed_at",
            "description",
        )
    )


def _highlight_family_tokens(model: dict[str, Any]) -> set[str]:
    """Return stable tokens for grouping nearby model-family comparisons."""
    model_id = str(model.get("model_id") or "")
    name = str(model.get("name") or "")
    tail = model_id.split("/", 1)[-1]
    text = f"{tail} {name}".lower()
    tokens = set(re.findall(r"[a-z]+", text))
    return {
        token
        for token in tokens
        if len(token) >= 3 and token not in {"model", "fast", "latest", "preview", "instruct", "chat"}
    }


async def _highlight_comparison_models(target: dict[str, Any], *, limit: int = 6) -> tuple[list[dict[str, Any]], str]:
    """Choose same-family comparison rows, falling back to nearest overall scores."""
    from gcb_mcp.public_api import list_published_models as _list_published  # noqa: PLC0415

    target_id = str(target.get("model_id") or "")
    target_provider = str(target.get("provider") or (target_id.split("/")[0] if "/" in target_id else "")).lower()
    target_score = _maybe_float(target.get("overall_score") if target.get("overall_score") is not None else target.get("score"))
    target_tokens = _highlight_family_tokens(target)

    listed = await _list_published(limit=100)
    if "error" in listed:
        row = dict(target)
        row["is_target"] = True
        return [row], "GCB OVERALL SCORE"

    entries = [entry for entry in (listed.get("models") or []) if isinstance(entry, dict)]
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        entry_id = str(entry.get("model_id") or "")
        if entry_id:
            by_id[entry_id] = dict(entry)
    if target_id:
        by_id[target_id] = {**by_id.get(target_id, {}), **target}
    entries = list(by_id.values())

    def row_score(row: dict[str, Any]) -> float | None:
        return _maybe_float(row.get("overall_score") if row.get("overall_score") is not None else row.get("score"))

    def with_target_flag(rows: list[dict[str, Any]], subtitle: str) -> tuple[list[dict[str, Any]], str]:
        for row in rows:
            row["is_target"] = str(row.get("model_id") or "") == target_id
        if not any(row.get("is_target") for row in rows):
            target_row = dict(target)
            target_row["is_target"] = True
            rows.append(target_row)
        rows.sort(key=lambda row: (row_score(row) is None, -(row_score(row) or 0)))
        return rows[:limit], subtitle

    family: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = str(entry.get("model_id") or "")
        entry_provider = str(entry.get("provider") or (entry_id.split("/", 1)[0] if "/" in entry_id else "")).lower()
        if target_provider and entry_provider != target_provider:
            continue
        overlap = len(target_tokens & _highlight_family_tokens(entry))
        if entry_id == target_id or overlap >= 2:
            family.append(dict(entry))
    if len(family) >= 2:
        return with_target_flag(family, "GCB OVERALL SCORE - MODEL FAMILY")

    if target_score is None:
        nearest = [dict(entry) for entry in entries if str(entry.get("model_id") or "") == target_id]
    else:
        nearest = sorted(
            [dict(entry) for entry in entries if row_score(entry) is not None],
            key=lambda entry: abs((row_score(entry) or 0) - target_score),
        )[:limit]
    return with_target_flag(nearest, "GCB OVERALL SCORE - NEAREST MODELS")


def _extract_model_id_from_text(text: str) -> str | None:
    match = re.search(r"\b[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._:-]*\b", text.lower())
    return match.group(0) if match else None


async def _list_highlight_candidate_posts(query: str, model_id: str | None) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Fetch blog posts likely to identify source reviews or existing Highlights."""
    import gcb_mcp.blog as blog  # noqa: PLC0415

    posts_by_id: dict[str, dict[str, Any]] = {}
    first_error: dict[str, Any] | None = None

    batches: list[dict[str, Any]] = []
    if model_id:
        batches.append(await blog.list_posts(limit=100, model_id=model_id))
    batches.append(await blog.list_posts(limit=100))

    for batch in batches:
        if "error" in batch:
            if first_error is None:
                first_error = batch
            continue
        for post in batch.get("items") or []:
            if isinstance(post, dict):
                post_id = str(post.get("id") or "")
                if post_id:
                    posts_by_id[post_id] = post

    lookup = query.strip()
    extracted = None
    try:
        from gcb_mcp.highlight import extract_slug_or_query  # noqa: PLC0415

        extracted = extract_slug_or_query(lookup)
    except Exception:
        extracted = lookup
    if extracted and extracted != lookup:
        for batch in (await blog.list_posts(status="published", limit=100), await blog.list_posts(status="draft", limit=100)):
            if "error" in batch:
                if first_error is None:
                    first_error = batch
                continue
            for post in batch.get("items") or []:
                if isinstance(post, dict):
                    post_id = str(post.get("id") or "")
                    if post_id:
                        posts_by_id[post_id] = post

    return list(posts_by_id.values()), first_error


async def _resolve_model_highlight_context_impl(query: str) -> dict[str, Any]:
    """Discover model, source review, and duplicate Highlight context."""
    from gcb_mcp.highlight import (  # noqa: PLC0415
        compact_post,
        extract_slug_or_query,
        is_highlight_post,
        match_score,
        related_model_ids,
    )
    from gcb_mcp.public_api import list_published_models as _list_published  # noqa: PLC0415

    raw_query = str(query or "").strip()
    if not raw_query:
        return {"error": "invalid_argument", "message": "query must not be empty"}

    lookup = extract_slug_or_query(raw_query)
    is_url_query = raw_query.startswith("http://") or raw_query.startswith("https://")
    query_model_id = _extract_model_id_from_text(lookup)
    if not query_model_id and not is_url_query:
        query_model_id = _extract_model_id_from_text(raw_query)
    model_id = query_model_id
    discovery_errors: list[dict[str, Any]] = []

    model_result: dict[str, Any] | None = None
    if model_id:
        result = await _fetch_model_result_for_review(model_id)
        if "error" in result:
            discovery_errors.append(result)
        elif _model_result_has_public_data(result):
            model_result = result

    posts, blog_error = await _list_highlight_candidate_posts(raw_query, model_id)
    if blog_error:
        discovery_errors.append(blog_error)

    scored_posts = sorted(
        posts,
        key=lambda p: max(
            match_score(lookup, p.get("title"), p.get("slug")),
            1.0 if model_id and model_id in related_model_ids(p) else 0.0,
        ),
        reverse=True,
    )
    matched_posts = [
        p for p in scored_posts
        if max(
            match_score(lookup, p.get("title"), p.get("slug")),
            1.0 if model_id and model_id in related_model_ids(p) else 0.0,
        ) >= 0.55
    ]

    if not model_id:
        for post in matched_posts:
            linked = related_model_ids(post)
            if linked:
                model_id = linked[0]
                break
            extracted = _extract_model_id_from_text(str(post.get("title") or ""))
            if extracted:
                model_id = extracted
                break

    leaderboard_match: dict[str, Any] | None = None
    lb = await _list_published(limit=100)
    if "error" in lb:
        discovery_errors.append(lb)
    else:
        for entry in lb.get("models") or []:
            if not isinstance(entry, dict):
                continue
            entry_id = str(entry.get("model_id") or "")
            if model_id and entry_id == model_id:
                leaderboard_match = entry
                break
        if not model_id:
            ranked = sorted(
                [
                    entry for entry in (lb.get("models") or [])
                    if isinstance(entry, dict)
                ],
                key=lambda entry: match_score(
                    lookup,
                    entry.get("model_id"),
                    entry.get("name"),
                    entry.get("provider"),
                ),
                reverse=True,
            )
            if ranked and match_score(lookup, ranked[0].get("model_id"), ranked[0].get("name"), ranked[0].get("provider")) >= 0.62:
                leaderboard_match = ranked[0]
                model_id = str(ranked[0].get("model_id") or "")

    if model_id and (model_result is None or not _model_result_has_public_data(model_result)):
        result = await _fetch_model_result_for_review(model_id)
        if "error" in result:
            discovery_errors.append(result)
        else:
            model_result = result

    if leaderboard_match and model_result is not None:
        for key, value in leaderboard_match.items():
            if model_result.get(key) is None:
                model_result[key] = value
    elif leaderboard_match:
        model_result = dict(leaderboard_match)

    if model_id and model_result is None:
        model_result = {"model_id": model_id}
    if model_result is not None and model_id and not model_result.get("model_id"):
        model_result["model_id"] = model_id

    existing_highlight = next((p for p in matched_posts if is_highlight_post(p)), None)
    review_post = next((p for p in matched_posts if not is_highlight_post(p)), None)

    if model_id and not review_post:
        for post in posts:
            if not is_highlight_post(post) and model_id in related_model_ids(post):
                review_post = post
                break

    if model_id and not existing_highlight:
        for post in posts:
            if is_highlight_post(post) and model_id in related_model_ids(post):
                existing_highlight = post
                break

    if existing_highlight:
        recommended_action = "update_existing_highlight"
    elif model_result and _model_result_has_public_data(model_result):
        recommended_action = "create_highlight_draft"
    elif review_post and model_id:
        recommended_action = "create_highlight_draft_from_review"
    elif model_id:
        recommended_action = "run_benchmark_or_fix_api"
    else:
        recommended_action = "need_more_context"

    return {
        "query": raw_query,
        "resolved_model_id": model_id,
        "model": model_result,
        "published_review_post": compact_post(review_post) if review_post else None,
        "existing_highlight_post": compact_post(existing_highlight) if existing_highlight else None,
        "matched_posts": [compact_post(p) for p in matched_posts[:5]],
        "recommended_action": recommended_action,
        "discovery_errors": discovery_errors,
    }


@mcp.tool()
async def resolve_model_highlight_context(query: str) -> dict[str, Any]:
    """Resolve Highlight drafting context from a model ID, title, slug, URL, or fuzzy query.

    Use this before creating Highlight emails. It discovers the normalized model_id,
    linked published review post, existing Highlight draft/published post, and the
    recommended next action so agents do not mistake transient API failures for
    absent resources.
    """
    return await _resolve_model_highlight_context_impl(query)


@mcp.tool()
async def create_model_highlight_draft(
    model_id: str,
    featured_image_url: str | None = None,
    auto_generate_header: bool = True,
    auto_generate_chart: bool = True,
) -> dict[str, Any]:
    """Create a brief email-first model Highlight draft.

    Pulls the public model result, generates a hosted Highlight header and
    comparison chart when requested, saves a draft insights post, and links it to the
    benchmark model. The draft is intentionally short so it can be sent as email
    after human review, publication, and a dry run.
    """
    import gcb_mcp.blog as blog  # noqa: PLC0415
    import gcb_mcp.header_svg as header_svg  # noqa: PLC0415
    from gcb_mcp.highlight import build_highlight_markdown  # noqa: PLC0415

    context = await _resolve_model_highlight_context_impl(model_id)
    if "error" in context:
        return context
    if context.get("existing_highlight_post"):
        return {
            "error": "highlight_already_exists",
            "message": (
                "A Highlight post already appears to exist for this query. "
                "Use get_blog_post/update_blog_post or send_highlight_to_subscribers with the existing post."
            ),
            "context": context,
        }

    resolved_model_id = context.get("resolved_model_id") or model_id
    result = context.get("model") if isinstance(context.get("model"), dict) else {}
    if not resolved_model_id:
        return {
            "error": "model_not_resolved",
            "message": "Could not resolve a model_id from the query.",
            "context": context,
        }
    if not _model_result_has_public_data(result):
        return {
            "error": "insufficient_highlight_context",
            "message": (
                "Could not fetch published model data or a linked review post with enough context "
                "to create a Highlight draft."
            ),
            "context": context,
        }
    model_id = str(resolved_model_id)
    result["model_id"] = model_id

    name = str(result.get("name") or model_id)
    provider = str(result.get("provider") or (model_id.split("/")[0] if "/" in model_id else "unknown"))

    chart_result: dict[str, Any] = {}
    chart_url: str | None = None
    if auto_generate_chart:
        comparison_models, comparison_subtitle = await _highlight_comparison_models(result)
        chart_result = await header_svg.generate_and_upload_highlight_comparison_chart(
            model_name=name,
            comparison_models=comparison_models,
            subtitle=comparison_subtitle,
        )
        if "error" not in chart_result:
            chart_url = chart_result.get("url")

    title, excerpt, content = build_highlight_markdown(
        model_result=result,
        chart_url=chart_url,
        source_post=context.get("published_review_post"),
    )

    header_result: dict[str, Any] = {}
    featured = featured_image_url
    header_auto_generated = False
    if not featured and auto_generate_header:
        header_result = await header_svg.generate_and_upload_highlight_header(
            model_name=name,
            provider_name=provider,
            score=_maybe_float(result.get("overall_score")),
            model_id=model_id,
        )
        if "error" not in header_result:
            featured = header_result.get("url")
            header_auto_generated = bool(featured)

    category_id = await _highlights_category_id()
    category_ids = [category_id] if category_id else []

    slug_hint = await blog.generate_slug(title)
    slug_val = slug_hint.get("slug") if isinstance(slug_hint, dict) else None

    created = await blog.create_post(
        title=title,
        content=content,
        excerpt=excerpt,
        slug=slug_val,
        featured_image_url=featured,
        category_ids=category_ids,
        model_ids=[model_id],
        publish=False,
    )
    if "error" in created:
        return created

    slug = created.get("slug", "")
    out: dict[str, Any] = {
        **created,
        "url": blog.build_live_url(slug) if slug else None,
        "model_id": model_id,
        "highlight_context": context,
        "highlight_header_auto_generated": header_auto_generated,
        "highlight_chart_auto_generated": bool(chart_url),
        "highlight_chart_url": chart_url,
        "highlights_category_applied": bool(category_id),
        "admin_note": (
            "Draft Highlight created. Human-review with get_blog_post / update_blog_post, "
            "then publish_blog_post. For email: render_highlight_email_html, then "
            "send_highlight_to_subscribers (dry_run first; requires admin API key)."
        ),
    }
    if "error" in header_result:
        out["highlight_header_error"] = header_result.get("message") or header_result.get("error")
        out["admin_note"] += (
            " Highlight header upload failed; featured_image_url is unset unless you supplied one."
        )
    if "error" in chart_result:
        out["highlight_chart_error"] = chart_result.get("message") or chart_result.get("error")
        out["admin_note"] += (
            " Highlight chart upload failed; regenerate it with generate_and_upload_highlight_chart "
            "and add the returned URL to the draft content."
        )
    if not category_id:
        out["admin_note"] += " Highlights category was not found, so no category was assigned."
    return out


@mcp.tool()
async def list_blog_posts(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    model_id: str | None = None,
) -> dict[str, Any]:
    """List GCB blog posts, optionally filtered by status.

    Args:
        status: Filter by 'draft' | 'published'. Omit for all posts.
        limit:  Maximum number of posts to return (default 20, max 100).
        offset: Pagination offset (default 0).
        model_id: When set, only posts linked to this OpenRouter model_id (e.g. openai/gpt-4o).

    Returns a list with id, title, slug, status, excerpt, created_at for each post.
    """
    from gcb_mcp.blog import list_posts  # noqa: PLC0415

    valid = {None, "draft", "published"}
    if status not in valid:
        return {"error": "invalid_argument", "message": "status must be 'draft', 'published', or omitted"}
    return await list_posts(status=status, limit=limit, offset=offset, model_id=model_id)


@mcp.tool()
async def get_blog_post(post_id: str) -> dict[str, Any]:
    """Fetch a single blog post by UUID, including its full markdown content.

    Use this to retrieve a draft for editing or copy-editing.

    Args:
        post_id: UUID of the blog post (from list_blog_posts or create_blog_draft).
    """
    from gcb_mcp.blog import get_post  # noqa: PLC0415

    return await get_post(post_id=post_id)


@mcp.tool()
async def create_blog_draft(
    title: str,
    content: str,
    excerpt: str | None = None,
    slug: str | None = None,
    featured_image_url: str | None = None,
    category_ids: list[str] | None = None,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new GCB blog post as a draft (never auto-publishes).

    Typical usage: after generating an article, call this to save it to the
    live site as a draft for review before publishing.

    Args:
        title:             Article title (max 255 chars).
        content:           Full article body in markdown.
        excerpt:           1–2 sentence summary for listing pages.
                           Auto-extracted from first paragraph if omitted.
        slug:              URL slug (e.g. "gpt-4o-benchmark-review").
                           Auto-generated from title if omitted.
        featured_image_url: JSON string, full https URL of the header image from
            generate_and_upload_header (must be quoted in the tool arguments object).
        category_ids:      List of category UUIDs. Use list_blog_categories() to find IDs.
        model_ids:         List of OpenRouter model identifiers (e.g. ["openai/gpt-4o"])
                           to cross-reference this article with benchmark model pages.
                           Visitors will see links between the article and model detail pages.

    Returns:
        {id, title, slug, status, url}
    """
    from gcb_mcp.blog import build_live_url, create_post  # noqa: PLC0415

    result = await create_post(
        title=title,
        content=content,
        excerpt=excerpt,
        slug=slug,
        featured_image_url=featured_image_url,
        category_ids=category_ids or [],
        model_ids=model_ids or [],
        publish=False,
    )

    if "error" in result:
        return result

    post_slug = result.get("slug", "")
    return {
        **result,
        "url": build_live_url(post_slug) if post_slug else None,
        "admin_note": "Post created as draft. Call publish_blog_post(id) when ready to go live.",
    }


@mcp.tool()
async def update_blog_post(
    post_id: str,
    content: str | None = None,
    title: str | None = None,
    excerpt: str | None = None,
    featured_image_url: str | None = None,
    slug: str | None = None,
    category_ids: list[str] | None = None,
    model_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing blog post (draft or published).

    Only the fields you supply are changed — omitted fields are left as-is.
    Use this for the edit / copy-edit loop: fetch the post with get_blog_post,
    revise the content, then call this to save changes.

    Args:
        post_id:           UUID of the post to update.
        content:           Revised markdown body.
        title:             New title.
        excerpt:           New excerpt.
        featured_image_url: New header image URL as a JSON string (quoted https URL).
        slug:              New URL slug (must be unique).
        category_ids:      Replace category list with these UUIDs.
        model_ids:         Replace linked models with these OpenRouter model identifiers
                           (e.g. ["openai/gpt-4o"]). Pass empty list to unlink all models.
    """
    from gcb_mcp.blog import update_post  # noqa: PLC0415

    return await update_post(
        post_id=post_id,
        content=content,
        title=title,
        excerpt=excerpt,
        featured_image_url=featured_image_url,
        slug=slug,
        category_ids=category_ids,
        model_ids=model_ids,
    )


@mcp.tool()
async def publish_blog_post(post_id: str) -> dict[str, Any]:
    """Publish a draft blog post to the live GCB website.

    This is the final step of the article authoring workflow. The post will
    appear at greatcommissionbenchmark.ai/insights/{slug}.

    Args:
        post_id: UUID of the draft post to publish.
    """
    from gcb_mcp.blog import build_live_url, publish_post  # noqa: PLC0415

    result = await publish_post(post_id=post_id)
    if "error" in result:
        return result

    slug = result.get("slug", "")
    return {
        **result,
        "live_url": build_live_url(slug) if slug else None,
    }


@mcp.tool()
async def list_blog_categories() -> dict[str, Any]:
    """List all available GCB blog categories with their UUIDs.

    Use category UUIDs in create_blog_draft or update_blog_post.
    Model review articles typically use the "Model Reviews" category.
    """
    from gcb_mcp.blog import list_categories  # noqa: PLC0415

    return await list_categories()


@mcp.tool()
async def render_newsletter_email_html(post_id: str) -> dict[str, Any]:
    """Render a blog post as sanitized HTML suitable for email distribution.

    Calls ``GET /api/admin/newsletter/preview-html`` using the configured GCB API key.
    The key's user must have **can_admin** (same as other admin newsletter tools).

    Args:
        post_id: UUID of the insights post (draft or published).
    """
    from gcb_mcp.admin_api import preview_newsletter_html  # noqa: PLC0415

    return await preview_newsletter_html(post_id=post_id)


@mcp.tool()
async def render_highlight_email_html(post_id: str) -> dict[str, Any]:
    """Render a Highlight blog post as sanitized HTML suitable for email distribution."""
    from gcb_mcp.admin_api import preview_newsletter_html  # noqa: PLC0415

    return await preview_newsletter_html(post_id=post_id)


@mcp.tool()
async def send_newsletter_to_subscribers(
    post_id: str,
    dry_run: bool = True,
    audience: str = "test",
    confirm_production_send: bool = False,
    force_resend: bool = False,
) -> dict[str, Any]:
    """Send newsletter to test or production MailerLite audience.

    Always run with ``dry_run=true`` first after human approval. A real
    production send (``audience='production'`` and ``dry_run=false``) requires
    a published post and ``confirm_production_send=true``.

    Args:
        post_id: UUID of the insights post.
        dry_run: When true (default), only validates subscriber counts and configuration.
        audience: ``test`` (default) or ``production``.
        confirm_production_send: Required for production sends.
        force_resend: Override duplicate-send protection for production.
    """
    from gcb_mcp.admin_api import send_newsletter_campaign_v2  # noqa: PLC0415

    return await send_newsletter_campaign_v2(
        post_id=post_id,
        dry_run=dry_run,
        audience=audience,
        confirm_production_send=confirm_production_send,
        force_resend=force_resend,
    )


@mcp.tool()
async def send_highlight_to_subscribers(
    post_id: str,
    dry_run: bool = True,
    audience: str = "test",
    confirm_production_send: bool = False,
    force_resend: bool = False,
) -> dict[str, Any]:
    """Send a Highlight post to test or production newsletter audiences.

    Uses the same recipient lists and safety gates as newsletter sends, but logs
    the send as ``campaign_type='highlight'`` for duplicate protection and audit
    clarity.
    """
    from gcb_mcp.admin_api import send_newsletter_campaign_v2  # noqa: PLC0415

    return await send_newsletter_campaign_v2(
        post_id=post_id,
        dry_run=dry_run,
        audience=audience,
        confirm_production_send=confirm_production_send,
        force_resend=force_resend,
        campaign_type="highlight",
    )


@mcp.tool()
async def list_newsletter_test_recipients(
    status: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List admin-managed newsletter test recipients."""
    from gcb_mcp.admin_api import list_newsletter_test_recipients as _list  # noqa: PLC0415

    return await _list(status=status, search=search, limit=limit, offset=offset)


@mcp.tool()
async def add_newsletter_test_recipient(
    email: str,
    name: str | None = None,
    notes: str | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """Add a managed newsletter test recipient."""
    from gcb_mcp.admin_api import create_newsletter_test_recipient as _create  # noqa: PLC0415

    return await _create(email=email, name=name, notes=notes, is_active=is_active)


@mcp.tool()
async def update_newsletter_test_recipient(
    recipient_id: str,
    email: str | None = None,
    name: str | None = None,
    notes: str | None = None,
    is_active: bool | None = None,
) -> dict[str, Any]:
    """Update a managed newsletter test recipient."""
    from gcb_mcp.admin_api import update_newsletter_test_recipient as _update  # noqa: PLC0415

    return await _update(
        recipient_id=recipient_id,
        email=email,
        name=name,
        notes=notes,
        is_active=is_active,
    )


@mcp.tool()
async def remove_newsletter_test_recipient(recipient_id: str) -> dict[str, Any]:
    """Deactivate a managed newsletter test recipient."""
    from gcb_mcp.admin_api import delete_newsletter_test_recipient as _delete  # noqa: PLC0415

    return await _delete(recipient_id=recipient_id)


@mcp.tool()
async def generate_and_upload_header(
    model_name: str,
    provider_name: str,
    score: float | None = None,
    model_version: str | None = None,
    accent_color: str | None = None,
    tier1_score: float | None = None,
    tier2_score: float | None = None,
    tier3_score: float | None = None,
) -> dict[str, Any]:
    """Generate a programmatic SVG article header image and upload it to GCB storage.

    Returns a hosted URL ready to pass as featured_image_url to create_blog_draft.

    The SVG contains:
    - Dark gradient background with radial accent glow
    - GCB logomark (left)
    - Provider logo or letter monogram (right)
    - Model name, score, and optional tier score pills (all live SVG text)
    - Provider-specific accent colour (auto-detected or overridden)

    No LLM image generation, no browser screenshot, no external image fetch.

    Args:
        model_name:    Full display name, e.g. "GPT-5 Mini" or "Kimi K2.5"
        provider_name: Provider slug or name, e.g. "openai", "Moonshot AI"
                       Used to select logo and accent colour automatically.
        score:         Overall GCB score (0–100).
        model_version: Short version string shown large, e.g. "5 Mini", "K2.5".
                       Auto-derived from model_name if omitted.
        accent_color:  CSS hex colour override (e.g. "#ff7000").
                       Inferred from provider if omitted.
        tier1_score:   Tier 1 raw score (0–100) for the pill row.
        tier2_score:   Tier 2 raw score.
        tier3_score:   Tier 3 raw score.

    Returns:
        {url, svg_path, filename, provider_color}
    """
    from gcb_mcp.header_svg import generate_and_upload  # noqa: PLC0415

    return await generate_and_upload(
        model_name=model_name,
        provider_name=provider_name,
        score=score,
        model_version=model_version,
        accent_color=accent_color,
        tier1_score=tier1_score,
        tier2_score=tier2_score,
        tier3_score=tier3_score,
    )


@mcp.tool()
async def generate_and_upload_newsletter_header(month_label: str | None = None) -> dict[str, Any]:
    """Generate the monthly newsletter hero SVG and upload it to GCB storage.

    Visual style follows the public homepage hero (dark diagonal wash, red glow,
    faint grid). Fixed copy: **Great Commission Benchmark**, **Evaluating AI for
    the Great Commission**, plus a dateline derived from ``month_label`` (e.g.
    ``April 2026`` → ``April, 2026``) or the current UTC month when omitted.

    Returns ``{url, svg_path, filename, dateline}`` on success, or ``error`` /
    ``message`` when upload fails.

    ``create_monthly_newsletter_draft`` calls this automatically for every new digest.
    """
    from gcb_mcp.header_svg import generate_and_upload_newsletter_header as _gen  # noqa: PLC0415

    return await _gen(month_label=month_label)


@mcp.tool()
async def generate_and_upload_highlight_header(model_id: str) -> dict[str, Any]:
    """Generate and upload the model Highlight header SVG for a published GCB model."""
    import gcb_mcp.header_svg as header_svg  # noqa: PLC0415

    result = await _fetch_model_result_for_review(model_id)
    if "error" in result:
        return result
    return await header_svg.generate_and_upload_highlight_header(
        model_name=str(result.get("name") or model_id),
        provider_name=str(result.get("provider") or (model_id.split("/")[0] if "/" in model_id else "unknown")),
        score=_maybe_float(result.get("overall_score")),
        model_id=model_id,
    )


@mcp.tool()
async def generate_and_upload_highlight_chart(model_id: str) -> dict[str, Any]:
    """Generate and upload the model Highlight overall-score comparison chart SVG."""
    import gcb_mcp.header_svg as header_svg  # noqa: PLC0415

    result = await _fetch_model_result_for_review(model_id)
    if "error" in result:
        return result
    comparison_models, comparison_subtitle = await _highlight_comparison_models(result)
    return await header_svg.generate_and_upload_highlight_comparison_chart(
        model_name=str(result.get("name") or model_id),
        comparison_models=comparison_models,
        subtitle=comparison_subtitle,
    )


@mcp.tool()
async def get_local_test_json(job_id: str) -> dict[str, Any]:
    """Return the full gcb-runner export JSON for a locally-run benchmark test.

    This is the richest source of article-writing material. It contains:
    - All 150 individual model responses (full text)
    - Judge reasoning for every verdict
    - Exact verdict counts per category (e.g. "9 Accepted, 2 Compromised, 4 Refused in 1.1")
    - Overall verdict_counts summary (Accepted / Compromised / Refused totals)
    - Test run metadata (model, benchmark version, judge model, completed_at)

    Use this instead of (or alongside) get_model_test_result() when writing a
    benchmark review article for a model you tested locally. The response text
    in each entry enables deep pattern analysis: repeated refusal phrasing,
    identity breaks, politically sensitive refusals, theological hedging patterns.

    Args:
        job_id: The job UUID returned by start_gcb_test(). Use list_jobs() to
                find available job IDs. Only jobs with status 'succeeded' will
                have a complete export file.

    Returns a dict with keys:
        format_version, test_run, summary (with verdict_counts, tier_scores),
        responses (list of 150 entries with response text + verdict + judge_reasoning),
        category_breakdown (per-category exact counts, computed client-side),
        error (if job not found or export file missing)
    """
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    manager = JobManager()
    job = manager.get_job(job_id)

    if job is None:
        # Also search by model_id prefix in case caller passed a model slug
        all_jobs = manager.list_jobs(status="succeeded", limit=100)
        matches = [j for j in all_jobs if job_id.lower() in j.model_id.lower()]
        if len(matches) == 1:
            job = matches[0]
        elif len(matches) > 1:
            return {
                "error": "ambiguous_match",
                "message": (
                    f"'{job_id}' matches multiple jobs: "
                    + ", ".join(f"{j.id} ({j.model_id})" for j in matches[:5])
                    + ". Use the exact job_id."
                ),
            }
        else:
            return {
                "error": "job_not_found",
                "message": (
                    f"No job found with id or model_id containing '{job_id}'. "
                    "Use list_jobs() to see available jobs."
                ),
            }

    if job.status != "succeeded":
        return {
            "error": "job_not_succeeded",
            "job_id": job.id,
            "model_id": job.model_id,
            "status": job.status,
            "message": (
                f"Job is '{job.status}' — export JSON is only available for succeeded jobs."
            ),
        }

    # Resolve export file path
    export_path: Path | None = None
    if job.export_path:
        export_path = Path(job.export_path)

    if export_path is None or not export_path.exists():
        # Fall back to convention-based path
        from gcb_mcp.jobs import _get_jobs_dir  # noqa: PLC0415

        export_path = _get_jobs_dir() / f"{job.id}-export.json"

    if not export_path.exists():
        return {
            "error": "export_not_found",
            "job_id": job.id,
            "model_id": job.model_id,
            "message": (
                f"Export file not found at {export_path}. "
                "The file may have been deleted or the path changed."
            ),
        }

    try:
        raw = json.loads(export_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": "read_error", "message": str(exc), "path": str(export_path)}

    # Build per-category breakdown so the agent doesn't have to iterate manually
    responses = raw.get("responses", [])
    category_breakdown: dict[str, dict] = {}
    refusal_openings: list[str] = []

    for resp in responses:
        cat = resp.get("category", "unknown")
        verdict = resp.get("verdict", "UNKNOWN")
        if cat not in category_breakdown:
            category_breakdown[cat] = {
                "ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0,
                "total": 0,
            }
        category_breakdown[cat][verdict] = category_breakdown[cat].get(verdict, 0) + 1
        category_breakdown[cat]["total"] += 1

        # Capture first 12 words of each refusal response for pattern analysis
        if verdict == "REFUSED":
            text = resp.get("response", "")
            opening = " ".join(text.split()[:12])
            if opening:
                refusal_openings.append(opening)

    # Compute per-category pass rates
    for cat, counts in category_breakdown.items():
        total = counts["total"]
        accepted = counts["ACCEPTED"]
        compromised = counts.get("COMPROMISED", 0)
        if total > 0:
            counts["pass_rate"] = round(
                (accepted + 0.5 * compromised) / total * 100, 1
            )

    return {
        **raw,
        "category_breakdown": category_breakdown,
        "refusal_opening_phrases": refusal_openings,
        "export_path": str(export_path),
    }


@mcp.tool()
async def get_remote_test_json(test_run_id: str) -> dict[str, Any]:
    """Fetch the full benchmark export JSON for a submitted test run from the live platform.

    Use this when the original local export file is unavailable — for example when
    writing an article about a historical run that predates the local job database,
    or when you need to recover a run on a different machine.

    Requires an admin platform API key (GCB_API_KEY or ~/.gcb-runner config). Any completed run on the platform can be fetched
    regardless of who originally submitted it.

    The tool applies the same convenience analysis as get_local_test_json:
    - category_breakdown: per-category exact counts (9A / 2C / 4R) + pass_rate
    - refusal_opening_phrases: first words of every refused response for pattern detection

    Args:
        test_run_id: Platform UUID of the test run. Obtain from:
            - get_model_test_result(model_id)["test_run_id"]
            - list_published_models()  → entries include test_run_id
            - The GCB admin dashboard

    Returns a dict with keys:
        format_version, test_run (includes _reconstructed flag if built from DB),
        summary (verdict_counts, tier_scores, score),
        responses (list of entries with response text + verdict + judge_reasoning),
        category_breakdown, refusal_opening_phrases, _source
        error (if the fetch failed or permissions were insufficient)
    """
    from gcb_mcp.blog import fetch_remote_test_export  # noqa: PLC0415

    raw = await fetch_remote_test_export(test_run_id)
    if "error" in raw:
        return raw

    # Apply the same convenience analysis as get_local_test_json
    responses = raw.get("responses", [])
    category_breakdown: dict[str, dict] = {}
    refusal_openings: list[str] = []

    for resp in responses:
        cat = resp.get("category", "unknown")
        verdict = resp.get("verdict", "UNKNOWN")
        if cat not in category_breakdown:
            category_breakdown[cat] = {
                "ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0,
                "total": 0,
            }
        category_breakdown[cat][verdict] = category_breakdown[cat].get(verdict, 0) + 1
        category_breakdown[cat]["total"] += 1

        if verdict == "REFUSED":
            text = resp.get("response", "")
            opening = " ".join(text.split()[:12])
            if opening:
                refusal_openings.append(opening)

    for cat, counts in category_breakdown.items():
        total = counts["total"]
        accepted = counts.get("ACCEPTED", 0)
        compromised = counts.get("COMPROMISED", 0)
        if total > 0:
            counts["pass_rate"] = round(
                (accepted + 0.5 * compromised) / total * 100, 1
            )

    return {
        **raw,
        "category_breakdown": category_breakdown,
        "refusal_opening_phrases": refusal_openings,
        "_source": "remote_platform",
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
