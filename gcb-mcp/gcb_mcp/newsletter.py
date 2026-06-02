"""Monthly newsletter draft assembly (leaderboard + blog join)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from urllib.parse import quote

import httpx

SelectionMode = Literal["overall_score", "tier1_score"]

logger = logging.getLogger(__name__)

INSIGHTS_BASE = "https://greatcommissionbenchmark.ai/insights"
SITE_MODEL_BASE = "https://greatcommissionbenchmark.ai/leaderboard/models"
_OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Friendly org names for newsletter prose (OpenRouter provider slug → display)
_PROVIDER_DISPLAY: dict[str, str] = {
    "x-ai": "XAI",
    "openai": "OpenAI",
    "google": "Google",
    "anthropic": "Anthropic",
    "meta-llama": "Meta",
    "mistralai": "Mistral AI",
    "microsoft": "Microsoft",
    "moonshotai": "Moonshot AI",
    "qwen": "Qwen",
    "deepseek": "DeepSeek",
    "z-ai": "Z.AI",
    "amazon": "Amazon",
    "ibm-granite": "IBM",
    "essentialai": "Essential AI",
    "bytedance-seed": "ByteDance Seed",
    "xiaomi": "Xiaomi",
    "minimax": "MiniMax",
}

# GCB category ids → short public labels (see insights/_article_review_prompt.md)
_CATEGORY_SOFT_LABEL: dict[str, str] = {
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


def _ordinal_day(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def publisher_display_name(provider_slug: str) -> str:
    s = (provider_slug or "").strip().lower()
    if s in _PROVIDER_DISPLAY:
        return _PROVIDER_DISPLAY[s]
    if not s:
        return "the listed provider"
    return s.replace("-", " ").title()


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


def openrouter_created_to_human(created: Any) -> str | None:
    """Turn OpenRouter ``created`` (unix seconds or ISO-ish string) into a soft UTC date phrase."""
    if created is None:
        return None
    try:
        if isinstance(created, (int, float)):
            dt = datetime.fromtimestamp(float(created), tz=timezone.utc)
        else:
            raw = str(created).strip()
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
        return f"{dt.strftime('%B')} {_ordinal_day(dt.day)}, {dt.year}"
    except (OSError, OverflowError, TypeError, ValueError):
        return None


async def fetch_openrouter_created_map(model_ids: set[str]) -> dict[str, str | None]:
    """Map ``model_id`` → human listing date from OpenRouter's public ``/models`` snapshot."""
    if not model_ids:
        return {}
    out: dict[str, str | None] = {mid: None for mid in model_ids}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(_OPENROUTER_MODELS_URL)
    except httpx.RequestError as exc:
        logger.warning("OpenRouter models fetch failed: %s", exc)
        return out

    if not resp.is_success:
        logger.warning("OpenRouter models HTTP %s", resp.status_code)
        return out

    try:
        payload = resp.json()
    except ValueError:
        return out

    rows = payload.get("data")
    if not isinstance(rows, list):
        return out

    lowered = {mid.lower(): mid for mid in model_ids}
    for item in rows:
        iid = item.get("id")
        if not isinstance(iid, str):
            continue
        canon = lowered.get(iid.lower())
        if not canon:
            continue
        out[canon] = openrouter_created_to_human(item.get("created"))

    return out


def _sorted_category_scores(category_scores: dict[str, Any] | None) -> list[tuple[float, str]]:
    if not category_scores:
        return []
    scored: list[tuple[float, str]] = []
    for key, val in category_scores.items():
        try:
            scored.append((float(val), str(key)))
        except (TypeError, ValueError):
            continue
    scored.sort(reverse=True)
    return scored


