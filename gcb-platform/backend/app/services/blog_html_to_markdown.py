"""Convert legacy HTML blog bodies to Markdown using ``markdownify``."""

from __future__ import annotations

from markdownify import markdownify as _markdownify


def html_fragment_to_markdown(html: str) -> str:
    """Turn stored HTML into GitHub-flavored-ish Markdown.

    Tuned for insight articles: ATX headings, ``-`` bullets, strip bare wrappers.
    """
    raw = (html or "").strip()
    if not raw:
        return ""

    md = _markdownify(
        raw,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    # Collapse excessive blank lines from div soup
    lines = [ln.rstrip() for ln in md.splitlines()]
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 2:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip() + ("\n" if out else "")
