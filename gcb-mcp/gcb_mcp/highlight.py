"""Brief model-highlight draft assembly for email-first announcements."""

from __future__ import annotations

from typing import Any

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
    lines.append(
        f"{name} is worth a focused look because the result gives ministry and technical leaders "
        f"a fast read on how the model behaves under Great Commission-shaped tasks. The scorecard is from "
        f"the **{benchmark_version}** test set, so use it as a practical signal alongside local policy, "
        "pastoral judgment, and hands-on evaluation.\n\n"
    )
    lines.append("## Explore next\n\n")
    lines.append(
        f"- **[Open the full benchmark result]({model_link})**\n"
        f"- **[Compare on the leaderboard]({LEADERBOARD_URL})**\n"
        f"- **[Read more GCB insights]({INSIGHTS_URL})**\n"
        f"- **[Sponsor or run a test]({CONTRIBUTE_URL})**\n"
        f"- **[Subscribe for future updates]({NEWSLETTER_URL})**\n"
    )
    lines.append(
        "\nGCB scores are decision support, not a substitute for spiritual discernment, doctrine, "
        "or local accountability.\n"
    )

    return title, excerpt, "".join(lines)
