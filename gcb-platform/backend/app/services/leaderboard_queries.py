"""Shared leaderboard query helpers."""
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.db.models.model import Model
from app.db.models.test_run import TestRun


def _base_completed_test_runs_query(
    db: Session,
    *,
    question_set_id: UUID,
    provider: Optional[str] = None,
    trust_tier: Optional[str] = None,
):
    query = (
        db.query(TestRun)
        .options(
            joinedload(TestRun.model),
            joinedload(TestRun.question_set),
        )
        .join(Model, TestRun.model_id == Model.id)
        .filter(
            TestRun.status == "completed",
            TestRun.question_set_id == question_set_id,
            TestRun.overall_score.isnot(None),
            or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
            Model.is_active == True,
        )
    )

    if provider:
        query = query.filter(Model.provider == provider)
    if trust_tier:
        query = query.filter(TestRun.trust_tier == trust_tier)

    return query


def _dedupe_latest_per_model_python(test_runs: list[TestRun]) -> list[TestRun]:
    seen_models = set()
    unique_test_runs = []
    for test_run in test_runs:
        if test_run.model_id not in seen_models:
            seen_models.add(test_run.model_id)
            unique_test_runs.append(test_run)
    return unique_test_runs


def get_latest_completed_test_runs(
    db: Session,
    *,
    question_set_id: UUID,
    provider: Optional[str] = None,
    trust_tier: Optional[str] = None,
) -> list[TestRun]:
    """Return the most recent completed test run per active model."""
    query = _base_completed_test_runs_query(
        db,
        question_set_id=question_set_id,
        provider=provider,
        trust_tier=trust_tier,
    )

    if db.bind.dialect.name == "postgresql":
        return (
            query.order_by(TestRun.model_id, TestRun.completed_at.desc().nullslast())
            .distinct(TestRun.model_id)
            .all()
        )

    # SQLite and other dialects: fetch ordered runs and dedupe in Python (tests).
    test_runs = query.order_by(TestRun.completed_at.desc()).all()
    return _dedupe_latest_per_model_python(test_runs)
