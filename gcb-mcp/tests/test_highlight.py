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
