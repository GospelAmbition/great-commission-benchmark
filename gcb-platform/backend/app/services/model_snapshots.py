"""Stable cached snapshots of published model scores and test history."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.cache import CACHE_TTL, cache
from app.db.models.model import Model
from app.db.models.test_run import TestRun
from app.services.published_cache import model_snapshot_key


def _snapshot_from_runs(runs: Iterable[TestRun]) -> dict:
    tests = list(runs)[:10]
    best_test = tests[0] if tests else None
    best_result = None
    if best_test:
        best_result = {
            "test_run_id": str(best_test.id),
            "scores": {
                "overall": float(best_test.overall_score),
                "tier1": float(best_test.tier1_score or 0),
                "tier2": float(best_test.tier2_score or 0),
                "tier3": float(best_test.tier3_score or 0),
                "category_scores": best_test.category_scores or {},
                "verdict_distribution": best_test.verdict_distribution or {
                    "ACCEPTED": 0,
                    "COMPROMISED": 0,
                    "REFUSED": 0,
                    "ERROR": 0,
                },
                "total_questions": best_test.total_questions or 0,
            },
            "trust_tier": best_test.trust_tier,
            "completed_at": best_test.completed_at.isoformat() if best_test.completed_at else None,
            "benchmark_version": best_test.question_set.semantic_version,
        }

    history = [
        {
            "test_run_id": str(test.id),
            "overall_score": float(test.overall_score),
            "tier1_score": float(test.tier1_score or 0),
            "tier2_score": float(test.tier2_score or 0),
            "tier3_score": float(test.tier3_score or 0),
            "benchmark_version": test.question_set.semantic_version,
            "completed_at": test.completed_at.isoformat() if test.completed_at else None,
            "trust_tier": test.trust_tier,
        }
        for test in tests
    ]

    category_scores = best_test.category_scores or {} if best_test else {}
    category_breakdown = {
        category: {
            "total": 100,
            "passed": int(round(score)) if score is not None else 0,
            "score": float(score) if score is not None else 0.0,
        }
        for category, score in category_scores.items()
    }
    return {
        "best_result": best_result,
        "test_history": history,
        "category_breakdown": category_breakdown,
        "category_scores": category_scores,
        "test_count": len(history),
    }


def build_model_snapshot(db: Session, model: Model) -> dict:
    runs = (
        db.query(TestRun)
        .options(joinedload(TestRun.question_set))
        .filter(
            TestRun.model_id == model.id,
            TestRun.status == "completed",
            TestRun.overall_score.isnot(None),
            or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        )
        .order_by(TestRun.completed_at.desc())
        .limit(10)
        .all()
    )
    return _snapshot_from_runs(runs)


async def get_model_snapshot(db: Session, model: Model) -> dict:
    key = model_snapshot_key(model.id)
    cached = await cache.get(key)
    if cached is not None:
        return cached
    snapshot = build_model_snapshot(db, model)
    if snapshot["best_result"] is not None:
        await cache.set(
            key,
            snapshot,
            ttl_seconds=CACHE_TTL["model_snapshot"],
            stale_ttl_seconds=CACHE_TTL["model_snapshot"],
        )
    return snapshot


async def warm_model_snapshots(db: Session) -> tuple[int, list[str]]:
    """Batch-build every published model snapshot using two database queries."""
    models = db.query(Model).order_by(Model.name).all()
    runs = (
        db.query(TestRun)
        .options(joinedload(TestRun.question_set))
        .filter(
            TestRun.status == "completed",
            TestRun.overall_score.isnot(None),
            or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        )
        .order_by(TestRun.model_id, TestRun.completed_at.desc())
        .all()
    )
    grouped: dict[object, list[TestRun]] = defaultdict(list)
    for run in runs:
        if len(grouped[run.model_id]) < 10:
            grouped[run.model_id].append(run)

    built = 0
    warnings: list[str] = []
    for model in models:
        snapshot = _snapshot_from_runs(grouped.get(model.id, []))
        if snapshot["best_result"] is None:
            continue
        try:
            await cache.set(
                model_snapshot_key(model.id),
                snapshot,
                ttl_seconds=CACHE_TTL["model_snapshot"],
                stale_ttl_seconds=CACHE_TTL["model_snapshot"],
            )
            built += 1
        except Exception as exc:  # pragma: no cover - cache backends fail open
            warnings.append(f"{model.model_id}: {exc}")
    return built, warnings
