"""Newsletter hero SVG (static markup checks)."""

from gcb_mcp.header_svg import NEWSLETTER_TAGLINE, generate_newsletter_header_svg


def test_generate_newsletter_header_svg_anchors_and_hero_tokens():
    svg = generate_newsletter_header_svg("April, 2026")
    assert "Great Commission" in svg
    assert "Benchmark" in svg
    assert NEWSLETTER_TAGLINE in svg
    assert "April, 2026" in svg
    assert "#09090b" in svg
    assert "#2a0a0a" in svg
    assert "NEWSLETTER" in svg
    assert "220, 38, 38" in svg or "rgba(220, 38, 38" in svg
