"""Monthly newsletter draft assembly (leaderboard + blog join)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from urllib.parse import quote

SelectionMode = Literal["overall_score", "tier1_score"]

INSIGHTS_BASE = "https://greatcommissionbenchmark.ai/insights"
SITE_MODEL_BASE = "https://greatcommissionbenchmark.ai/leaderboard/models"


def _parse_completed_at(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_completed_human(completed_at: str | None) -> str:
    """Render API timestamps as calendar dates (UTC), e.g. April 15, 2026."""
    dt = _parse_completed_at(completed_at)
    if dt is None:
        return (str(completed_at).strip() if completed_at else "") or "—"
    month_name = dt.strftime("%B")
    return f"{month_name} {dt.day}, {dt.year}"


def format_newsletter_header_dateline(
    month_label: str | None = None,
    *,
    now: datetime | None = None,
) -> str:
    """Dateline for newsletter hero SVG, e.g. ``April, 2026`` (comma after month).

    ``month_label`` is typically ``strftime(\"%B %Y\")`` (``April 2026``); a comma
    is inserted after the month name. When omitted, uses ``now`` (UTC default: today).
    """
    ref = now or datetime.now(timezone.utc)
    if month_label and str(month_label).strip():
        parts = str(month_label).strip().split()
        if len(parts) >= 2:
            return f"{parts[0]}, {' '.join(parts[1:])}"
        return str(month_label).strip()
    return ref.strftime("%B, %Y")


def clip_description(text: Any, max_len: int = 280) -> str | None:
    """Single-line catalog description for newsletter copy; None if empty."""
    if text is None:
        return None
    raw = str(text).strip()
    if not raw:
        return None
    single = " ".join(raw.split())
    if len(single) <= max_len:
        return single
    return single[: max_len - 1].rstrip() + "…"


def _score(entry: dict[str, Any], mode: SelectionMode) -> float:
    if mode == "tier1_score":
        v = entry.get("tier1_score")
    else:
        v = entry.get("overall_score")
    if v is None:
        return float("-inf")
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("-inf")


def filter_and_rank_models(
    models: list[dict[str, Any]],
    *,
    days_back: int,
    selection: SelectionMode,
    now: datetime | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (in_window_sorted_by_completed_desc, in_window_sorted_by_score_desc)."""
    ref = now or datetime.now(timezone.utc)
    cutoff = ref - timedelta(days=days_back)
    in_window: list[dict[str, Any]] = []
    for m in models:
        completed = _parse_completed_at(m.get("completed_at"))
        if completed is None or completed < cutoff:
            continue
        in_window.append(m)

    by_date = sorted(
        in_window,
        key=lambda x: _parse_completed_at(x.get("completed_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    by_score = sorted(
        in_window,
        key=lambda x: (_score(x, selection), _parse_completed_at(x.get("completed_at")) or datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )
    return by_date, by_score


def insight_url(slug: str) -> str:
    return f"{INSIGHTS_BASE}/{slug}"


def model_page_url(model_id: str) -> str:
    return f"{SITE_MODEL_BASE}/{quote(model_id, safe='')}"


@dataclass
class PostMatch:
    slug: str
    title: str
    featured_image_url: str | None
    model_id: str


def index_posts_by_model_id(items: list[dict[str, Any]]) -> dict[str, PostMatch]:
    """Map OpenRouter model_id -> first published post that lists the model."""
    out: dict[str, PostMatch] = {}
    for item in items:
        slug = item.get("slug") or ""
        title = item.get("title") or ""
        img = item.get("featured_image_url")
        for rel in item.get("related_models") or []:
            mid = rel.get("model_id")
            if not mid or mid in out:
                continue
            out[str(mid)] = PostMatch(
                slug=str(slug),
                title=str(title),
                featured_image_url=str(img) if img else None,
                model_id=str(mid),
            )
    return out


def build_newsletter_markdown(
    *,
    month_label: str,
    window_days: int,
    selection: SelectionMode,
    spotlight: list[dict[str, Any]],
    all_in_window: list[dict[str, Any]],
    post_by_model: dict[str, PostMatch],
) -> tuple[str, str, str]:
    """Return (title, excerpt, markdown_content)."""
    title = (
        f"Great Commission Benchmark — Newsletter, {month_label}: "
        "New tests, top picks for ministry"
    )

    if selection == "overall_score":
        excerpt = (
            f"In the last {window_days} days on the Great Commission Benchmark, we spotlight two models "
            "with the strongest **overall scores** among new publications, plus every new leaderboard "
            "entry in this window."
        )
    else:
        excerpt = (
            f"In the last {window_days} days on the Great Commission Benchmark, we spotlight two models "
            "picked with extra weight on **Tier 1 (ministry-task) performance** among new publications—but "
            "we only quote the simple **overall score** here. See each model’s page for full tier detail, "
            "plus every new leaderboard entry in this window."
        )

    lines: list[str] = []
    lines.append(f"# {title}\n")
    lines.append(
        "**Great Commission Benchmark** is an independent evaluation of how AI models respond when "
        "the work sounds like real Great Commission ministry—research, discipleship, evangelism, "
        "and integrity under pressure. This digest highlights recent public test results.\n"
    )
    lines.append("## At a glance\n")
    lines.append(
        "- **Why this exists:** We help ministry and technical leaders steward AI for Great Commission faithfulness—not hype.\n"
        "- **What changed:** New benchmark runs hit the public leaderboard in the window below.\n"
        "- **What to do next:** Read the spotlight reviews, scan the release list, then explore the leaderboard or contribute a test.\n"
    )
    lines.append("---\n")
    lines.append("## Spotlight: two models to watch\n")
    lines.append(
        "Among the models **newly published** on our leaderboard in this window, these two ranked highest for this issue. "
        "Below is each model’s **overall score** (composite 0–100) and where to read more.\n"
    )

    for i, m in enumerate(spotlight, start=1):
        mid = m.get("model_id") or ""
        name = m.get("name") or mid
        provider = m.get("provider") or ""
        overall = m.get("overall_score")
        desc = clip_description(m.get("description"), max_len=320)
        match = post_by_model.get(str(mid))
        review_link = insight_url(match.slug) if match and match.slug else None
        model_link = model_page_url(str(mid))

        lines.append(f"### {i}. {name}\n")
        if provider:
            lines.append(f"*{provider}*\n")
        if desc:
            lines.append(f"> {desc}\n")
        lines.append(
            f"- **Overall score:** **{overall}** / 100  \n"
            f"- **[See full benchmark result]({model_link})**\n"
        )
        if review_link:
            lines.append(f"- **[Read the insight article]({review_link})**\n")

    lines.append(
        "\n\nOverall scores summarize automated testing across ministry-shaped scenarios—use them alongside Scripture, "
        "sound doctrine, and your team's policies—not as a substitute for spiritual discernment.\n"
    )
    lines.append("---\n")
    lines.append(f"## New on the leaderboard (last {window_days} days)\n")
    lines.append(
        "Here is everything **newly published** in this window, newest first. "
        "Open **View result** for scores and charts; open **Insight** when we have published commentary for that model.\n"
    )
    lines.append("| Model | About (short) | Published (UTC) | View result | Insight |\n")
    lines.append("| --- | --- | --- | --- | --- |\n")
    for m in all_in_window:
        mid = str(m.get("model_id") or "")
        name = (m.get("name") or mid).replace("|", "\\|")
        about_raw = clip_description(m.get("description"), max_len=90)
        about = (about_raw or "—").replace("|", "\\|")
        completed = format_completed_human(
            str(m.get("completed_at")) if m.get("completed_at") else None
        ).replace("|", "\\|")
        ml = model_page_url(mid)
        pm = post_by_model.get(mid)
        ins = f"[Read]({insight_url(pm.slug)})" if pm and pm.slug else "—"
        lines.append(f"| {name} | {about} | {completed} | [View result]({ml}) | {ins} |\n")

    lines.append("---\n")
    lines.append("## Explore, test, and serve\n")
    lines.append(
        "- **Explore the leaderboard:** [greatcommissionbenchmark.ai/leaderboard](https://greatcommissionbenchmark.ai/leaderboard)\n"
        "- **Read more insights:** [greatcommissionbenchmark.ai/insights](https://greatcommissionbenchmark.ai/insights)\n"
        "- **Sponsor or run a test:** [greatcommissionbenchmark.ai/contribute](https://greatcommissionbenchmark.ai/contribute)\n"
        "- **Volunteer (moderation / advisory):** [greatcommissionbenchmark.ai/contribute](https://greatcommissionbenchmark.ai/contribute)\n"
        "- **Subscribe for updates:** [greatcommissionbenchmark.ai/newsletter](https://greatcommissionbenchmark.ai/newsletter)\n"
    )
    lines.append("\n*“Test everything; hold fast what is good” (1 Thessalonians 5:21)—and keep making disciples (Matthew 28:19–20).*\n")

    return title, excerpt, "".join(lines)
