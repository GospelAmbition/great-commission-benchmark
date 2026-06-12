"""Tests for model Highlight drafting and SVG helpers."""

from __future__ import annotations

import asyncio

import gcb_mcp.blog as blog
import gcb_mcp.header_svg as header_svg
import gcb_mcp.server as server
from gcb_mcp.highlight import build_highlight_markdown


def _model_result() -> dict:
    return {
        "model_id": "openai/gpt-highlight-1",
        "name": "GPT Highlight 1",
        "provider": "openai",
        "overall_score": 82.4,
        "tier1_score": 88.0,
        "tier2_score": 76.5,
        "tier3_score": 70.0,
        "total_questions": 150,
        "completed_at": "2026-06-10T12:00:00Z",
        "benchmark_version": "1.0.0",
        "description": "A useful model for testing highlight copy.",
        "category_scores": {"1.2": 95.0, "3.1": 42.0},
    }


def _review_post() -> dict:
    return {
        "id": "review-post-1",
        "title": "anthropic/claude-opus-4.8-fast: Capability With a Refusal Burden",
        "slug": "anthropicclaude-opus-48-fast-capability-with-a-refusal-burden",
        "status": "published",
        "excerpt": "Claude Opus 4.8 Fast shows capability with a refusal burden.",
        "categories": [{"name": "Model Reviews", "slug": "model-reviews"}],
        "related_models": [
            {
                "id": "model-1",
                "model_id": "anthropic/claude-opus-4.8-fast",
                "name": "Claude Opus 4.8 Fast",
                "provider": "anthropic",
            }
        ],
        "published_at": "2026-06-12T12:00:00Z",
    }


def test_build_highlight_markdown_includes_chart_and_cross_links() -> None:
    title, excerpt, content = build_highlight_markdown(
        model_result=_model_result(),
        chart_url="https://greatcommissionbenchmark.ai/api/files/highlight.svg",
    )

    assert title.startswith("Model Highlight:")
    assert "82.4" in excerpt
    assert "## At a glance" in content
    assert "![GPT Highlight 1 GCB tier score chart]" in content
    assert "leaderboard/models/openai%2Fgpt-highlight-1" in content
    assert "greatcommissionbenchmark.ai/leaderboard" in content
    assert "greatcommissionbenchmark.ai/insights" in content
    assert "greatcommissionbenchmark.ai/contribute" in content
    assert "greatcommissionbenchmark.ai/newsletter" in content


def test_build_highlight_markdown_links_source_review() -> None:
    result = {
        **_model_result(),
        "model_id": "anthropic/claude-opus-4.8-fast",
        "name": "Claude Opus 4.8 Fast",
        "provider": "anthropic",
        "overall_score": 43.0,
    }
    _, _, content = build_highlight_markdown(
        model_result=result,
        source_post={
            "title": _review_post()["title"],
            "url": "https://greatcommissionbenchmark.ai/insights/anthropicclaude-opus-48-fast-capability-with-a-refusal-burden",
        },
    )

    assert "refusal burden" in content
    assert "Read the full insight" in content
    assert "anthropicclaude-opus-48-fast-capability-with-a-refusal-burden" in content


def test_highlight_header_svg_contains_required_tokens() -> None:
    svg = header_svg.generate_highlight_header_svg(
        model_name="GPT Highlight 1",
        provider_name="openai",
        score=82.4,
        model_id="openai/gpt-highlight-1",
    )
    assert "MODEL HIGHLIGHT" in svg
    assert "GPT Highlight 1" in svg
    assert "Openai" in svg
    assert "82.4" in svg


def test_highlight_tier_chart_svg_handles_missing_scores() -> None:
    svg = header_svg.generate_highlight_tier_chart_svg(
        model_name="GPT Highlight 1",
        overall_score=82.4,
        tier1_score=88.0,
        tier2_score=None,
        tier3_score=70.0,
    )
    assert "GCB TIER SCORECARD" in svg
    assert "Overall" in svg
    assert "Tier 1" in svg
    assert "Tier 2" in svg
    assert "Tier 3" in svg
    assert "—" in svg


