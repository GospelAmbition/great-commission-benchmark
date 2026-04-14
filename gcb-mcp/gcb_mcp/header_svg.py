"""
Programmatic SVG header generator for GCB blog posts.

Generates a self-contained 800×250 SVG with:
  - Solid dark background with a radial accent glow
  - Subtle dot-grid texture
  - GCB logomark (left column)
  - Provider logo or monogram (right column, left area)
  - Model name, version, score, tier pills (live SVG text — not burned-in)
  - Provider accent colour (auto-detected or caller-supplied)
  - Bottom gradient accent line

No external image fetch, no LLM, no browser/screenshot required.
SVG uploads directly via the blog upload-image endpoint.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Provider colour palette
# ---------------------------------------------------------------------------

PROVIDER_COLORS: dict[str, str] = {
    "openai":       "#10a37f",
    "anthropic":    "#d97757",
    "google":       "#4285f4",
    "meta-llama":   "#0082fb",
    "meta":         "#0082fb",
    "mistralai":    "#ff7000",
    "mistral":      "#ff7000",
    "microsoft":    "#00a4ef",
    "moonshot":     "#7c6af7",
    "moonshotai":   "#7c6af7",
    "x-ai":         "#1da1f2",
    "qwen":         "#6b7280",
    "deepseek":     "#1e6fff",
    "cohere":       "#39594a",
    "ai21":         "#ff5a5f",
    "perplexity":   "#20b2aa",
    "z-ai":         "#b45309",
    "essentialai":  "#7c3aed",
    "_default":     "#7E57C2",  # GCB purple
}


# ---------------------------------------------------------------------------
# Provider SVG logo paths  (viewBox 0 0 64 64, stroke="currentColor" fill="currentColor")
# Paths are simplified symbolic marks — not official brand assets.
# ---------------------------------------------------------------------------

# Each value is the inner SVG content (no <svg> wrapper) drawn at viewBox 0 0 64 64.
PROVIDER_LOGOS: dict[str, str] = {
    "openai": """
        <path fill="currentColor" d="
          M32 10 C20 10 11 19 11 30 C11 38 15.5 45 22 48.5 L22 54 L28 54 L28 44
          C29.3 44.4 30.6 44.6 32 44.6 C44 44.6 53 35.6 53 30 C53 22
          44 10 32 10 Z
          M32 14 C41.9 14 49 21.1 49 30 C49 35.7 42.9 40.6 32 40.6
          C21.1 40.6 15 35.7 15 30 C15 21.1 22.1 14 32 14 Z"
        opacity="0.9"/>
    """,
    "anthropic": """
        <text x="32" y="46" text-anchor="middle"
              font-family="Georgia,serif" font-size="40" font-weight="700"
              fill="currentColor" opacity="0.9">A</text>
    """,
    "google": """
        <path fill="currentColor" d="
          M52 32 C52 31 51.9 30 51.8 29 L32 29 L32 35.5 L43.1 35.5
          C42.6 38.2 41 40.4 38.6 41.9 L38.6 46 L45.5 46
          C49.5 42.3 52 37.6 52 32 Z" opacity="0.85"/>
        <path fill="currentColor" d="
          M32 52 C37.7 52 42.5 50.1 45.5 46 L38.6 41.9
          C36.7 43.2 34.5 44 32 44 C26.5 44 21.8 40.3 20.1 35.2 L13 35.2
          L13 39.4 C16.4 46.3 23.7 52 32 52 Z" opacity="0.85"/>
        <path fill="currentColor" d="
          M20.1 35.2 C19.6 33.8 19.4 32.4 19.4 31 C19.4 29.6 19.7 28.2 20.1 26.8
          L20.1 22.6 L13 22.6 C11.5 25.5 10.6 28.7 10.6 32
          C10.6 35.3 11.5 38.5 13 41.4 L20.1 35.2 Z" opacity="0.85"/>
        <path fill="currentColor" d="
          M32 18 C34.8 18 37.3 19 39.3 20.9 L45.7 14.5
          C42.5 11.5 37.6 9.6 32 9.6 C23.7 9.6 16.4 15.3 13 22.6
          L20.1 26.8 C21.8 21.7 26.5 18 32 18 Z" opacity="0.85"/>
    """,
    "meta-llama": """
        <path fill="currentColor" d="
          M14 44 Q14 20 26 20 Q32 20 32 32 Q32 20 38 20 Q50 20 50 44
          L46 44 Q46 26 38 26 Q35 26 34 32 L30 32 Q29 26 26 26 Q18 26 18 44 Z"
        opacity="0.9"/>
    """,
    "meta": """
        <path fill="currentColor" d="
          M14 44 Q14 20 26 20 Q32 20 32 32 Q32 20 38 20 Q50 20 50 44
          L46 44 Q46 26 38 26 Q35 26 34 32 L30 32 Q29 26 26 26 Q18 26 18 44 Z"
        opacity="0.9"/>
    """,
    "mistralai": """
        <rect x="12" y="12" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="28" y="12" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="44" y="12" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="12" y="28" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="28" y="28" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="12" y="44" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="28" y="44" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="44" y="44" width="12" height="12" rx="2" fill="currentColor" opacity="0.9"/>
    """,
    "microsoft": """
        <rect x="10" y="10" width="20" height="20" fill="#f25022" opacity="0.9"/>
        <rect x="34" y="10" width="20" height="20" fill="#7fba00" opacity="0.9"/>
        <rect x="10" y="34" width="20" height="20" fill="#00a4ef" opacity="0.9"/>
        <rect x="34" y="34" width="20" height="20" fill="#ffb900" opacity="0.9"/>
    """,
    "moonshot": """
        <path fill="currentColor" d="
          M38 14 A22 22 0 1 1 38 50 A16 16 0 1 0 38 14 Z" opacity="0.25"/>
        <path fill="none" stroke="currentColor" stroke-width="2.5" d="
          M38 14 A22 22 0 1 1 38 50 A16 16 0 1 0 38 14 Z" opacity="0.9"/>
        <circle cx="46" cy="20" r="3" fill="currentColor" opacity="0.7"/>
        <circle cx="50" cy="30" r="1.8" fill="currentColor" opacity="0.5"/>
    """,
    "moonshotai": """
        <path fill="currentColor" d="
          M38 14 A22 22 0 1 1 38 50 A16 16 0 1 0 38 14 Z" opacity="0.25"/>
        <path fill="none" stroke="currentColor" stroke-width="2.5" d="
          M38 14 A22 22 0 1 1 38 50 A16 16 0 1 0 38 14 Z" opacity="0.9"/>
        <circle cx="46" cy="20" r="3" fill="currentColor" opacity="0.7"/>
    """,
    "x-ai": """
        <text x="32" y="48" text-anchor="middle"
              font-family="Arial,sans-serif" font-size="46" font-weight="700"
              fill="currentColor" opacity="0.9">X</text>
    """,
    "deepseek": """
        <circle cx="32" cy="32" r="20" fill="none" stroke="currentColor"
                stroke-width="3" opacity="0.9"/>
        <path fill="currentColor" d="M22 32 Q32 18 42 32 Q32 46 22 32 Z" opacity="0.5"/>
        <circle cx="32" cy="32" r="5" fill="currentColor" opacity="0.9"/>
    """,
    "z-ai": """
        <text x="32" y="48" text-anchor="middle"
              font-family="Arial,sans-serif" font-size="44" font-weight="700"
              fill="currentColor" opacity="0.9">Z</text>
    """,
    "essentialai": """
        <text x="32" y="48" text-anchor="middle"
              font-family="Arial,sans-serif" font-size="36" font-weight="700"
              fill="currentColor" opacity="0.9">E</text>
    """,
    "qwen": """
        <text x="32" y="46" text-anchor="middle"
              font-family="Arial,sans-serif" font-size="30" font-weight="700"
              fill="currentColor" opacity="0.9">Qw</text>
    """,
}

# ---------------------------------------------------------------------------
# GCB cross/logomark (inline SVG paths, viewBox 0 0 200 200)
# ---------------------------------------------------------------------------

_GCB_LOGOMARK = """
<g fill="none" stroke="url(#gcbGrad)" stroke-width="5" stroke-linecap="round">
  <line x1="100" y1="40" x2="100" y2="160"/>
  <line x1="40"  y1="85" x2="160" y2="85"/>
  <circle cx="100" cy="100" r="52" stroke-width="4" opacity="0.5"/>
  <circle cx="100" cy="100" r="30" stroke-width="3" opacity="0.25"/>
