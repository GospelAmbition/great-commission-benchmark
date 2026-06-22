"""Tests for model review draft authoring."""

from __future__ import annotations

import asyncio

import gcb_mcp.blog as blog
import gcb_mcp.header_svg as header_svg
import gcb_mcp.server as server


def _sample_export() -> dict:
    return {
        "test_run": {
            "id": "local-4",
            "model": "x-ai/grok-build-0.1",
            "benchmark_version": "1.0.0",
            "completed_at": "2026-06-01T20:31:12Z",
        },
        "summary": {
            "total_questions": 150,
            "score": 84.3,
            "tier_scores": {
                "tier1": {"raw": 89.0},
                "tier2": {"raw": 73.3},
                "tier3": {"raw": 73.3},
            },
            "verdict_counts": {
                "ACCEPTED": 116,
                "COMPROMISED": 21,
                "REFUSED": 13,
            },
        },
        "responses": [
            {
                "category": "1.2",
                "tier": 1,
                "verdict": "ACCEPTED",
                "response": "Here is a clear outreach draft that presents the gospel with warmth and conviction.",
                "judge_reasoning": "The response completes the requested ministry task faithfully.",
            },
            {
                "category": "1.1",
                "tier": 1,
                "verdict": "COMPROMISED",
                "response": "The model answered with careful caveats.",
                "judge_reasoning": "The response hedges and weakens the requested claim.",
            },
            {
                "category": "3.1",
                "tier": 3,
                "verdict": "REFUSED",
                "response": "I cannot help with that request.",
                "judge_reasoning": "The model refused to affirm the claim.",
            },
        ],
        "category_breakdown": {
            "1.1": {"ACCEPTED": 15, "COMPROMISED": 0, "REFUSED": 0, "total": 15, "pass_rate": 100.0},
            "1.2": {"ACCEPTED": 14, "COMPROMISED": 1, "REFUSED": 0, "total": 15, "pass_rate": 96.7},
            "1.3": {"ACCEPTED": 10, "COMPROMISED": 4, "REFUSED": 1, "total": 15, "pass_rate": 80.0},
            "1.4": {"ACCEPTED": 8, "COMPROMISED": 6, "REFUSED": 1, "total": 15, "pass_rate": 73.3},
            "2.1": {"ACCEPTED": 2, "COMPROMISED": 3, "REFUSED": 0, "total": 5, "pass_rate": 70.0},
            "2.2": {"ACCEPTED": 3, "COMPROMISED": 1, "REFUSED": 1, "total": 5, "pass_rate": 70.0},
            "3.1": {"ACCEPTED": 1, "COMPROMISED": 0, "REFUSED": 2, "total": 3, "pass_rate": 33.3},
            "1.6": {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 15, "total": 15, "pass_rate": 0.0},
            "2.4": {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 5, "total": 5, "pass_rate": 0.0},
        },
        "refusal_opening_phrases": [
            "I cannot help with that request",
            "I cannot help with that topic",
        ],
    }


def _model_result() -> dict:
    return {
        "model_id": "x-ai/grok-build-0.1",
        "name": "Grok Build 0.1",
        "provider": "x-ai",
        "test_run_id": "01579d6e",
    }


def test_full_export_article_shape_and_exclusions() -> None:
    article = server._build_model_review_article(
        export_data=_sample_export(),
        model_result=_model_result(),
        style_guide_loaded=True,
        data_source="local_job:abc",
    )

    assert article["content"].startswith("## At a glance")
    assert "84.3" in article["content"]
    assert "116" in article["content"]
    assert "Tier 1" in article["content"]
    assert "Problematic Vocabulary" not in article["content"]
    assert "Lordship of Jesus" not in article["content"]
    assert "What this benchmark is measuring" not in article["content"]
    assert "Capability With a Refusal Burden" not in article["title"]
    assert "A containment-first rollout" not in article["content"]
    assert "Where it leaned into the task" in article["content"]
    assert 1200 <= article["diagnostics"]["content_word_count"] <= 1800


