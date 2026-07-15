"""Tests for leaderboard DB connection fixes."""
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.test_run import TestRun as TestRunModel
from app.db.models.user import User
from main import app
from app.services.leaderboard_queries import get_latest_completed_test_runs


@pytest.fixture
def api_client(db_session):
    """Test client with injected database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def leaderboard_test_data(db_session: Session):
    """Question set, model, user, and methodology for leaderboard tests."""
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active",
    )
    db_session.add(question_set)
    db_session.commit()
    db_session.refresh(question_set)

    methodology_version = MethodologyVersion(
        question_set_id=question_set.id,
        scoring_config={"tier1_weight": 0.70, "tier2_weight": 0.20, "tier3_weight": 0.10},
        active_from=question_set.created_at,
    )
    db_session.add(methodology_version)

    user = User(
        auth0_id="test|leaderboard",
        email="leaderboard@example.com",
        name="Leaderboard User",
    )
    db_session.add(user)

    model = Model(
        model_id="test/leaderboard-model",
        name="Leaderboard Model",
        provider="Test Provider",
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    db_session.refresh(user)
    db_session.refresh(methodology_version)

    return {
        "question_set": question_set,
        "model": model,
        "user": user,
        "methodology_version": methodology_version,
    }


def _make_completed_run(
    db_session: Session,
    *,
    data: dict,
    completed_at: datetime,
    overall_score: float,
) -> TestRunModel:
    test_run = TestRunModel(
        user_id=data["user"].id,
        model_id=data["model"].id,
        question_set_id=data["question_set"].id,
        methodology_version_id=data["methodology_version"].id,
        status="completed",
        trust_tier="automated",
        overall_score=overall_score,
        tier1_score=overall_score,
        tier2_score=overall_score,
        tier3_score=overall_score,
        category_scores={"1.1": overall_score},
        total_questions=10,
        completed_at=completed_at,
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


def test_get_latest_completed_test_runs_returns_newest_per_model(
    db_session: Session, leaderboard_test_data
):
    """Only the most recent completed run per model should be returned."""
    older = _make_completed_run(
        db_session,
        data=leaderboard_test_data,
        completed_at=datetime.now(timezone.utc) - timedelta(days=2),
        overall_score=40.0,
    )
    newer = _make_completed_run(
        db_session,
        data=leaderboard_test_data,
        completed_at=datetime.now(timezone.utc) - timedelta(days=1),
        overall_score=80.0,
    )

    results = get_latest_completed_test_runs(
        db_session,
        question_set_id=leaderboard_test_data["question_set"].id,
    )

    assert len(results) == 1
    assert results[0].id == newer.id
    assert results[0].id != older.id
    assert float(results[0].overall_score) == 80.0


@pytest.mark.asyncio
async def test_refresh_leaderboard_cache_owns_db_session():
    """Background refresh must open and close its own DB session."""
    from app.api.v1.endpoints.public import _refresh_leaderboard_cache

    mock_db = MagicMock()
    mock_db.close = MagicMock()

    with patch("app.api.v1.endpoints.public.get_db_sync", return_value=mock_db) as mock_get_db, \
         patch("app.api.v1.endpoints.public.cache.mark_refreshing", new_callable=AsyncMock), \
         patch("app.api.v1.endpoints.public.cache.unmark_refreshing", new_callable=AsyncMock), \
         patch("app.api.v1.endpoints.public.cache.set", new_callable=AsyncMock), \
         patch(
             "app.services.cache_warmer._generate_leaderboard_data",
             new_callable=AsyncMock,
             return_value=MagicMock(),
         ):
        await _refresh_leaderboard_cache("leaderboard:test", {"version": "current"})

    mock_get_db.assert_called_once()
    mock_db.close.assert_called_once()


def test_get_leaderboard_returns_503_on_db_outage(api_client, leaderboard_test_data):
    """Leaderboard cache-miss path should return 503 when the database is unavailable."""
    with patch.object(
        Session,
        "query",
        side_effect=OperationalError("SELECT 1", {}, Exception("connection failed")),
    ):
        response = api_client.get("/api/public/leaderboard")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database service temporarily unavailable"
