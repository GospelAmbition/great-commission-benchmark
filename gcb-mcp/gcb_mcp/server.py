"""Stdio MCP server: calls GET /api/runner/models on the GCB platform."""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
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
        "preview_archive_candidates and archive_missing_on_openrouter support "
        "archiving models no longer available on OpenRouter. "
        "upload_json and upload_runner_json upload an exported gcb-runner JSON "
        "for direct publish. "
        "check_ready_for_testing verifies LMStudio judge, OpenRouter, and GCB API are ready. "
        "start_gcb_test spawns a background benchmark test and returns a job_id immediately. "
        "get_job_status, list_jobs, get_job_logs, and upload_result monitor and act on jobs. "
        "list_published_models and get_model_test_result fetch published benchmark data from the platform. "
        "list_blog_posts, get_blog_post, create_blog_draft, update_blog_post, and publish_blog_post "
        "manage the GCB blog for agentic article authoring. "
        "create_model_review_draft generates a style-guide aligned benchmark article draft from published model results. "
        "generate_and_upload_header creates a programmatic SVG article header image."
    ),
)


def _base_url() -> str:
    return os.environ.get(
        "GCB_API_BASE_URL", "https://greatcommissionbenchmark.ai"
    ).rstrip("/")


def _api_key() -> str:
    return os.environ.get("GCB_API_KEY", "").strip()


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


