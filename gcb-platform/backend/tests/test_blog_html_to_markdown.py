"""Tests for HTML → Markdown conversion (markdownify)."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "blog_html_to_markdown_under_test",
    Path(__file__).resolve().parents[1] / "app" / "services" / "blog_html_to_markdown.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

html_fragment_to_markdown = _mod.html_fragment_to_markdown


def test_simple_paragraphs():
    out = html_fragment_to_markdown("<p>Hello</p><p>World</p>")
    assert "Hello" in out
    assert "World" in out
