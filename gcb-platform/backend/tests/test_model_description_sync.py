"""Persist full model text without request-time scraping or destructive refreshes."""
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.db.models.model import Model
from app.services import model_description, model_sync


def page(description="Model intro and full continuation.", url="https://openrouter.ai/provider/model", kind="SoftwareApplication"):
    return '<script type="application/ld+json">' + json.dumps({"@type": kind, "url": url, "description": description}) + '</script>'


@pytest.mark.parametrize("html,expected", [
    (page(), "Model intro and full continuation."),
    (page(url="https://openrouter.ai/provider/other"), None),
    (page(url="https://evil.example/provider/model"), None),
    (page(kind="WebPage"), None),
    (page(description="Different introduction."), None),
    (page(description="Model intro..."), None),
    ('<script type="application/ld+json">broken</script>', None),
])
def test_verified_structured_description(html, expected):
    assert model_description.extract_full_description(html, "provider/model", "Model intro...") == expected


def test_unicode_ellipsis_and_graph():
    entity = {"@type": "SoftwareApplication", "url": "https://openrouter.ai/provider/model", "description": "Model intro & more."}
    html = '<script type="application/ld+json">' + json.dumps({"@graph": [entity]}) + '</script>'
    assert model_description.extract_full_description(html, "provider/model", "Model intro…") == "Model intro & more."


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["success", "error", "large", "timeout", "redirect"])
async def test_public_fetch_is_bounded_and_has_no_authorization(monkeypatch, mode):
    actual_client = httpx.AsyncClient
    async def respond(request):
        assert request.url == "https://openrouter.ai/provider/model"
        assert "authorization" not in request.headers
        if mode == "timeout":
            raise httpx.ReadTimeout("timeout")
        if mode == "error":
            return httpx.Response(500)
        if mode == "redirect":
            return httpx.Response(302, headers={"location": "https://other.example"})
        content = "x" * (model_description.MAX_PAGE_BYTES + 1) if mode == "large" else page()
        return httpx.Response(200, text=content)
    def client(**kwargs):
        assert kwargs["timeout"] == 5
        assert kwargs["follow_redirects"] is False
        return actual_client(transport=httpx.MockTransport(respond), **kwargs)
    monkeypatch.setattr(model_description.httpx, "AsyncClient", client)
    result = await model_description.fetch_full_description("provider/model", "Model intro...")
    assert result == ("Model intro and full continuation." if mode == "success" else None)


@pytest.fixture
def router():
    client = AsyncMock()
    with patch.object(model_sync, "OpenRouterClient", return_value=client):
        yield client


@pytest.mark.asyncio
async def test_single_sync_persists_full_text(db_session, test_model, router):
    router.get_model_info.return_value = {"description": "Model intro..."}
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value="Model intro and full text.")):
        assert await model_sync.sync_model_description(db_session, test_model)
    db_session.refresh(test_model)
    assert test_model.description == "Model intro and full text."
    router.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_full_api_description_does_not_fetch_html(db_session, test_model, router):
    router.get_model_info.return_value = {"description": "Complete API text."}
    with patch.object(model_sync, "fetch_full_description", AsyncMock()) as fetch:
        assert await model_sync.sync_model_description(db_session, test_model)
        fetch.assert_not_awaited()
    assert test_model.description == "Complete API text."


@pytest.mark.asyncio
async def test_abbreviated_refresh_preserves_full_continuation(db_session, test_model, router):
    test_model.description = "Model intro and full text."
    db_session.commit()
    router.get_model_info.return_value = {"description": "Model intro..."}
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value=None)) as fetch:
        assert not await model_sync.sync_model_description(db_session, test_model)
        fetch.assert_awaited_once()
    assert test_model.description == "Model intro and full text."


@pytest.mark.asyncio
async def test_failed_enrichment_preserves_full_text(db_session, test_model, router):
    test_model.description = "Previous complete description."
    db_session.commit()
    router.get_model_info.return_value = {"description": "New intro..."}
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value=None)):
        assert not await model_sync.sync_model_description(db_session, test_model)
    assert test_model.description == "Previous complete description."