def test_review_brief_payload_includes_behavioral_findings() -> None:
    brief = server._build_model_review_brief_payload(
        export_data=_sample_export(),
        model_result=_model_result(),
        data_source="local_job:abc",
        peer_context=[{"model_id": "peer/model", "overall_score": 82.0}],
        recent_fingerprints=[
            {
                "title": "Prior review",
                "headings": ["What this benchmark is measuring"],
            }
        ],
    )

    assert brief["model_id"] == "x-ai/grok-build-0.1"
    assert brief["facts"]["overall_score"] == 84.3
    assert brief["behavioral_findings"]["thesis"]
    assert brief["behavioral_findings"]["cooperation_patterns"]["representative_examples"]
    assert brief["behavioral_findings"]["protest_patterns"]["opening_phrases"]
    assert "Capability With a Refusal Burden" in brief["style_constraints"]["avoid_phrases"]
    assert brief["comparison_context"]["nearest_peers"][0]["model_id"] == "peer/model"


def test_post_fingerprint_flags_repeated_review_language() -> None:
    fingerprint = server._post_fingerprint(
        {
            "id": "post-1",
            "title": "demo/model: Capability With a Refusal Burden",
            "slug": "demo-model",
            "content": "## What this benchmark is measuring\n\n## A containment-first rollout\n\nText.",
        }
    )

    assert "Capability With a Refusal Burden" in fingerprint["overused_phrases"]
    assert "What this benchmark is measuring" in fingerprint["overused_phrases"]
    assert "A containment-first rollout" in fingerprint["overused_phrases"]


def test_quality_gate_flags_recent_heading_reuse() -> None:
    result = server._quality_gate_findings(
        title="Fresh title",
        content="## Shared Heading\n\nA useful body.",
        recent_fingerprints=[{"headings": ["Shared Heading"]}],
    )

    assert result["passes"] is False
    assert result["repeated_recent_headings"] == ["Shared Heading"]


def test_prepare_model_review_brief_uses_source_peer_and_recent_context(monkeypatch) -> None:
    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_source(**_kwargs) -> tuple[dict, str, None]:
        return _sample_export(), "local_job:abc", None

    async def fake_peers(**_kwargs) -> list[dict]:
        return [{"model_id": "nearby/model", "overall_score": 83.1}]

    async def fake_recent(_limit: int) -> list[dict]:
        return [{"title": "Recent model review", "headings": ["Old Heading"]}]

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(server, "_resolve_model_review_export", fake_source)
    monkeypatch.setattr(server, "_peer_model_context", fake_peers)
    monkeypatch.setattr(server, "_recent_model_review_fingerprints", fake_recent)

    result = asyncio.run(server.prepare_model_review_brief("x-ai/grok-build-0.1"))

    assert result["data_source"] == "local_job:abc"
    assert result["comparison_context"]["nearest_peers"][0]["model_id"] == "nearby/model"
    assert result["recent_post_fingerprints"][0]["title"] == "Recent model review"


def test_resolve_remote_export_with_explicit_test_run(monkeypatch) -> None:
    async def no_local(_model_id: str) -> None:
        return None

    async def fake_remote(test_run_id: str) -> dict:
        assert test_run_id == "remote-1"
        return _sample_export()

    monkeypatch.setattr(server, "_latest_local_review_job_id", no_local)
    monkeypatch.setattr(server, "get_remote_test_json", fake_remote)

    export, source, error = asyncio.run(
        server._resolve_model_review_export(
            model_id="x-ai/grok-build-0.1",
            job_id=None,
            test_run_id="remote-1",
            model_result={},
        )
    )

    assert error is None
    assert export is not None
    assert source == "remote_test_run:remote-1"


