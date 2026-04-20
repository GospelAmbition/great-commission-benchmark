"""Tests for newsletter selection and URL helpers."""

from datetime import datetime, timedelta, timezone

from gcb_mcp.newsletter import (
    clip_description,
    filter_and_rank_models,
    format_completed_human,
    index_posts_by_model_id,
    insight_url,
    model_page_url,
)


def test_model_page_url_encodes_slash():
    assert "anthropic%2Fclaude-3-opus" in model_page_url("anthropic/claude-3-opus")


def test_insight_url():
    assert insight_url("my-slug").endswith("/insights/my-slug")


def test_format_completed_human():
    assert "2026" in format_completed_human("2026-04-15T12:00:00+00:00")
    assert "April" in format_completed_human("2026-04-15T12:00:00+00:00")
    assert format_completed_human(None) in ("", "—")


def test_clip_description():
    assert clip_description(None) is None
    assert clip_description("  hello  world  ") == "hello world"
    long = "x" * 300
    out = clip_description(long, max_len=20)
    assert out is not None
    assert len(out) == 20
    assert out.endswith("…")


def test_filter_and_rank_models_window_and_scores():
    ref = datetime(2026, 4, 15, 12, 0, 0, tzinfo=timezone.utc)
    old = (ref - timedelta(days=40)).isoformat()
    mid = (ref - timedelta(days=5)).isoformat()
    recent = (ref - timedelta(days=1)).isoformat()

    models = [
        {
            "model_id": "a/a",
            "name": "Old",
            "completed_at": old,
            "overall_score": 99,
            "tier1_score": 10,
        },
        {
            "model_id": "b/b",
            "name": "Mid",
            "completed_at": mid,
            "overall_score": 50,
            "tier1_score": 90,
        },
        {
            "model_id": "c/c",
            "name": "Recent",
            "completed_at": recent,
            "overall_score": 80,
            "tier1_score": 20,
        },
    ]

    by_date, by_score = filter_and_rank_models(
        models, days_back=30, selection="overall_score", now=ref
    )
    assert [m["model_id"] for m in by_date] == ["c/c", "b/b"]
    assert by_score[0]["model_id"] == "c/c"

    _, by_t1 = filter_and_rank_models(
        models, days_back=30, selection="tier1_score", now=ref
    )
    assert by_t1[0]["model_id"] == "b/b"


def test_index_posts_by_model_id_first_wins():
    items = [
        {
            "slug": "first",
            "title": "A",
            "featured_image_url": "https://x/a.png",
            "related_models": [{"model_id": "openai/gpt-4o"}],
        },
        {
            "slug": "second",
            "title": "B",
            "featured_image_url": None,
            "related_models": [{"model_id": "openai/gpt-4o"}],
        },
    ]
    idx = index_posts_by_model_id(items)
    assert idx["openai/gpt-4o"].slug == "first"