@pytest.mark.asyncio
async def test_bulk_repairs_missing_and_abbreviated_and_retries(db_session, router):
    records = [Model(model_id=f"provider/{index}", provider="provider", name=f"Model {index}", description=description) for index, description in enumerate([None, "Model intro...", "Already complete."])]
    db_session.add_all(records)
    db_session.commit()
    router.list_models.return_value = [{"id": record.model_id, "description": "Model intro..."} for record in records]
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value=None)) as fetch:
        assert await model_sync.sync_all_model_descriptions(db_session) == 1
        assert fetch.await_count == 2
    router.list_models.assert_awaited_once()
    router.get_model_info.assert_not_awaited()
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value="Model intro full text.")) as fetch:
        assert await model_sync.sync_all_model_descriptions(db_session) == 2
        assert fetch.await_count == 2
    assert records[2].description == "Already complete."


@pytest.mark.asyncio
async def test_bulk_offsets_include_complete_rows(db_session, router):
    db_session.add_all([Model(model_id=f"provider/{index}", provider="provider", name=str(index), description="Complete." if index == 0 else None) for index in range(3)])
    db_session.commit()
    router.list_models.return_value = [{"id": f"provider/{index}", "description": "New full text."} for index in range(3)]
    assert await model_sync.sync_all_model_descriptions(db_session, offset=0, limit=1) == 0
    router.list_models.assert_not_awaited()
    assert await model_sync.sync_all_model_descriptions(db_session, offset=1, limit=1) == 1
    assert await model_sync.sync_all_model_descriptions(db_session, all_models=True, offset=0, limit=1) == 1
    assert db_session.query(Model).filter_by(model_id="provider/2").one().description is None


@pytest.mark.parametrize("url,kind,expected", [
    ("https://openrouter.ai/provider%2Fmodel/", ["Thing", "SoftwareApplication"], "Model intro and full continuation."),
    ("https://openrouter.ai@evil.example/provider/model", "SoftwareApplication", None),
    ("https://openrouter.ai/provider/model?other=1", "SoftwareApplication", None),
    ("http://openrouter.ai/provider/model", "SoftwareApplication", None),
])
def test_canonical_variants_and_origin(url, kind, expected):
    assert model_description.extract_full_description(page(url=url, kind=kind), "provider/model", "Model intro...") == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("model_id", ["../model", "provider/../model", "provider/", "/model", "provider/model?key=x", "https://evil.example"])
async def test_invalid_model_id_never_fetches(model_id):
    with patch.object(model_description.httpx, "AsyncClient") as client:
        assert await model_description.fetch_full_description(model_id, "Model intro...") is None
        client.assert_not_called()


def test_description_size_is_bounded():
    assert model_description.extract_full_description(page(description="Model intro" + "é" * 65536), "provider/model", "Model intro...") is None


@pytest.mark.asyncio
async def test_explicit_refresh_updates_full_continuation(db_session, test_model, router):
    test_model.description = "Model intro old full text."
    db_session.commit()
    router.list_models.return_value = [{"id": test_model.model_id, "description": "Model intro..."}]
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value="Model intro new full text.")) as fetch:
        assert await model_sync.sync_all_model_descriptions(db_session, all_models=True) == 1
        fetch.assert_awaited_once()
    assert test_model.description == "Model intro new full text."


@pytest.mark.asyncio
async def test_page_above_old_two_megabyte_limit_is_supported(monkeypatch):
    actual_client = httpx.AsyncClient
    content = '<!--' + 'x' * 2_100_000 + '-->' + page()
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=content))
    monkeypatch.setattr(model_description.httpx, "AsyncClient", lambda **kwargs: actual_client(transport=transport, **kwargs))
    assert await model_description.fetch_full_description("provider/model", "Model intro...") == "Model intro and full continuation."


@pytest.mark.asyncio
async def test_archived_model_uses_existing_abbreviation_when_absent_from_catalog(db_session, test_model, router):
    test_model.description = "Model intro..."
    db_session.commit()
    router.list_models.return_value = []
    with patch.object(model_sync, "fetch_full_description", AsyncMock(return_value="Model intro archived full text.")):
        assert await model_sync.sync_all_model_descriptions(db_session) == 1
    assert test_model.description == "Model intro archived full text."
