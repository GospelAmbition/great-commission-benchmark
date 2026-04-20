"""Convert markdown blog content to a conservative HTML fragment for email."""

from __future__ import annotations

import re
from html import escape

import bleach
import markdown


_ALLOWED_TAGS = frozenset(
    {
        "p",
        "br",
        "strong",
        "em",
        "b",
        "i",
        "u",
        "a",
        "ul",
        "ol",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "blockquote",
        "code",
        "pre",
        "hr",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    }
)

_ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title", "rel"],
    "th": ["align"],
    "td": ["align"],
}


def markdown_to_email_html_fragment(markdown_source: str) -> str:
    """Render markdown to HTML and sanitize for email embedding."""
    raw = markdown.markdown(
        markdown_source or "",
        extensions=["extra", "nl2br", "sane_lists"],
        output_format="html",
    )
    cleaned = bleach.clean(
        raw,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
    )
    # Harden external links
    cleaned = re.sub(r"<a ", '<a rel="noopener noreferrer" ', cleaned)
    return f'<div class="gcb-newsletter-body" style="font-family:Georgia,serif;line-height:1.5;color:#111;">{cleaned}</div>'


def wrap_email_shell(inner_html: str, *, title: str, web_version_url: str | None) -> str:
    """Minimal table-based wrapper for client compatibility."""
    title_esc = escape(title)
    link_block = ""
    if web_version_url:
        link_block = (
            f'<p style="font-size:13px;color:#555;">'
            f'Having trouble reading this email? '
            f'<a href="{escape(web_version_url)}" rel="noopener noreferrer">View in browser</a>.'
            f"</p>"
        )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><title>{title_esc}</title></head>
<body style="margin:0;padding:0;background:#f4f4f5;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f4f5;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width:600px;background:#ffffff;border-radius:8px;padding:24px;">
<tr><td>
{link_block}
{inner_html}
</td></tr></table></td></tr></table></body></html>"""
