"""Archived model URLs remain public without republishing disabled scores."""
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from app.api.v1.endpoints.public import get_model_by_model_id, get_model_detail, list_model_pages
from app.db.models.model import Model
from app.db.models.methodology_version import MethodologyVersion


@pytest.fixture
def test_methodology_version(db_session, test_question_set):
    methodology = MethodologyVersion(
        question_set_id=test_question_set.id, active_from=datetime.now(timezone.utc),
    )
    db_session.add(methodology)
    db_session.commit()
    return methodology


@pytest.mark.asyncio
async def test_archived_model_without_valid_results(db_session, test_model):
    test_model.is_active = False
    db_session.commit()
    data = await get_model_by_model_id(test_model.model_id, db_session)
    assert data["is_active"] is False
    assert data["model_id"] == test_model.model_id
    assert "score" not in data
    assert data["related_models"] == []
    uuid_data = await get_model_detail(test_model.id, db_session)
    assert uuid_data["best_result"] is None


@pytest.mark.asyncio
async def test_unknown_and_active_untested_models_still_404(db_session, test_model):
    for model_id in ["unknown/missing", test_model.model_id]:
        with pytest.raises(HTTPException) as exc:
            await get_model_by_model_id(model_id, db_session)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_alternatives_require_active_valid_results(db_session, test_model, completed_test_run):
    completed_test_run.overall_score = 85
    archived = Model(model_id="test-provider/test-old", name="Old Model", provider="test-provider", is_active=False)
    untested = Model(model_id="test-provider/test-new", name="Untested", provider="test-provider", is_active=True)
    db_session.add_all([archived, untested])
    db_session.commit()
    data = await get_model_by_model_id(archived.model_id, db_session)
    assert [m["model_id"] for m in data["related_models"]] == [test_model.model_id]
    assert data["related_models"][0]["relationship"] == "family"
    test_model.is_active = False
    db_session.commit()
    data = await get_model_by_model_id(archived.model_id, db_session)
    assert data["related_models"] == []


@pytest.mark.asyncio
async def test_sitemap_includes_archived_excludes_untested(db_session, test_model):
    archived = Model(model_id="old/model", name="Archived", provider="old", is_active=False)
    db_session.add(archived)
    db_session.commit()
    data = await list_model_pages(limit=1, offset=0, db=db_session)
    assert data == {"items": [{"model_id": "old/model"}], "has_more": False}
