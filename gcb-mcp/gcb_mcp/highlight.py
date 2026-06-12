"""Brief model-highlight draft assembly and discovery helpers."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import unquote, urlparse

from gcb_mcp.newsletter import (
    clip_description,
    format_completed_human,
    model_page_url,
    publisher_display_name,
)


LEADERBOARD_URL = "https://greatcommissionbenchmark.ai/leaderboard"
INSIGHTS_URL = "https://greatcommissionbenchmark.ai/insights"
CONTRIBUTE_URL = "https://greatcommissionbenchmark.ai/contribute"
NEWSLETTER_URL = "https://greatcommissionbenchmark.ai/newsletter"

_CATEGORY_LABELS: dict[str, str] = {
    "1.1": "Missiological Research",
    "1.2": "Evangelistic Material",
    "1.3": "Apologetic Work",
    "1.4": "Conversational Ministry Tools",
    "1.5": "Intercessory Prayer",
    "1.6": "Sensitive Biblical Vocabulary",
    "1.7": "Difficult Scripture Passages",
    "2.1": "Christ's Exclusive Claim",
    "2.2": "Universal Sin",
    "2.3": "Final Judgment",
    "2.4": "Christ's Lordship",
    "2.5": "Repentance and Faith",
    "2.6": "The Great Commission Calling",
    "3.1": "God's Existence",
    "3.2": "Jesus in History",
    "3.3": "The Crucifixion",
    "3.4": "The Resurrection",
    "3.5": "Human Sinfulness",
    "3.6": "Salvation Through Faith",
}


def score_text(value: Any) -> str:
    """Render a nullable numeric score for public copy."""
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "not available"


def normalize_lookup_text(value: Any) -> str:
    """Normalize user input, slugs, titles, and model IDs for fuzzy matching."""
    text = unquote(str(value or "")).strip().lower()
    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        text = parsed.path.rsplit("/", 1)[-1] or parsed.netloc
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_slug_or_query(value: str) -> str:
    """Return the most useful lookup token from a raw query or public URL."""
    raw = str(value or "").strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        last_path = parsed.path.strip("/").rsplit("/", 1)[-1]
        return unquote(last_path or raw)
    return raw


def post_live_url(post: dict[str, Any]) -> str | None:
    """Build a public insight URL from a blog post list/detail payload."""
    slug = post.get("slug")
    if isinstance(slug, str) and slug:
        return f"{INSIGHTS_URL}/{slug}"
    return None


def related_model_ids(post: dict[str, Any]) -> list[str]:
    """Extract linked OpenRouter model IDs from runner blog API payloads."""
    ids: list[str] = []
    for item in post.get("related_models") or []:
        if not isinstance(item, dict):
            continue
        model_id = item.get("model_id")
        if isinstance(model_id, str) and model_id and model_id not in ids:
            ids.append(model_id)
    return ids


def compact_post(post: dict[str, Any]) -> dict[str, Any]:
    """Return stable discovery metadata for a blog post."""
    return {
        "id": str(post.get("id") or ""),
        "title": post.get("title"),
        "slug": post.get("slug"),
        "status": post.get("status"),
        "excerpt": post.get("excerpt"),
        "url": post_live_url(post),
        "model_ids": related_model_ids(post),
        "published_at": post.get("published_at"),
        "created_at": post.get("created_at"),
    }


def is_highlight_post(post: dict[str, Any]) -> bool:
    """Heuristic for identifying existing Highlight posts."""
    title = normalize_lookup_text(post.get("title"))
    slug = normalize_lookup_text(post.get("slug"))
    categories = " ".join(
        normalize_lookup_text(cat.get("name") or cat.get("slug"))
        for cat in (post.get("categories") or [])
        if isinstance(cat, dict)
    )
    haystack = f"{title} {slug} {categories}"
    return "highlight" in haystack or "model highlight" in haystack


def match_score(query: str, *candidates: Any) -> float:
    """Score a candidate against a natural-language highlight query."""
    q = normalize_lookup_text(query)
    if not q:
        return 0.0
    best = 0.0
    for candidate in candidates:
        c = normalize_lookup_text(candidate)
        if not c:
            continue
        if q == c:
            best = max(best, 1.0)
        elif q in c or c in q:
            best = max(best, 0.92)
        else:
            best = max(best, SequenceMatcher(None, q, c).ratio())
    return best


def _score_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _category_label(category_id: str) -> str:
    label = _CATEGORY_LABELS.get(category_id)
    return f"{category_id} {label}" if label else category_id


def strongest_and_weakest(category_scores: dict[str, Any] | None) -> tuple[tuple[str, float] | None, tuple[str, float] | None]:
    """Return best and weakest category score pairs, ignoring malformed values."""
    scored: list[tuple[str, float]] = []
    for key, raw in (category_scores or {}).items():
        val = _score_float(raw)
        if val is not None:
            scored.append((str(key), val))
    if not scored:
        return None, None
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[0], scored[-1]


def build_highlight_markdown(
    *,
    model_result: dict[str, Any],
    chart_url: str | None = None,
    source_post: dict[str, Any] | None = None,
) -> tuple[str, str, str]:
    """Return ``(title, excerpt, markdown_content)`` for a brief Highlight."""
    model_id = str(model_result.get("model_id") or "")
    name = str(model_result.get("name") or model_id or "Model")
    provider = str(model_result.get("provider") or (model_id.split("/")[0] if "/" in model_id else ""))
    provider_display = publisher_display_name(provider)

    overall = score_text(model_result.get("overall_score"))
    tier1 = score_text(model_result.get("tier1_score"))
    tier2 = score_text(model_result.get("tier2_score"))
    tier3 = score_text(model_result.get("tier3_score"))
    total_questions = model_result.get("total_questions") or 150
    completed = format_completed_human(model_result.get("completed_at"))
    benchmark_version = model_result.get("benchmark_version") or "current public benchmark"
    desc = clip_description(model_result.get("description"), max_len=220)
    source_post = source_post or {}
    source_title = str(source_post.get("title") or "").strip()
    source_url = str(source_post.get("url") or "").strip()

    best, weakest = strongest_and_weakest(model_result.get("category_scores"))

    title = f"Model Highlight: {name} on the Great Commission Benchmark"
    excerpt = (
        f"{name} scored {overall} overall on the Great Commission Benchmark, "
        "with quick links into the full result and leaderboard context."
    )

    model_link = model_page_url(model_id) if model_id else LEADERBOARD_URL

    bullets = [
        f"- **Overall score:** **{overall} / 100** across **{total_questions}** benchmark items.",
        f"- **Tier scores:** Tier 1 **{tier1}**, Tier 2 **{tier2}**, Tier 3 **{tier3}**.",
        f"- **Publisher:** {provider_display}; latest public GCB result completed **{completed}**.",
    ]
    if best:
        bullets.append(f"- **Strongest signal:** {_category_label(best[0])} at **{best[1]:.1f}**.")
    if weakest and (not best or weakest[0] != best[0]):
        bullets.append(f"- **Watch area:** {_category_label(weakest[0])} at **{weakest[1]:.1f}**.")

    lines: list[str] = []
    lines.append(f"# {title}\n\n")
    if desc:
        lines.append(f"> {desc}\n\n")
    lines.append("## At a glance\n\n")
    lines.append("\n".join(bullets[:5]))
    lines.append("\n\n")
    if chart_url:
        lines.append(f"![{name} GCB tier score chart]({chart_url})\n\n")
    lines.append("## Why it matters\n\n")
    if source_title and "refusal burden" in source_title.lower():
        lines.append(
            f"{name} is a useful reminder that capability and deployability are not the same thing. "
            "The published result points to a refusal burden: the model may be strong enough to help, "
            "while still declining enough valid ministry-shaped work to affect practical reliability.\n\n"
        )
    else:
        lines.append(
            f"{name} is worth a focused look because the result gives ministry and technical leaders "
            f"a fast read on how the model behaves under Great Commission-shaped tasks. The scorecard is from "
            f"the **{benchmark_version}** test set, so use it as a practical signal alongside local policy, "
            "pastoral judgment, and hands-on evaluation.\n\n"
        )
    lines.append("## Explore next\n\n")
    explore = [f"- **[Open the full benchmark result]({model_link})**"]
    if source_url:
        explore.append(f"- **[Read the full insight]({source_url})**")
    explore.extend(
        [
            f"- **[Compare on the leaderboard]({LEADERBOARD_URL})**",
            f"- **[Read more GCB insights]({INSIGHTS_URL})**",
            f"- **[Sponsor or run a test]({CONTRIBUTE_URL})**",
            f"- **[Subscribe for future updates]({NEWSLETTER_URL})**",
        ]
    )
    lines.append("\n".join(explore) + "\n")
    lines.append(
        "\nGCB scores are decision support, not a substitute for spiritual discernment, doctrine, "
        "or local accountability.\n"
    )

    return title, excerpt, "".join(lines)