@mcp.tool()
async def upload_json(
    export_json_path: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Upload a gcb-runner export JSON for direct publish.

    Uses API-key auth and posts to the runner bulk-submit endpoint. This is
    admin-only and bypasses moderation/payment.
    """
    api_key = _api_key()
    if not api_key:
        return {
            "error": "missing_api_key",
            "message": (
                "Set GCB_API_KEY in MCP env. This endpoint requires an admin "
                "API key for direct publish."
            ),
        }

    try:
        export_data = _load_json_file(export_json_path)
    except FileNotFoundError as exc:
        return {"error": "file_not_found", "message": str(exc)}
    except json.JSONDecodeError as exc:
        return {"error": "invalid_json", "message": f"Invalid JSON: {exc}"}
    except Exception as exc:
        return {"error": "invalid_input", "message": str(exc)}

    test_run = export_data.get("test_run", {})
    summary = export_data.get("summary", {})
    responses = export_data.get("responses", [])
    model = test_run.get("model") if isinstance(test_run, dict) else None
    benchmark_version = (
        test_run.get("benchmark_version") if isinstance(test_run, dict) else None
    )
    score = summary.get("score") if isinstance(summary, dict) else None
    response_count = len(responses) if isinstance(responses, list) else 0

    preview = {
        "path": str(Path(export_json_path).expanduser()),
        "model": model,
        "benchmark_version": benchmark_version,
        "score": score,
        "response_count": response_count,
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
) -> dict[str, Any]:
    """Alias for upload_json with the same behavior."""
    return await upload_json(export_json_path=export_json_path, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Fire-and-forget benchmark test tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def check_ready_for_testing(auto_launch: bool = True) -> dict[str, Any]:
    """Check that all prerequisites for running a GCB benchmark test are ready.

    Verifies:
      - LMStudio is running with the judge model (openai/gpt-oss-20b) loaded.
      - OpenRouter API key is configured and reachable.
      - GCB platform API key is configured for result upload.

    Args:
        auto_launch: If True (default), attempts to start the LMStudio server
            and load the judge model automatically if they are not running.
            Set to False for a read-only status check.

    Returns a dict with a top-level 'ready' bool and per-service details.
    """
    from gcb_mcp.readiness import check_all_ready  # noqa: PLC0415

    return await check_all_ready(auto_launch=auto_launch)


@mcp.tool()
async def start_gcb_test(model_id: str) -> dict[str, Any]:
    """Spawn a background GCB benchmark test for the given OpenRouter model.

    Returns immediately (< 1 second) with a job_id. The test runs in the
    background for 1-2.5 hours. Use get_job_status(job_id) to monitor progress
    and upload_result(job_id) to publish when done.

    Default configuration:
      - Testing backend: OpenRouter (uses configured API key)
      - Judge: LMStudio local, model openai/gpt-oss-20b
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
async def upload_result(job_id: str, dry_run: bool = False) -> dict[str, Any]:
    """Upload a succeeded benchmark test result to the GCB platform.

    Only valid when the job status is 'succeeded' and an export JSON exists.
    Uses the existing admin bulk-submit endpoint (bypasses moderation).

    Args:
        job_id:  The UUID returned by start_gcb_test.
        dry_run: If True, validate the export but do not actually upload.

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

    # Delegate to the existing upload_json tool implementation
    result = await upload_json(export_json_path=job.export_path, dry_run=dry_run)
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
    write an article about. Returns model_id, name, provider, overall score,
    tier scores, completed_at, and test_run_id.

    Args:
        limit: Maximum number of models to return (default 30, max 200).
    """
    from gcb_mcp.public_api import list_published_models as _list  # noqa: PLC0415

    return await _list(limit=limit)


@mcp.tool()
async def get_model_test_result(model_id: str) -> dict[str, Any]:
    """Fetch the full published benchmark result for a model by its OpenRouter model_id.

    Returns the complete structured data needed to write a benchmark review article:
    overall score, tier 1/2/3 scores, all 19 category scores, verdict distribution
    (Accepted / Compromised / Refused), test history, benchmark version, and rank.

    This replaces the manual step of locating and passing a local JSON export file.

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


def _build_model_review_article(result: dict[str, Any], style_guide_loaded: bool) -> dict[str, str]:
    """Build a scan-friendly, style-guide aligned draft article payload."""
    model_id = (result.get("model_id") or "unknown-model").strip()
    provider = (result.get("provider") or "unknown-provider").strip()
    overall = _safe_float(result.get("overall_score"))
    tier1 = _safe_float(result.get("tier1_score"))
    tier2 = _safe_float(result.get("tier2_score"))
    tier3 = _safe_float(result.get("tier3_score"))
    benchmark_version = str(result.get("benchmark_version") or "unknown").strip()
    test_run_id = str(result.get("test_run_id") or "unknown").strip()
    completed = _format_completed_date(result.get("completed_at"))

    verdicts = _normalize_verdict_distribution(result.get("verdict_distribution"))
    total_questions = _safe_int(result.get("total_questions"))
    if total_questions <= 0:
        total_questions = verdicts["accepted"] + verdicts["compromised"] + verdicts["refused"]
    total_questions_text = str(total_questions) if total_questions > 0 else "unknown"

    verdict_line, implication_line = _score_band(overall)
    score_text = f"{overall:.1f}" if overall is not None else "N/A"
    tier1_text = f"{tier1:.1f}" if tier1 is not None else "N/A"
    tier2_text = f"{tier2:.1f}" if tier2 is not None else "N/A"
    tier3_text = f"{tier3:.1f}" if tier3 is not None else "N/A"

    title = f"{model_id}: Great Commission Benchmark v{benchmark_version} Review"
    excerpt = (
        f"{model_id} scored {score_text} on GCB v{benchmark_version}. "
        f"This review summarizes tier performance, verdict patterns, and deployment guidance for ministry teams."
    )

    guide_note = (
        "This draft follows the repository article style guide."
        if style_guide_loaded
        else "Style guide file was not readable at runtime; structure still follows the expected benchmark-review format."
    )

    content = f"""## At a glance

- **Model tested:** `{model_id}` (`{provider}`)
- **Overall GCB score:** **{score_text}** on benchmark version `{benchmark_version}`
- **One-sentence verdict:** {verdict_line}
- **Strategic implication:** {implication_line}
- **Run metadata:** `{total_questions_text}` questions, completed `{completed}`, test run `{test_run_id}`

{guide_note}

## Why this benchmark matters for your ministry team

Large language models (LLMs) can accelerate research, content drafting, and digital ministry workflows. But speed is not the same as alignment. For Great Commission use, we need to evaluate whether a model can support ministry goals without quietly weakening doctrinal clarity or refusing core biblical language.

In this review, we treat the benchmark as a strategic governance signal. We are not asking whether a model is merely capable; we are asking whether it is dependable for disciple-making contexts where truth, clarity, and consistency matter.

## Benchmark snapshot

- **Overall score:** `{score_text}`
- **Tier 1 (Task Capability, 70% weight):** `{tier1_text}`
- **Tier 2 (Doctrinal Fidelity, 20% weight):** `{tier2_text}`
- **Tier 3 (Worldview Confession, 10% weight):** `{tier3_text}`
- **Accepted:** `{verdicts['accepted']}` (`{_fmt_pct(verdicts['accepted'], total_questions)}`)
- **Compromised:** `{verdicts['compromised']}` (`{_fmt_pct(verdicts['compromised'], total_questions)}`)
- **Refused:** `{verdicts['refused']}` (`{_fmt_pct(verdicts['refused'], total_questions)}`)

## Reading the result strategically

- **Tier-weight reality:** Tier 1 drives most of the final score, so practical task performance can mask doctrinal inconsistency unless you inspect Tier 2 and Tier 3 directly.
- **Compromised responses matter:** Compromised outputs often sound usable at first glance but can dilute theological precision through hedging language.
- **Refusal clustering risk:** Refusal behavior in ministry-critical use cases creates workflow interruption and pushes teams toward ad hoc workarounds.
- **Governance signal:** The strongest indicator is not a single score; it is consistency across capability, doctrine, and worldview confession.

## Implications for Great Commission operations

When we evaluate model alignment for ministry settings, we need shared definitions:

- **Guardrails:** Behavior constraints that shape what the model will or will not say.
- **Alignment:** The practical fit between model behavior and your ministry’s theological and operational commitments.
- **Human-in-the-loop:** A review design where trained people approve or correct outputs before distribution.

Given this run, consider the following operating posture:

- Keep human review mandatory for public-facing spiritual guidance and doctrinal statements.
- Use structured prompt standards for repeatable ministry tasks (research briefs, prayer summaries, training drafts).
- Track refusal and compromise incidents in production so policy decisions are based on observed behavior, not assumptions.
- Build escalation paths for content that touches doctrinal claims, repentance language, salvation claims, or evangelistic invitations.

## Suggested deployment posture (30/60/90 day)

- **First 30 days:** Pilot in low-risk internal workflows with explicit QA checklists.
- **By 60 days:** Expand only if refusal and compromise rates are operationally manageable for your team.
- **By 90 days:** Decide whether to broaden adoption, keep constrained usage, or replace with a stronger model profile.

## Biblical and strategic framing

Technology can serve the Church, but it cannot disciple people. Our responsibility is to steward tools in ways that strengthen obedience to Christ, not outsource conviction. As we evaluate AI systems, we should anchor strategy in mission fidelity: “test everything; hold fast what is good” (1 Thessalonians 5:21) while continuing to “make disciples of all nations” (Matthew 28:19-20).

## Final recommendation

{verdict_line} {implication_line}

Use this result as a governance input, not an isolated decision-maker. Pair benchmark evidence with pilot telemetry, theological oversight, and ministry-specific risk controls before scaling.
"""

    return {
        "title": title,
        "excerpt": excerpt,
        "content": content,
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


@mcp.tool()
async def create_model_review_draft(
    model_id: str,
    featured_image_url: str | None = None,
) -> dict[str, Any]:
    """Create a scan-friendly benchmark review draft using the repository style guide.

    Workflow:
      1) Fetch published model benchmark result.
      2) Load insights/_article_review_prompt.md.
      3) Build a guide-aligned markdown review with "At a glance" + bullet-heavy analysis.
      4) Save as a draft blog post and auto-assign "Model Reviews" category when present.

    Args:
        model_id: OpenRouter model identifier (e.g. "z-ai/glm-5.1").
        featured_image_url: Optional hosted image URL for article header.

    Returns:
        Created draft metadata plus diagnostics about guide/category application.
    """
    from gcb_mcp.blog import build_live_url, create_post, generate_slug  # noqa: PLC0415
    from gcb_mcp.public_api import get_model_test_result as _get  # noqa: PLC0415
    from gcb_mcp.public_api import list_published_models as _list  # noqa: PLC0415

    result = await _get(model_id=model_id)
    if "error" in result:
        return result

    # Fill gaps from leaderboard payload where model-by-id endpoint is sparse.
    listed = await _list(limit=100)
    if "error" not in listed:
        for entry in listed.get("models", []):
            if entry.get("model_id") == model_id:
                if not result.get("benchmark_version"):
                    result["benchmark_version"] = entry.get("benchmark_version")
                if not result.get("test_run_id"):
                    result["test_run_id"] = entry.get("test_run_id")
                if not result.get("completed_at"):
                    result["completed_at"] = entry.get("completed_at")
                if not result.get("total_questions"):
                    result["total_questions"] = entry.get("total_questions")
                if not result.get("verdict_distribution"):
                    result["verdict_distribution"] = entry.get("verdict_distribution")
                break

    # Final fallback to latest test_history shape from by-id endpoint.
    test_history = result.get("test_history") or []
    if test_history:
        latest = test_history[0]
        if not result.get("benchmark_version"):
            result["benchmark_version"] = latest.get("benchmark_version")
        if not result.get("test_run_id"):
            result["test_run_id"] = latest.get("test_run_id")
        if not result.get("completed_at"):
            result["completed_at"] = latest.get("completed_at")

    style_guide = _read_article_review_guide()
    article = _build_model_review_article(result=result, style_guide_loaded=bool(style_guide))
    category_id = await _model_reviews_category_id()
    category_ids = [category_id] if category_id else []
    generated_slug = await generate_slug(article["title"])
    slug = generated_slug.get("slug") if isinstance(generated_slug, dict) else None

    created = await create_post(
        title=article["title"],
        content=article["content"],
        excerpt=article["excerpt"],
        slug=slug,
        featured_image_url=featured_image_url,
        category_ids=category_ids,
        publish=False,
    )
    if "error" in created:
        return created

    slug = created.get("slug", "")
    return {
        **created,
        "url": build_live_url(slug) if slug else None,
        "category_auto_applied": bool(category_id),
        "style_guide_path": str(_article_review_guide_path()),
        "style_guide_loaded": bool(style_guide),
        "admin_note": (
            "Draft created via create_model_review_draft with style-guide aligned template. "
            "Use update_blog_post for refinements, then publish_blog_post when ready."
        ),
    }


@mcp.tool()
async def list_blog_posts(
    status: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """List GCB blog posts, optionally filtered by status.

    Args:
        status: Filter by 'draft' | 'published'. Omit for all posts.
        limit:  Maximum number of posts to return (default 20).

    Returns a list with id, title, slug, status, excerpt, created_at for each post.
    """
    from gcb_mcp.blog import list_posts  # noqa: PLC0415

    valid = {None, "draft", "published"}
    if status not in valid:
        return {"error": "invalid_argument", "message": "status must be 'draft', 'published', or omitted"}
    return await list_posts(status=status, limit=limit)


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
        featured_image_url: URL of the header image (from generate_and_upload_header).
        category_ids:      List of category UUIDs. Use list_blog_categories() to find IDs.

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
        featured_image_url: New header image URL.
        slug:              New URL slug (must be unique).
        category_ids:      Replace category list with these UUIDs.
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
    )


@mcp.tool()
async def publish_blog_post(post_id: str) -> dict[str, Any]:
    """Publish a draft blog post to the live GCB website.

    This is the final step of the article authoring workflow. The post will
    appear at greatcommissionbenchmark.ai/action/insights/{slug}.

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


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
