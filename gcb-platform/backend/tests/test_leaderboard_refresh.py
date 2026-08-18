import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.db.models.test_run import TestRun
from app.services.leaderboard_refresh import (
    DEFAULT_REVALIDATE_PATHS,
    refresh_leaderboard_after_test_publish,
    trigger_frontend_revalidation,
)


@pytest.mark.asyncio
async def test_refresh_leaderboard_after_test_publish_clears_and_warms(db_session, test_question_set):
    model_id = uuid4()
    test_run = TestRun(
        id=uuid4(),
        user_id=uuid4(),
        model_id=model_id,
        question_set_id=test_question_set.id,
        status="completed",
    )

    with patch(
        "app.services.aggregation.AggregationService.recalculate_model_stats",
        return_value=None,
    ) as recalc_mock, patch(
        "app.services.published_cache.invalidate_published_data",
        new_callable=AsyncMock,
    ) as invalidate_mock, patch(
        "app.services.cache_warmer.warm_filter_options_cache",
        new_callable=AsyncMock,
    ) as warm_filters_mock, patch(
        "app.services.cache_warmer.warm_leaderboard_cache",
        new_callable=AsyncMock,
    ) as warm_leaderboard_mock, patch(
        "app.services.cache_warmer.warm_category_rankings_cache",
        new_callable=AsyncMock,
    ) as warm_categories_mock, patch(
        "app.services.leaderboard_refresh.trigger_frontend_revalidation",
        new_callable=AsyncMock,
        return_value=True,
    ) as revalidate_mock:
        await refresh_leaderboard_after_test_publish(db_session, test_run)

    recalc_mock.assert_called_once_with(db_session, model_id, test_question_set.id)
    invalidate_mock.assert_awaited_once_with(model_id)
    warm_filters_mock.assert_awaited_once_with(db_session)
    warm_leaderboard_mock.assert_awaited_once_with(db_session)
    warm_categories_mock.assert_awaited_once_with(db_session)
    revalidate_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_trigger_frontend_revalidation_skips_without_secret(monkeypatch):
    monkeypatch.delenv("WARM_SECRET", raising=False)
    monkeypatch.delenv("REVALIDATE_SECRET", raising=False)

    assert await trigger_frontend_revalidation() is False


@pytest.mark.asyncio
async def test_trigger_frontend_revalidation_posts_to_frontend(monkeypatch):
    monkeypatch.setenv("WARM_SECRET", "test-secret")
    monkeypatch.setenv("FRONTEND_URL", "https://example.test")

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "ok"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        ok = await trigger_frontend_revalidation()

    assert ok is True
    mock_client.post.assert_awaited_once()
    args, kwargs = mock_client.post.await_args
    assert args[0] == "https://example.test/api/revalidate?secret=test-secret"
    assert kwargs["json"]["paths"] == DEFAULT_REVALIDATE_PATHS