</g>
"""


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def infer_provider(model_id: str) -> str:
    """Extract provider slug from an OpenRouter model_id (e.g. 'openai/gpt-4o' → 'openai')."""
    if "/" in model_id:
        return model_id.split("/")[0].lower()
    return model_id.lower()


def provider_color(provider: str, override: str | None = None) -> str:
    if override:
        return override
    return PROVIDER_COLORS.get(provider.lower(), PROVIDER_COLORS["_default"])


def _provider_logo_svg(provider: str, color: str, x: int, y: int, size: int = 64) -> str:
    """Return a positioned <g> containing the provider logo at (x, y) scaled to `size`."""
    inner = PROVIDER_LOGOS.get(provider.lower())
    if not inner:
        # Monogram fallback: first letter of provider in a circle
        letter = provider[0].upper() if provider else "?"
        inner = f"""
            <circle cx="32" cy="32" r="28" fill="none"
                    stroke="currentColor" stroke-width="3" opacity="0.6"/>
            <text x="32" y="42" text-anchor="middle"
                  font-family="DM Sans,Arial,sans-serif" font-size="32" font-weight="700"
                  fill="currentColor" opacity="0.9">{letter}</text>
        """

    scale = size / 64
    return (
        f'<g transform="translate({x},{y}) scale({scale:.4f})" '
        f'color="{color}" opacity="0.85">'
        f"{inner}</g>"
    )


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )


def _score_color(score: float | None) -> str:
    """Return a colour for a given score (traffic-light style)."""
    if score is None:
        return "#9ca3af"
    if score >= 60:
        return "#34d399"
    if score >= 40:
        return "#fbbf24"
    return "#f87171"


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------


def generate_header_svg(
    model_name: str,
    provider_name: str,
    score: float | None,
    model_version: str | None = None,
    accent_color: str | None = None,
    tier1_score: float | None = None,
    tier2_score: float | None = None,
    tier3_score: float | None = None,
) -> str:
    """
    Generate and return a complete SVG string for a blog article header.

    Parameters
    ----------
    model_name      Display name of the model (e.g. "GPT-5 Mini")
    provider_name   Provider slug or display name (e.g. "openai", "Moonshot AI")
    score           Overall GCB score (0–100), or None
    model_version   Short version string shown large (e.g. "5 Mini", "K2.5")
    accent_color    CSS hex colour override; inferred from provider if None
    tier1/2/3_score Optional tier scores for the pill row
    """
    provider_slug = infer_provider(provider_name if "/" not in provider_name else provider_name)
    color = provider_color(provider_slug, accent_color)

    # Derive a short version label: last segment of model name or explicit
    if model_version is None:
        # Try to extract version-like suffix: "GPT-4o Mini" → "4o Mini"
        parts = model_name.split()
        if len(parts) > 1:
            model_version = " ".join(parts[1:])  # drop first word (usually brand)
        else:
            model_version = model_name
    # Truncate if very long
    if len(model_version) > 12:
        model_version = model_version[:12]

    score_str = f"{score:.1f}" if score is not None else "—"
    provider_display = provider_name.replace("-", " ").title()
    model_name_safe = _xml_escape(model_name)
    provider_safe = _xml_escape(provider_display)
    version_safe = _xml_escape(model_version)

    # Derive a unique gradient ID to avoid collisions if multiple SVGs are embedded
    safe_id = re.sub(r"[^a-zA-Z0-9]", "_", model_name)[:20]

    # Provider logo positioned at (290, 93) — small icon above model label
    logo_g = _provider_logo_svg(provider_slug, color, x=290, y=88, size=50)

    # Tier pill row — only shown if at least one tier score is provided
    tier_pills = ""
    if any(s is not None for s in [tier1_score, tier2_score, tier3_score]):
        px = 348
        for label, ts in [("T1", tier1_score), ("T2", tier2_score), ("T3", tier3_score)]:
            ts_str = f"{ts:.0f}%" if ts is not None else "—"
            tc = _score_color(ts)
            tier_pills += (
                f'<rect x="{px}" y="163" width="62" height="22" rx="4" '
                f'fill="{tc}" fill-opacity="0.12" '
                f'stroke="{tc}" stroke-opacity="0.3" stroke-width="1"/>'
                f'<text x="{px + 7}" y="178" '
                f'font-family="DM Sans,Arial,sans-serif" font-size="10" '
                f'font-weight="500" letter-spacing="0.05em" fill="{tc}" opacity="0.9">'
                f'{label} {ts_str}</text>'
            )
            px += 70

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 800 250" width="800" height="250">
  <defs>
    <!-- Background gradient -->
    <linearGradient id="bgGrad_{safe_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0a0814"/>
      <stop offset="100%" stop-color="#0e0a18"/>
    </linearGradient>

    <!-- Accent radial glow -->
    <radialGradient id="accentGlow_{safe_id}" cx="60%" cy="45%" r="55%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>

    <!-- GCB logo gradient -->
    <linearGradient id="gcbGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.6"/>
    </linearGradient>

    <!-- Bottom line gradient -->
    <linearGradient id="bottomLine_{safe_id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="60%" stop-color="{color}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="800" height="250" fill="url(#bgGrad_{safe_id})"/>
  <rect width="800" height="250" fill="url(#accentGlow_{safe_id})"/>

  <!-- Subtle dot grid -->
  <pattern id="dots_{safe_id}" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
    <circle cx="0" cy="0" r="0.8" fill="white" opacity="0.06"/>
  </pattern>
  <rect width="800" height="250" fill="url(#dots_{safe_id})"/>

  <!-- ── LEFT COLUMN: GCB logomark ── -->
  <svg x="20" y="35" width="180" height="180" viewBox="0 0 200 200">
    {_GCB_LOGOMARK}
  </svg>
  <text x="108" y="232"
        font-family="DM Sans,Arial,sans-serif" font-size="11"
        font-weight="400" letter-spacing="0.14em" text-anchor="middle"
        text-decoration="none"
        fill="{color}" opacity="0.45">greatcommissionbenchmark</text>

  <!-- Vertical divider -->
  <line x1="220" y1="55" x2="220" y2="195"
        stroke="{color}" stroke-opacity="0.2" stroke-width="1"/>

  <!-- ── RIGHT COLUMN ── -->

  <!-- Provider logo icon (50×50) -->
  {logo_g}

  <!-- Provider name label -->
  <text x="350" y="108"
        font-family="DM Sans,Arial,sans-serif" font-size="11"
        font-weight="500" letter-spacing="0.18em" text-transform="uppercase"
        fill="{color}" opacity="0.6">{provider_safe.upper()}</text>

  <!-- Model name (large) -->
  <text x="348" y="148"
        font-family="DM Sans,Arial,sans-serif" font-size="32"
        font-weight="700" letter-spacing="-0.01em"
        fill="#e8e0f8">{model_name_safe}</text>

  <!-- Tier pills row -->
  {tier_pills}

  <!-- ── FAR RIGHT: score block ── -->
  <rect x="640" y="68" width="130" height="114" rx="6"
        fill="{color}" fill-opacity="0.06"
        stroke="{color}" stroke-opacity="0.18" stroke-width="1"/>

  <text x="705" y="118"
        font-family="DM Sans,Arial,sans-serif" font-size="52"
        font-weight="700" letter-spacing="-0.03em" text-anchor="middle"
        fill="{_score_color(score)}">{score_str}</text>

  <text x="705" y="138"
        font-family="DM Sans,Arial,sans-serif" font-size="11"
        font-weight="400" letter-spacing="0.06em" text-anchor="middle"
        fill="{color}" opacity="0.45">/ 100</text>

  <text x="705" y="162"
        font-family="DM Sans,Arial,sans-serif" font-size="9"
        font-weight="500" letter-spacing="0.2em" text-anchor="middle"
        fill="{color}" opacity="0.35">GCB SCORE</text>

  <!-- Subtitle bar -->
  <text x="348" y="222"
        font-family="DM Sans,Arial,sans-serif" font-size="10"
        font-weight="400" letter-spacing="0.12em"
        fill="white" opacity="0.22">GREAT COMMISSION BENCHMARK REVIEW</text>

  <!-- Bottom accent line -->
  <rect x="0" y="246" width="800" height="4"
        fill="url(#bottomLine_{safe_id})"/>

  <!-- Editorial tag (top right) -->
  <text x="788" y="18"
        font-family="DM Sans,Arial,sans-serif" font-size="8"
        font-weight="500" letter-spacing="0.2em" text-anchor="end"
        fill="white" opacity="0.18">EDITORIAL REVIEW</text>
</svg>"""
    return svg


