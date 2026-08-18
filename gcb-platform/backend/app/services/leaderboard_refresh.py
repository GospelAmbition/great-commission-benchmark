"""Refresh leaderboard caches after a test run is published."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.db.models.test_run import TestRun

logger = logging.getLogger(__name__)

DEFAULT_REVALIDATE_PATHS = ["/", "/leaderboard", "/categories"]


async def refresh_leaderboard_after_test_publish(
    db: Session,
    test_run: TestRun,
    *,
    revalidate_frontend: bool = True,
) -> None:
    """Rebuild leaderboard caches after a newly published test run.

    Clears stale API cache entries, recalculates model-version stats, warms
    the default leaderboard payload, and optionally triggers Next.js ISR
    revalidation for public pages that embed leaderboard data.
    """
    from app.services.aggregation import AggregationService
    from app.services.published_cache import invalidate_published_data
    from app.services.cache_warmer import (
        warm_category_rankings_cache,
        warm_filter_options_cache,
        warm_leaderboard_cache,
    )

    try:
        AggregationService.recalculate_model_stats(
            db,
            test_run.model_id,
            test_run.question_set_id,
        )
    except Exception as exc:
        logger.warning(
            "Model stats recalculation after publish failed for test_run=%s: %s",
            test_run.id,
            exc,
        )

    try:
        await invalidate_published_data(test_run.model_id)
        await warm_filter_options_cache(db)
        await warm_leaderboard_cache(db)
        await warm_category_rankings_cache(db)
    except Exception as exc:
        logger.warning(
            "Leaderboard cache refresh after publish failed for test_run=%s: %s",
            test_run.id,
            exc,
        )

    if revalidate_frontend:
        await trigger_frontend_revalidation()


async def trigger_frontend_revalidation(
    paths: Optional[list[str]] = None,
) -> bool:
    """Ask the Next.js frontend to revalidate ISR pages that show leaderboard data."""
    frontend_url = os.getenv("FRONTEND_URL", "https://greatcommissionbenchmark.ai").rstrip("/")
    secret = os.getenv("WARM_SECRET") or os.getenv("REVALIDATE_SECRET")
    if not secret:
        logger.debug("Skipping frontend revalidation: WARM_SECRET/REVALIDATE_SECRET not set")
        return False

    payload = {"paths": paths or DEFAULT_REVALIDATE_PATHS}
    url = f"{frontend_url}/api/revalidate?secret={secret}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code >= 400:
                logger.warning(
                    "Frontend revalidation failed: status=%s body=%s",
                    response.status_code,
                    response.text[:200],
                )
                return False
        logger.info("Frontend revalidation triggered for paths=%s", payload["paths"])
        return True
    except Exception as exc:
        logger.warning("Frontend revalidation request failed: %s", exc)
        return False


def schedule_leaderboard_refresh_after_test_publish(
    db: Session,
    test_run: TestRun,
    *,
    revalidate_frontend: bool = True,
) -> None:
    """Fire-and-forget wrapper for sync endpoints that cannot await."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning(
            "No running event loop; skipping leaderboard refresh for test_run=%s",
            test_run.id,
        )
        return

    loop.create_task(
        refresh_leaderboard_after_test_publish(
            db,
            test_run,
            revalidate_frontend=revalidate_frontend,
        )
    )
