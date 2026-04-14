"""GCB public API helpers for fetching published model test results."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Public API base — no authentication required
_PUBLIC_BASE = "https://api.greatcommissionbenchmark.ai/api/public"


def _public_base() -> str:
    """Return the base URL for GCB public API endpoints.
    
    Supports three forms of GCB_API_BASE_URL:
      - https://api.greatcommissionbenchmark.ai/api  → .../public
      - https://api.greatcommissionbenchmark.ai      → .../api/public
      - https://greatcommissionbenchmark.ai          → rewrites to api subdomain
    Default: https://api.greatcommissionbenchmark.ai/api/public
    """
    env = os.environ.get("GCB_API_BASE_URL", "").strip().rstrip("/")
    if not env:
        return "https://api.greatcommissionbenchmark.ai/api/public"
    # If the env var points at the non-api domain, redirect to the API subdomain
    if "api." not in env:
        env = env.replace("greatcommissionbenchmark.ai", "api.greatcommissionbenchmark.ai")
    if env.endswith("/api"):
        return f"{env}/public"
    return f"{env}/api/public"


async def list_published_models(limit: int = 50) -> dict[str, Any]:
    """
    Fetch the GCB leaderboard ordered by most recently completed test.

    Returns a list of entries each containing:
        model_id, name, provider, overall_score, tier1/2/3_score,
        completed_at, test_run_id, trust_tier, benchmark_version
    """
    base = _public_base()
    url = f"{base}/leaderboard"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params={"limit": min(limit, 200)})
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc), "url": url}

    if not resp.is_success:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        return {
            "error": "api_error",
            "status_code": resp.status_code,
            "url": url,
            "detail": detail,
        }

    payload = resp.json()
    # Actual shape: {entries: [...], total_models, pagination, ...}
    raw_entries = payload.get("entries", payload.get("leaderboard", []))

    entries = []
    for e in raw_entries:
        scores = e.get("scores", {})
        test_run = e.get("test_run", {})
        model = e.get("model", {})
        entries.append(
            {
                "rank": e.get("rank"),
                "model_id": model.get("model_id") or e.get("model_id"),
                "name": model.get("name") or e.get("name"),
                "provider": model.get("provider") or e.get("provider"),
                "overall_score": scores.get("overall"),
                "tier1_score": scores.get("tier1"),
                "tier2_score": scores.get("tier2"),
                "tier3_score": scores.get("tier3"),
                "completed_at": test_run.get("completed_at"),
                "test_run_id": test_run.get("id"),
                "trust_tier": test_run.get("trust_tier"),
                "benchmark_version": test_run.get("question_set_version"),
                "verdict_distribution": e.get("verdict_distribution", {}),
                "total_questions": e.get("total_questions"),
            }
        )

    # Sort by completed_at descending (most recently published first)
    entries.sort(
        key=lambda x: x.get("completed_at") or "",
        reverse=True,
    )

    total = payload.get("total_models") or payload.get("pagination", {}).get("total") or len(entries)
    return {
        "models": entries,
        "total": total,
        "returned": len(entries),
    }


async def get_model_test_result(model_id: str) -> dict[str, Any]:
    """
    Fetch full test result data for a model by its OpenRouter model_id string.

    Returns structured data ready for article writing:
        model_id, name, provider, overall_score, tier1/2/3_score,
        verdict_distribution, category_scores, test_history,
        benchmark_version, trust_tier, total_questions
    """
    base = _public_base()
    url = f"{base}/models/by-id"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params={"model_id": model_id})
    except httpx.RequestError as exc:
        return {"error": "request_failed", "message": str(exc), "model_id": model_id}

    if resp.status_code == 404:
        return {
            "error": "not_found",
            "message": (
                f"Model '{model_id}' not found or has no completed test on the GCB platform. "
                "Use list_published_models() to see available models."
            ),
            "model_id": model_id,
        }

    if not resp.is_success:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        return {
            "error": "api_error",
            "status_code": resp.status_code,
            "url": url,
            "detail": detail,
        }

    data = resp.json()

    # Shape (after backend fix):
    # {id, model_id, model_name, name, provider, description,
    #  overall_score, score, tier1_score, tier2_score, tier3_score,
    #  verdict_distribution, total_questions,
    #  trust_tier, test_count, category_scores, version_history, test_history}

    test_history = data.get("test_history", [])

    # verdict_distribution is now a top-level field; fall back to test_history for
    # deployments that haven't picked up the backend fix yet
    verdict_dist: dict = data.get("verdict_distribution") or {}
    if not verdict_dist and test_history:
        verdict_dist = test_history[0].get("verdict_distribution", {})

    return {
        "model_id": data.get("model_id") or model_id,
        "name": data.get("name") or data.get("model_name"),
        "provider": data.get("provider"),
        "overall_score": data.get("overall_score") or data.get("score"),
        "tier1_score": data.get("tier1_score"),
        "tier2_score": data.get("tier2_score"),
        "tier3_score": data.get("tier3_score"),
        "verdict_distribution": verdict_dist,
        "category_scores": data.get("category_scores", {}),
        "total_questions": data.get("total_questions") or (
            test_history[0].get("total_questions") if test_history else None
        ),
        "benchmark_version": (
            data.get("version_history", [{}])[0].get("question_set_version")
            if data.get("version_history")
            else None
        ),
        "trust_tier": data.get("trust_tier"),
        "completed_at": (
            test_history[0].get("completed_at") if test_history else None
        ),
        "test_run_id": (
            test_history[0].get("id") if test_history else None
        ),
        "test_history": test_history,
        "test_count": data.get("test_count"),
        # Pass through the full raw payload so the agent can dig deeper if needed
        "_raw": data,
    }
