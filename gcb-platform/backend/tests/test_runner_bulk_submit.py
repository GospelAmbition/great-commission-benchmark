from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.db.models.model import Model


def _valid_export(model_id: str, version: str, questions: list) -> dict:
    responses = [
        {
            "question_id": str(question.id),
            "tier": question.tier,
            "category": question.category,
            "response": "Test response",
            "verdict": "ACCEPTED",
            "judge_reasoning": "Accepted for test purposes.",
        }
        for question in questions
    ]

    return {
        "format_version": "1.0",
        "test_run": {
            "id": "test-run-1",
            "model": model_id,
            "backend": "openrouter",
            "benchmark_version": version,
            "judge_model": "openai/gpt-oss-20b",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        },
        "summary": {
            "total_questions": len(responses),
            "score": 100,
            "scoring_weights": {"tier1": 0.7, "tier2": 0.2, "tier3": 0.1},
            "tier_scores": {
                "tier1": {"raw": 100, "questions": 7},
                "tier2": {"raw": 100, "questions": 2},
                "tier3": {"raw": 100, "questions": 1},
            },
            "verdict_counts": {"ACCEPTED": len(responses), "COMPROMISED": 0, "REFUSED": 0},
        },
        "responses": responses,
        "metadata": {
            "benchmark_version": version,
            "cli_version": "test",
        },
    }


def _authorize_runner(app, runner, admin_user, db_session):
    admin_user.can_admin = True
    db_session.commit()

    async def override_api_key():
        return None, admin_user

    app.dependency_overrides[runner.require_api_key] = override_api_key


def _bulk_submit(client, model_id: str, question_set, questions):
    return client.post(
        "/api/runner/bulk-submit",
        json={"export_data": _valid_export(model_id, question_set.semantic_version, questions)},
    )


def test_bulk_submit_syncs_description_for_new_model(
    client,
    db_session,
    admin_user,
    test_question_set,
    test_questions,
    monkeypatch,
):
    from main import app
    from app.api.v1.endpoints import runner

    _authorize_runner(app, runner, admin_user, db_session)

    async def fake_sync(db, model, commit=True):
        model.description = "OpenRouter description"
        return True

    sync_mock = AsyncMock(side_effect=fake_sync)
    monkeypatch.setattr("app.services.model_sync.sync_model_description", sync_mock)

    response = _bulk_submit(client, "test-provider/new-model", test_question_set, test_questions)

    assert response.status_code == 200
    assert response.json()["status"] == "published"

    model = db_session.query(Model).filter(Model.model_id == "test-provider/new-model").one()
    assert model.description == "OpenRouter description"
    sync_mock.assert_awaited_once()
    assert sync_mock.await_args.kwargs["commit"] is False


def test_bulk_submit_syncs_description_for_existing_model_without_description(
    client,
    db_session,
    admin_user,
    test_question_set,
    test_questions,
    monkeypatch,
):
    from main import app
    from app.api.v1.endpoints import runner

    model = Model(
        model_id="test-provider/existing-model",
        name="Existing Model",
        provider="test-provider",
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()

    _authorize_runner(app, runner, admin_user, db_session)

    async def fake_sync(db, model, commit=True):
        model.description = "Backfilled OpenRouter description"
        return True

    monkeypatch.setattr(
        "app.services.model_sync.sync_model_description",
        AsyncMock(side_effect=fake_sync),
    )

    response = _bulk_submit(client, "test-provider/existing-model", test_question_set, test_questions)

    assert response.status_code == 200
    assert response.json()["status"] == "published"

    db_session.refresh(model)
    assert model.description == "Backfilled OpenRouter description"


def test_bulk_submit_preserves_existing_description(
    client,
    db_session,
    admin_user,
    test_question_set,
    test_questions,
    monkeypatch,
):
    from main import app
    from app.api.v1.endpoints import runner

    model = Model(
        model_id="test-provider/curated-model",
        name="Curated Model",
        provider="test-provider",
        description="Curated description",
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()

    _authorize_runner(app, runner, admin_user, db_session)
    sync_mock = AsyncMock()
    monkeypatch.setattr("app.services.model_sync.sync_model_description", sync_mock)

    response = _bulk_submit(client, "test-provider/curated-model", test_question_set, test_questions)

    assert response.status_code == 200
    assert response.json()["status"] == "published"

    db_session.refresh(model)
    assert model.description == "Curated description"
    sync_mock.assert_not_awaited()


def test_bulk_submit_refreshes_leaderboard_cache(
    client,
    db_session,
    admin_user,
    test_question_set,
    test_questions,
    monkeypatch,
):
    from main import app
    from app.api.v1.endpoints import runner

    _authorize_runner(app, runner, admin_user, db_session)

    refresh_mock = AsyncMock()
    monkeypatch.setattr(
        "app.services.leaderboard_refresh.refresh_leaderboard_after_test_publish",
        refresh_mock,
    )

    response = _bulk_submit(client, "test-provider/cache-refresh", test_question_set, test_questions)

    assert response.status_code == 200
    assert response.json()["status"] == "published"
    refresh_mock.assert_awaited_once()


def test_bulk_submit_continues_when_description_sync_fails(
    client,
    db_session,
    admin_user,
    test_question_set,
    test_questions,
    monkeypatch,
):
    from main import app
    from app.api.v1.endpoints import runner

    _authorize_runner(app, runner, admin_user, db_session)
    monkeypatch.setattr(
        "app.services.model_sync.sync_model_description",
        AsyncMock(return_value=False),
    )

    response = _bulk_submit(client, "test-provider/no-description", test_question_set, test_questions)

    assert response.status_code == 200
    assert response.json()["status"] == "published"

    model = db_session.query(Model).filter(Model.model_id == "test-provider/no-description").one()
    assert model.description is None
