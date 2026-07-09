"""Tests for markdown → email HTML conversion."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "markdown_email_under_test",
    Path(__file__).resolve().parents[1] / "app" / "services" / "markdown_email.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

markdown_to_email_html_fragment = _mod.markdown_to_email_html_fragment
wrap_email_shell = _mod.wrap_email_shell
SPONSOR_ATTRIBUTION = _mod.SPONSOR_ATTRIBUTION


def test_markdown_to_email_basic():
    html = markdown_to_email_html_fragment("# Hi\n\n[link](https://example.com)")
    assert "gcb-newsletter-body" in html
    assert "https://example.com" in html
    assert "<script" not in html.lower()


def test_wrap_email_shell_contains_web_link():
    inner = "<p>Hello</p>"
    full = wrap_email_shell(
        inner,
        title='Test "News"',
        web_version_url="https://greatcommissionbenchmark.ai/insights/foo",
    )
    assert "View in browser" in full
    assert "insights/foo" in full
    assert SPONSOR_ATTRIBUTION in full


def test_wrap_email_shell_places_optional_footer_above_sponsor_attribution():
    full = wrap_email_shell(
        "<p>Hello</p>",
        title="Test News",
        web_version_url=None,
        footer_html="<p>Unsubscribe instructions</p>",
    )
    assert "Unsubscribe instructions" in full
    assert full.index("Unsubscribe instructions") < full.index(SPONSOR_ATTRIBUTION)


def test_markdown_to_email_preserves_safe_gcb_image():
    html = markdown_to_email_html_fragment(
        "![Chart](https://greatcommissionbenchmark.ai/api/files/highlight.svg)"
    )
    assert "<img" in html
    assert "highlight.svg" in html
    assert "max-width:100%" in html


def test_markdown_to_email_strips_unsafe_image_hosts():
    html = markdown_to_email_html_fragment("![Bad](https://evil.example/highlight.svg)")
    assert "<img" not in html
    assert "evil.example" not in html
