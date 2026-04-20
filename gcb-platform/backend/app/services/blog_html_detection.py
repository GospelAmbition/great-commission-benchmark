"""Heuristics to detect legacy HTML stored in blog ``content`` / ``excerpt`` fields.

Markdown-first posts may still contain occasional inline HTML (e.g. ``<img>``).
These helpers favor **high-confidence** structural HTML (block tags, legacy
WordPress-style wrappers) for migration triage.
"""

from __future__ import annotations

import re
from typing import Literal

Confidence = Literal["high", "medium", "low", "none"]

# Block / document-level tags typical of HTML-first CMS exports
_BLOCK_TAG_RE = re.compile(
    r"<\s*(p|div|section|article|header|footer|nav|main|figure|table|tbody|thead|tr|td|th|ul|ol|li|blockquote|pre)\b",
    re.IGNORECASE | re.DOTALL,
)
_HEADING_TAG_RE = re.compile(r"<\s*h[1-6]\b", re.IGNORECASE)
_BR_RE = re.compile(r"<\s*br\s*/?>", re.IGNORECASE)
_INLINE_WRAPPER_RE = re.compile(r"<\s*(span|font|center)\b", re.IGNORECASE)
_DOCTYPE_OR_HTML_RE = re.compile(r"<\s*!DOCTYPE\b|<\s*html\b", re.IGNORECASE)


def _strip_for_scan(text: str) -> str:
    return (text or "").strip()


def content_confidence(text: str | None) -> Confidence:
    """Return how strongly ``text`` looks like HTML body copy rather than Markdown."""
    s = _strip_for_scan(text or "")
    if not s:
        return "none"

    if _DOCTYPE_OR_HTML_RE.search(s):
        return "high"

    block_hits = len(_BLOCK_TAG_RE.findall(s))
    heading_hits = len(_HEADING_TAG_RE.findall(s))
    br_hits = len(_BR_RE.findall(s))

    if block_hits >= 2 or (block_hits >= 1 and heading_hits >= 1):
        return "high"
    if block_hits == 1 or heading_hits >= 1 or br_hits >= 3:
        return "medium"
    if _INLINE_WRAPPER_RE.search(s) or br_hits >= 1 or "<img" in s.lower():
        return "low"
    return "none"


def looks_like_legacy_html(text: str | None, min_confidence: Confidence = "medium") -> bool:
    """Whether ``text`` should be treated as legacy HTML for migration."""
    order: tuple[Confidence, ...] = ("none", "low", "medium", "high")
    c = content_confidence(text)
    return order.index(c) >= order.index(min_confidence)


def markdownish_score(text: str | None) -> float:
    """Rough signal 0–1 that prose is already Markdown-first (not used for gating)."""
    s = text or ""
    if not s.strip():
        return 0.0
    lines = [ln for ln in s.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    mdish = sum(
        1
        for ln in lines
        if ln.lstrip().startswith(("#", "-", "*", ">"))
        or re.match(r"^\s*\[[^\]]+\]\([^)]+\)\s*$", ln)
        or re.match(r"^\s*\|", ln)
    )
    return min(1.0, mdish / len(lines))