def spotlight_benchmark_soft_sentence(
    entry: dict[str, Any],
    category_scores: dict[str, Any] | None,
    *,
    min_highlight: float = 73.0,
    min_runner_up: float = 68.0,
) -> str:
    """Warm, plain sentence about overall GCB run plus a highlight lane when scores justify it."""
    try:
        nq = int(entry.get("total_questions") or 150)
    except (TypeError, ValueError):
        nq = 150

    ov = entry.get("overall_score")
    try:
        o = float(ov) if ov is not None else None
    except (TypeError, ValueError):
        o = None

    if o is None:
        perf = "did credibly"
    elif o >= 82:
        perf = "performed exceptionally well"
    elif o >= 74:
        perf = "performed very well"
    elif o >= 66:
        perf = "performed well"
    elif o >= 58:
        perf = "held its own"
    else:
        perf = "showed a more mixed profile"

    scored = _sorted_category_scores(category_scores)
    first_label: str | None = None
    second_label: str | None = None
    if scored:
        v0, k0 = scored[0]
        if v0 >= min_highlight:
            first_label = _CATEGORY_SOFT_LABEL.get(k0, f"category {k0}")
        if len(scored) > 1 and first_label:
            v1, k1 = scored[1]
            if v1 >= min_runner_up:
                second_label = _CATEGORY_SOFT_LABEL.get(k1, f"category {k1}")

    base = f"It {perf} on the {nq} Great Commission Benchmark items we publish"
    if first_label and second_label and first_label != second_label:
        return f"{base}, particularly well in {first_label} and {second_label}."
    if first_label:
        return f"{base}, particularly well in {first_label}."
    return f"{base}."


async def build_spotlight_paragraphs(spotlight: list[dict[str, Any]]) -> dict[str, str]:
    """Three soft sentences: publisher, public listing date, gentle GCB summary."""
    from gcb_mcp.public_api import get_model_test_result  # noqa: PLC0415

    mids = {str(m.get("model_id")) for m in spotlight if m.get("model_id")}
    created_map = await fetch_openrouter_created_map(mids)

    out: dict[str, str] = {}
    for m in spotlight:
        mid = str(m.get("model_id") or "")
        if not mid:
            continue
        provider = str(m.get("provider") or (mid.split("/")[0] if "/" in mid else "unknown"))
        listing = created_map.get(mid)

        pub_disp = publisher_display_name(provider)
        s1 = f"The model is published by {pub_disp}."
        if listing:
            s2 = f"It was made available publicly {listing}."
        else:
            s2 = (
                "We were not able to confirm a public OpenRouter listing date from the catalog "
                "snapshot used for this issue."
            )

        detail = await get_model_test_result(mid)
        scores = detail.get("category_scores") if isinstance(detail, dict) and "error" not in detail else None
        s3 = spotlight_benchmark_soft_sentence(m, scores)

        out[mid] = f"{s1} {s2} {s3}"
    return out


def build_newsletter_markdown(
    *,
    month_label: str,
    window_days: int,
    selection: SelectionMode,
    spotlight: list[dict[str, Any]],
    post_by_model: dict[str, PostMatch],
    spotlight_paragraphs: dict[str, str] | None = None,
) -> tuple[str, str, str]:
    """Return (title, excerpt, markdown_content)."""
    title = (
        f"Great Commission Benchmark — Newsletter, {month_label}: "
        "New tests, top picks for ministry"
    )

    if selection == "overall_score":
        excerpt = (
            f"In the last {window_days} days on the Great Commission Benchmark, we spotlight two models "
            "with the strongest **overall scores** among new publications."
        )
    else:
        excerpt = (
            f"In the last {window_days} days on the Great Commission Benchmark, we spotlight two models "
            "picked with extra weight on **Tier 1 (ministry-task) performance** among new publications—but "
            "we only quote the simple **overall score** here. See each model’s page for full tier detail."
        )

    lines: list[str] = []
    lines.append(f"# {title}\n")
    lines.append(
        f"For **{month_label}**, **Great Commission Benchmark** rounds up how leading AI models behave when the prompts "
        "sound like real ministry—research, discipleship, evangelism, and integrity under pressure. "
        "Below you will find two spotlight models, ranked by your selected scoring lens for this issue, "
        f"drawn from runs newly published to the public leaderboard in the last {window_days} days.\n"
    )
    lines.append("## At a glance\n")
    lines.append(
        "- **Why read this:** GCB exists so ministry and technical leaders can steward AI with discernment—not trend-chasing.\n"
        f"- **What this issue covers:** Benchmark runs that reached the public leaderboard within the last **{window_days} days**.\n"
        "- **What to do next:** Read the two spotlights, then open the leaderboard or contribute a test run.\n"
    )
    lines.append("---\n")
    lines.append("## Spotlight: two models to watch\n")
    lines.append(
        "These are the two highest-ranked models **among new publications in this window** for the scoring mode "
        "selected for this newsletter. Each entry shows the **overall score** (0–100 composite) plus direct links "
        "to the benchmark record and any published insight article.\n"
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
        para = (spotlight_paragraphs or {}).get(str(mid), "").strip()
        if para:
            lines.append(para + "\n\n")
        elif provider:
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
