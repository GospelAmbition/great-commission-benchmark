from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.core.cache import SimpleCache, cache
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.action_log import ActionLog
from app.db.models.model import Model
from app.db.models.test_run import TestRun as RunRecord
from app.services.runner_models import get_runner_models


@pytest.mark.asyncio
async def test_simple_cache_deletes_only_matching_prefix():
    local_cache = SimpleCache()
    await local_cache.set("leaderboard:one", {"rank": 1})
    await local_cache.set("leaderboard:two", {"rank": 2})
    await local_cache.set("model_snapshot:abc", {"score": 90})

    deleted = await local_cache.delete_prefix("leaderboard")

    assert deleted == 2
    assert await local_cache.get("leaderboard:one") is None
    assert await local_cache.get("model_snapshot:abc") == {"score": 90}


@pytest.mark.asyncio
async def test_runner_models_query_count_is_constant_and_cached(
    db_session,
    test_user,
    test_model,
    test_question_set,
):
    methodology = MethodologyVersion(
        question_set_id=test_question_set.id,
        scoring_config={},
        active_from=datetime.now(timezone.utc),
    )
    second_model = Model(
        model_id="test-provider/another-model",
        name="Another Model",
        provider="test-provider",
        is_active=True,
    )
    db_session.add_all([second_model, methodology])
    db_session.flush()

    older = datetime.now(timezone.utc) - timedelta(days=1)
    newer = datetime.now(timezone.utc)
    db_session.add_all([
        RunRecord(
            user_id=test_user.id,
            model_id=test_model.id,
            question_set_id=test_question_set.id,
            methodology_version_id=methodology.id,
            status="completed",
            completed_at=older,
        ),
        RunRecord(
            user_id=test_user.id,
            model_id=test_model.id,
            question_set_id=test_question_set.id,
            methodology_version_id=methodology.id,
            status="completed",
            completed_at=newer,
        ),
        RunRecord(
            user_id=test_user.id,
            model_id=second_model.id,
            question_set_id=test_question_set.id,
            methodology_version_id=methodology.id,
            status="running",
        ),
    ])
    db_session.commit()
    await cache.delete_prefix("runner_models")

    statements = []

    def count_statement(*args):
        statements.append(args[2])

    event.listen(db_session.bind, "before_cursor_execute", count_statement)
    try:
        cold = await get_runner_models(db_session)
        cold_query_count = len(statements)
        statements.clear()
        warm = await get_runner_models(db_session)
        warm_query_count = len(statements)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", count_statement)
        await cache.delete_prefix("runner_models")

    assert cold_query_count == 2
    assert warm_query_count == 0
    assert warm == cold
    assert [item["name"] for item in cold["models"]] == ["Another Model", "Test Model"]
    test_entry = next(item for item in cold["models"] if item["model_id"] == test_model.model_id)
    assert datetime.fromisoformat(test_entry["last_tested_at"]).replace(tzinfo=timezone.utc) == newer
    untested_entry = next(item for item in cold["models"] if item["model_id"] == second_model.model_id)
    assert untested_entry["last_tested_version"] is None


@pytest.mark.asyncio
async def test_admin_leaderboard_rebuild_returns_diagnostics_and_logs_action(
    db_session,
    admin_user,
    monkeypatch,
):
    from app.api.v1.endpoints.admin import refresh_cache

    admin_user.can_admin = True
    db_session.commit()
    clear_mock = AsyncMock(return_value={"leaderboard": 3, "model_snapshot": 2})
    warm_mock = AsyncMock(return_value={
        "warmed": {"leaderboard": True, "runner_models": 2},
        "model_snapshots_built": 2,
        "warnings": [],
    })
    revalidate_mock = AsyncMock(return_value=True)
    monkeypatch.setattr("app.services.published_cache.clear_published_caches", clear_mock)
    monkeypatch.setattr("app.services.cache_warmer.warm_all_caches", warm_mock)
    monkeypatch.setattr(
        "app.services.leaderboard_refresh.trigger_frontend_revalidation",
        revalidate_mock,
    )

    result = await refresh_cache(admin_user, db_session)

    assert result["message"] == "Leaderboard rebuilt successfully"
    assert result["model_snapshots_built"] == 2
    assert result["frontend_revalidated"] is True
    clear_mock.assert_awaited_once_with()
    warm_mock.assert_awaited_once_with(include_published_models=True)
    log = db_session.query(ActionLog).filter(ActionLog.action == "cache.leaderboard_rebuild").one()
    assert log.actor_user_id == admin_user.id


@pytest.mark.asyncio
async def test_admin_leaderboard_rebuild_requires_admin(db_session, test_user):
    from app.api.v1.endpoints.admin import refresh_cache

    with pytest.raises(HTTPException) as exc:
        await refresh_cache(test_user, db_session)
    assert exc.value.status_code == 403
