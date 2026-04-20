"""Tests for legacy HTML detection on blog fields."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "blog_html_detection_under_test",
    Path(__file__).resolve().parents[1] / "app" / "services" / "blog_html_detection.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

content_confidence = _mod.content_confidence
looks_like_legacy_html = _mod.looks_like_legacy_html
markdownish_score = _mod.markdownish_score


def test_pure_markdown_low_html_signal():
    md = "# Title\n\nSome **bold** and a [link](https://x.com).\n\n- one\n- two\n"
    assert content_confidence(md) in ("none", "low")
    assert markdownish_score(md) > 0.3


def test_paragraph_html_high():
    html = "<p>Hello world</p><p>Second</p>"
    assert content_confidence(html) == "high"


def test_looks_like_legacy_threshold():
    assert looks_like_legacy_html("<div>x</div><p>y</p>", "high") is True
    assert looks_like_legacy_html("<br><br><br>", "high") is False
    assert looks_like_legacy_html("<br><br><br>", "medium") is True
