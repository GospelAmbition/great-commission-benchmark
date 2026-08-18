"""Optimized and cached runner model catalog."""

from __future__ import annotations

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.cache import CACHE_TTL, cache, make_cache_key
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.test_run import TestRun


async def build_runner_models(db: Session) -> dict:
    active_qs = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    current_version = active_qs.semantic_version if active_qs else None

    if active_qs:
        ranked_runs = db.query(
            TestRun.id.label("test_run_id"),
            TestRun.model_id.label("model_id"),
            TestRun.completed_at.label("completed_at"),
            func.row_number().over(
                partition_by=TestRun.model_id,
                order_by=TestRun.completed_at.desc(),
            ).label("run_rank"),
        ).filter(
            TestRun.question_set_id == active_qs.id,
            TestRun.status == "completed",
        ).subquery()
        rows = db.query(Model, ranked_runs.c.test_run_id, ranked_runs.c.completed_at).outerjoin(
            ranked_runs,
            and_(ranked_runs.c.model_id == Model.id, ranked_runs.c.run_rank == 1),
        ).filter(Model.is_active == True).order_by(Model.name).all()
    else:
        rows = [
            (model, None, None)
            for model in db.query(Model)
            .filter(Model.is_active == True)
            .order_by(Model.name)
            .all()
        ]

    items = [
        {
            "id": str(model.id),
            "model_id": model.model_id,
            "name": model.name,
            "provider": model.provider,
            "last_tested_version": current_version if latest_run_id is not None else None,
            "last_tested_at": latest_completed_at.isoformat() if latest_completed_at else None,
        }
        for model, latest_run_id, latest_completed_at in rows
    ]
    return {"models": items, "total": len(items), "current_version": current_version}


async def get_runner_models(db: Session, *, force_rebuild: bool = False) -> dict:
    key = make_cache_key("runner_models")
    if not force_rebuild:
        cached = await cache.get(key)
        if cached is not None:
            return cached
    result = await build_runner_models(db)
    await cache.set(
        key,
        result,
        ttl_seconds=CACHE_TTL["runner_models"],
        stale_ttl_seconds=CACHE_TTL["runner_models"],
    )
    return result