def test_create_model_highlight_draft_generates_assets_and_draft(monkeypatch) -> None:
    captured: dict = {}

    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_category() -> str:
        return "highlight-category"

    async def fake_slug(title: str) -> dict:
        assert "highlight" in title.lower()
        return {"slug": "gpt-highlight-1-highlight"}

    async def fake_header(**kwargs) -> dict:
        captured["header"] = kwargs
        return {"url": "https://greatcommissionbenchmark.ai/api/files/header.svg"}

    async def fake_chart(**kwargs) -> dict:
        captured["chart"] = kwargs
        return {"url": "https://greatcommissionbenchmark.ai/api/files/chart.svg"}

    async def fake_create_post(**kwargs) -> dict:
        captured["post"] = kwargs
        return {
            "id": "post-1",
            "title": kwargs["title"],
            "slug": kwargs["slug"],
            "status": "draft",
            "featured_image_url": kwargs.get("featured_image_url"),
        }

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(server, "_highlights_category_id", fake_category)
    monkeypatch.setattr(blog, "generate_slug", fake_slug)
    monkeypatch.setattr(header_svg, "generate_and_upload_highlight_header", fake_header)
    monkeypatch.setattr(header_svg, "generate_and_upload_highlight_chart", fake_chart)
    monkeypatch.setattr(blog, "create_post", fake_create_post)

    result = asyncio.run(server.create_model_highlight_draft("openai/gpt-highlight-1"))

    assert result["status"] == "draft"
    assert result["highlight_header_auto_generated"] is True
    assert result["highlight_chart_auto_generated"] is True
    assert result["highlights_category_applied"] is True
    assert captured["post"]["model_ids"] == ["openai/gpt-highlight-1"]
    assert captured["post"]["category_ids"] == ["highlight-category"]
    assert "chart.svg" in captured["post"]["content"]


def test_resolve_model_highlight_context_finds_review_post_by_url(monkeypatch) -> None:
    async def fake_model_result(model_id: str) -> dict:
        assert model_id == "anthropic/claude-opus-4.8-fast"
        return {
            "model_id": model_id,
            "name": "Claude Opus 4.8 Fast",
            "provider": "anthropic",
            "overall_score": 43.0,
        }

    async def fake_list_posts(**kwargs) -> dict:
        return {"items": [_review_post()], "total": 1}

    async def fake_list_published(limit: int = 100) -> dict:
        return {
            "models": [
                {
                    "model_id": "anthropic/claude-opus-4.8-fast",
                    "name": "Claude Opus 4.8 Fast",
                    "provider": "anthropic",
                    "overall_score": 43.0,
                }
            ],
            "total": 1,
        }

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(blog, "list_posts", fake_list_posts)
    import gcb_mcp.public_api as public_api

    monkeypatch.setattr(public_api, "list_published_models", fake_list_published)

    result = asyncio.run(
        server.resolve_model_highlight_context(
            "https://greatcommissionbenchmark.ai/insights/anthropicclaude-opus-48-fast-capability-with-a-refusal-burden"
        )
    )

    assert result["resolved_model_id"] == "anthropic/claude-opus-4.8-fast"
    assert result["published_review_post"]["id"] == "review-post-1"
    assert result["recommended_action"] == "create_highlight_draft"


def test_create_model_highlight_draft_uses_resolved_review_context(monkeypatch) -> None:
    captured: dict = {}

    async def fake_context(_query: str) -> dict:
        model = {
            **_model_result(),
            "model_id": "anthropic/claude-opus-4.8-fast",
            "name": "Claude Opus 4.8 Fast",
            "provider": "anthropic",
            "overall_score": 43.0,
        }
        return {
            "resolved_model_id": "anthropic/claude-opus-4.8-fast",
            "model": model,
            "published_review_post": {
                "id": "review-post-1",
                "title": _review_post()["title"],
                "url": "https://greatcommissionbenchmark.ai/insights/anthropicclaude-opus-48-fast-capability-with-a-refusal-burden",
            },
            "existing_highlight_post": None,
            "recommended_action": "create_highlight_draft",
        }

    async def fake_category() -> str:
        return "highlight-category"

    async def fake_slug(title: str) -> dict:
        return {"slug": "claude-opus-48-fast-highlight"}

    async def fake_create_post(**kwargs) -> dict:
        captured["post"] = kwargs
        return {
            "id": "post-2",
            "title": kwargs["title"],
            "slug": kwargs["slug"],
            "status": "draft",
        }

    monkeypatch.setattr(server, "_resolve_model_highlight_context_impl", fake_context)
    monkeypatch.setattr(server, "_highlights_category_id", fake_category)
    monkeypatch.setattr(blog, "generate_slug", fake_slug)
    monkeypatch.setattr(blog, "create_post", fake_create_post)

    result = asyncio.run(
        server.create_model_highlight_draft(
            "https://greatcommissionbenchmark.ai/insights/anthropicclaude-opus-48-fast-capability-with-a-refusal-burden",
            auto_generate_header=False,
            auto_generate_chart=False,
        )
    )

    assert result["status"] == "draft"
    assert result["model_id"] == "anthropic/claude-opus-4.8-fast"
    assert captured["post"]["model_ids"] == ["anthropic/claude-opus-4.8-fast"]
    assert "Read the full insight" in captured["post"]["content"]
    assert "refusal burden" in captured["post"]["content"]