# ---------------------------------------------------------------------------
# File I/O and upload
# ---------------------------------------------------------------------------


def save_svg(svg_content: str, output_path: Path) -> Path:
    """Write SVG string to a file and return the path."""
    output_path.write_text(svg_content, encoding="utf-8")
    return output_path


async def generate_and_upload(
    model_name: str,
    provider_name: str,
    score: float | None,
    model_version: str | None = None,
    accent_color: str | None = None,
    tier1_score: float | None = None,
    tier2_score: float | None = None,
    tier3_score: float | None = None,
) -> dict[str, Any]:
    """
    Generate an SVG header, save to a temp file, upload via the blog API,
    and return the hosted URL plus local path.
    """
    from gcb_mcp.blog import upload_image  # noqa: PLC0415

    svg_content = generate_header_svg(
        model_name=model_name,
        provider_name=provider_name,
        score=score,
        model_version=model_version,
        accent_color=accent_color,
        tier1_score=tier1_score,
        tier2_score=tier2_score,
        tier3_score=tier3_score,
    )

    # Write to a deterministic temp path based on model name
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", model_name.lower())[:60]
    svg_path = Path(tempfile.gettempdir()) / f"gcb-header-{safe_name}.svg"
    save_svg(svg_content, svg_path)

    upload_result = await upload_image(svg_path, content_type="image/svg+xml")
    if "error" in upload_result:
        return {
            "error": upload_result.get("error"),
            "message": upload_result.get("message") or upload_result.get("detail"),
            "svg_path": str(svg_path),
            "svg_content": svg_content,
        }

    return {
        "url": upload_result.get("url"),
        "svg_path": str(svg_path),
        "filename": upload_result.get("filename"),
        "provider_color": provider_color(infer_provider(provider_name), accent_color),
    }
