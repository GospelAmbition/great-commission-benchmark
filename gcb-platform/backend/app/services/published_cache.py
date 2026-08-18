"""Cache namespaces and invalidation for published benchmark data."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from app.core.cache import cache


DERIVED_NAMESPACES = (
    "runner_models",
    "leaderboard",
    "category_rankings",
    "filter_options",
    "public_stats",
    "models_list",
    "model_comparison",
)

ALL_PUBLISHED_NAMESPACES = ("model_snapshot", *DERIVED_NAMESPACES, "versions")


def model_snapshot_key(model_id: UUID | str) -> str:
    return f"model_snapshot:{model_id}"


async def invalidate_namespaces(*prefixes: str) -> dict[str, int]:
    """Delete cache namespaces and return per-prefix deletion counts."""
    counts = await asyncio.gather(*(cache.delete_prefix(prefix) for prefix in prefixes))
    return dict(zip(prefixes, counts))


async def invalidate_published_data(
    model_id: UUID | str | None = None,
    *,
    include_versions: bool = False,
) -> dict[str, int]:
    """Invalidate one model snapshot and all collections derived from it."""
    prefixes: list[str] = []
    if model_id is not None:
        prefixes.append(model_snapshot_key(model_id))
    prefixes.extend(DERIVED_NAMESPACES)
    if include_versions:
        prefixes.append("versions")
    return await invalidate_namespaces(*prefixes)


async def clear_published_caches() -> dict[str, int]:
    """Clear every published-data namespace used by the admin rebuild."""
    return await invalidate_namespaces(*ALL_PUBLISHED_NAMESPACES)
