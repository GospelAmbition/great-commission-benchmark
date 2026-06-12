"""Convert markdown blog content to a conservative HTML fragment for email."""

from __future__ import annotations

import re
from html import escape
from urllib.parse import urlparse

import bleach
import markdown

from app.core.config import settings


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
        "img",
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
    "img": ["src", "alt", "width", "height"],
    "th": ["align"],
    "td": ["align"],
}


def _allowed_image_hosts() -> set[str]:
    hosts = {
        "greatcommissionbenchmark.ai",
        "www.greatcommissionbenchmark.ai",
        "api.greatcommissionbenchmark.ai",
    }
    configured = (settings.BACKEND_PUBLIC_URL or "").strip()
    if configured:
        parsed = urlparse(configured)
        if parsed.hostname:
            hosts.add(parsed.hostname.lower())
    return hosts


def _clean_attributes(tag: str, name: str, value: str) -> bool:
    if tag != "img":
        return name in _ALLOWED_ATTRIBUTES.get(tag, [])

    if name not in _ALLOWED_ATTRIBUTES["img"]:
        return False
    if name != "src":
        return True

    parsed = urlparse(value or "")
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    return host in _allowed_image_hosts() or host.endswith(".greatcommissionbenchmark.ai")


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
        attributes=_clean_attributes,
        strip=True,
    )
    # Harden external links
    cleaned = re.sub(r"<a ", '<a rel="noopener noreferrer" ', cleaned)
    cleaned = re.sub(r"<img(?![^>]*\ssrc=)[^>]*>", "", cleaned)
    cleaned = re.sub(
        r"<img ",
        '<img style="display:block;max-width:100%;height:auto;border:0;margin:16px 0;" ',
        cleaned,
    )
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