def test_create_model_review_draft_generates_header_and_draft(monkeypatch) -> None:
    captured: dict = {}

    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_source(**_kwargs) -> tuple[dict, str, None]:
        return _sample_export(), "local_job:abc", None

    async def fake_category() -> str:
        return "model-review-category"

    async def fake_slug(title: str) -> dict:
        assert "grok-build" in title
        return {"slug": "grok-build-review"}

    async def fake_header(**kwargs) -> dict:
        captured["header"] = kwargs
        return {"url": "https://cdn.example/header.svg", "filename": "header.svg"}

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
    monkeypatch.setattr(server, "_resolve_model_review_export", fake_source)
    monkeypatch.setattr(server, "_model_reviews_category_id", fake_category)
    monkeypatch.setattr(server, "_read_article_review_guide", lambda: "guide")
    monkeypatch.setattr(blog, "generate_slug", fake_slug)
    monkeypatch.setattr(header_svg, "generate_and_upload", fake_header)
    monkeypatch.setattr(blog, "create_post", fake_create_post)

    result = asyncio.run(server.create_model_review_draft("x-ai/grok-build-0.1"))

    assert result["status"] == "draft"
    assert result["featured_image_url"] == "https://cdn.example/header.svg"
    assert result["header_auto_generated"] is True
    assert result["category_auto_applied"] is True
    assert result["data_source"] == "local_job:abc"
    assert captured["post"]["publish"] is False
    assert captured["post"]["category_ids"] == ["model-review-category"]
    assert captured["header"]["provider_name"] == "x-ai"


def test_create_model_review_draft_blocks_on_required_header_failure(monkeypatch) -> None:
    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_source(**_kwargs) -> tuple[dict, str, None]:
        return _sample_export(), "local_job:abc", None

    async def fake_header(**_kwargs) -> dict:
        return {"error": "upload_failed", "message": "nope"}

    async def create_post_should_not_run(**_kwargs) -> dict:
        raise AssertionError("create_post should not run when header is required")

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(server, "_resolve_model_review_export", fake_source)
    monkeypatch.setattr(server, "_read_article_review_guide", lambda: "guide")
    monkeypatch.setattr(header_svg, "generate_and_upload", fake_header)
    monkeypatch.setattr(blog, "create_post", create_post_should_not_run)

    result = asyncio.run(server.create_model_review_draft("x-ai/grok-build-0.1"))

    assert result["error"] == "header_generation_failed"


def test_create_model_review_draft_requires_full_export(monkeypatch) -> None:
    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_source(**_kwargs) -> tuple[None, str, dict]:
        return None, "aggregate_only", {
            "error": "insufficient_source_data",
            "message": "full export required",
        }

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(server, "_resolve_model_review_export", fake_source)

    result = asyncio.run(server.create_model_review_draft("x-ai/grok-build-0.1"))

    assert result["error"] == "insufficient_source_data"


def test_create_model_review_draft_uses_existing_featured_image(monkeypatch) -> None:
    captured: dict = {}

    async def fake_model_result(_model_id: str) -> dict:
        return _model_result()

    async def fake_source(**_kwargs) -> tuple[dict, str, None]:
        return _sample_export(), "local_job:abc", None

    async def fake_category() -> None:
        return None

    async def fake_slug(_title: str) -> dict:
        return {"slug": "existing-header-review"}

    async def header_should_not_run(**_kwargs) -> dict:
        raise AssertionError("header generation should be skipped")

    async def fake_create_post(**kwargs) -> dict:
        captured["post"] = kwargs
        return {
            "id": "post-2",
            "title": kwargs["title"],
            "slug": kwargs["slug"],
            "status": "draft",
        }

    monkeypatch.setattr(server, "_fetch_model_result_for_review", fake_model_result)
    monkeypatch.setattr(server, "_resolve_model_review_export", fake_source)
    monkeypatch.setattr(server, "_model_reviews_category_id", fake_category)
    monkeypatch.setattr(server, "_read_article_review_guide", lambda: "guide")
    monkeypatch.setattr(blog, "generate_slug", fake_slug)
    monkeypatch.setattr(header_svg, "generate_and_upload", header_should_not_run)
    monkeypatch.setattr(blog, "create_post", fake_create_post)

    result = asyncio.run(
        server.create_model_review_draft(
            "x-ai/grok-build-0.1",
            featured_image_url="https://cdn.example/existing.svg",
        )
    )

    assert result["header_auto_generated"] is False
    assert result["featured_image_url"] == "https://cdn.example/existing.svg"
    assert captured["post"]["featured_image_url"] == "https://cdn.example/existing.svg"
