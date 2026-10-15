"""Official per-model metadata lookup for aliases missing from the active catalog."""
import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from app.services import openrouter


@pytest.fixture
def model_client():
    # Supply a mocked transport directly so no credentials or network are needed.
    client = openrouter.OpenRouterClient.__new__(openrouter.OpenRouterClient)
    return client


@pytest.mark.asyncio
async def test_get_model_info_uses_official_details_for_missing_alias(model_client):
    paths = []
    def respond(request):
        paths.append(request.url.path)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": []})
        return httpx.Response(200, json={"data": {"id": "provider/canonical", "description": "Full description."}})
    model_client.client = httpx.AsyncClient(base_url=openrouter.OpenRouterClient.BASE_URL, transport=httpx.MockTransport(respond))
    try:
        info = await model_client.get_model_info("provider/alias:free")
        assert info == {"id": "provider/canonical", "description": "Full description."}
        assert paths == ["/api/v1/models", "/api/v1/model/provider/alias:free"]
    finally:
        await model_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("status,payload", [(404, {}), (500, {}), (200, {"data": {"id": "../other"}}), (200, {"data": {"id": None}}), (200, []), (200, {"data": None})])
async def test_invalid_or_missing_details_return_none(model_client, status, payload):
    model_client.client = httpx.AsyncClient(base_url=openrouter.OpenRouterClient.BASE_URL, transport=httpx.MockTransport(lambda request: httpx.Response(status, json=payload)))
    try:
        assert await model_client.get_model_details("provider/model") is None
    finally:
        await model_client.close()


@pytest.mark.asyncio
async def test_detail_lookup_has_total_deadline(model_client, monkeypatch):
    monkeypatch.setattr(openrouter, "MODEL_DETAILS_TIMEOUT_SECONDS", 0.01)
    cancelled = asyncio.Event()
    async def stalled(request):
        assert request.extensions["timeout"]["read"] == 0.01
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
    model_client.client = httpx.AsyncClient(base_url=openrouter.OpenRouterClient.BASE_URL, transport=httpx.MockTransport(stalled))
    try:
        assert await model_client.get_model_details("provider/model") is None
        assert cancelled.is_set()
    finally:
        await model_client.close()


@pytest.mark.asyncio
async def test_invalid_model_id_is_not_requested(model_client):
    model_client.client = AsyncMock()
    assert await model_client.get_model_details("provider/model?redirect=evil") is None
    model_client.client.get.assert_not_awaited()
