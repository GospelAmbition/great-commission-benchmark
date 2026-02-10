#!/usr/bin/env python3
"""Generate header graphics (HTML + PNG) for all model review articles."""

import os
import sys

# ── Model definitions ──────────────────────────────────────────────
MODELS = [
    {
        "slug": "essentialai-rnj-1-instruct",
        "title": "RNJ-1 Instruct — Great Commission Benchmark Review",
        "company": "essential ai",
        "version": "RNJ-1",
        "model_label": "Instruct",
        "score": "66.7",
        "primary": "#00ACC1",
        "bg": "#090f14",
        "glow_rgb": "0,172,193",
        "text_light": "#d0e8ec",
        "version_font": "'JetBrains Mono', monospace",
        "version_size": "68px",
        "font_import": "JetBrains+Mono:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="4" stroke-linecap="round">
        <!-- Abstract neural/circuit pattern for Essential AI -->
        <circle cx="100" cy="100" r="65" opacity="0.4"/>
        <circle cx="100" cy="100" r="40" opacity="0.6"/>
        <circle cx="100" cy="100" r="12" fill="url(#grad)" stroke="none" opacity="0.8"/>
        <line x1="100" y1="35" x2="100" y2="60"/>
        <line x1="100" y1="140" x2="100" y2="165"/>
        <line x1="35" y1="100" x2="60" y2="100"/>
        <line x1="140" y1="100" x2="165" y2="100"/>
        <line x1="54" y1="54" x2="72" y2="72"/>
        <line x1="128" y1="128" x2="146" y2="146"/>
        <line x1="146" y1="54" x2="128" y2="72"/>
        <line x1="54" y1="146" x2="72" y2="128"/>
        <circle cx="100" cy="35" r="4" fill="url(#grad)" stroke="none"/>
        <circle cx="100" cy="165" r="4" fill="url(#grad)" stroke="none"/>
        <circle cx="35" cy="100" r="4" fill="url(#grad)" stroke="none"/>
        <circle cx="165" cy="100" r="4" fill="url(#grad)" stroke="none"/>
      </g>""",
    },
    {
        "slug": "microsoft-phi-4",
        "title": "Phi-4 — Great Commission Benchmark Review",
        "company": "microsoft",
        "version": "Phi-4",
        "model_label": "Small Language Model",
        "score": "49.0",
        "primary": "#0078D4",
        "bg": "#090d16",
        "glow_rgb": "0,120,212",
        "text_light": "#d0d8ec",
        "version_font": "'Outfit', sans-serif",
        "version_size": "82px",
        "font_import": "Outfit:wght@400;700",
        "logo_svg": """
      <g transform="translate(64,64)">
        <!-- Microsoft four-square logo -->
        <rect x="0" y="0" width="33" height="33" fill="#F25022" rx="2" opacity="0.7"/>
        <rect x="38" y="0" width="33" height="33" fill="#7FBA00" rx="2" opacity="0.7"/>
        <rect x="0" y="38" width="33" height="33" fill="#00A4EF" rx="2" opacity="0.7"/>
        <rect x="38" y="38" width="33" height="33" fill="#FFB900" rx="2" opacity="0.7"/>
      </g>""",
    },
    {
        "slug": "moonshotai-kimi-k2-thinking",
        "title": "Kimi K2 Thinking — Great Commission Benchmark Review",
        "company": "moonshot ai",
        "version": "K2",
        "model_label": "Kimi · Thinking",
        "score": "41.3",
        "primary": "#5C6BC0",
        "bg": "#0c0a16",
        "glow_rgb": "92,107,192",
        "text_light": "#d8d4ec",
        "version_font": "'Space Grotesk', sans-serif",
        "version_size": "96px",
        "font_import": "Space+Grotesk:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="5" stroke-linecap="round">
        <!-- Crescent moon for Moonshot AI -->
        <path d="M 130,60 A 55,55 0 1,1 130,140 A 38,38 0 1,0 130,60" fill="url(#grad)" stroke="none" opacity="0.3"/>
        <path d="M 130,60 A 55,55 0 1,1 130,140 A 38,38 0 1,0 130,60" fill="none"/>
        <!-- Small star accent -->
        <circle cx="148" cy="72" r="3" fill="url(#grad)" stroke="none" opacity="0.6"/>
        <circle cx="156" cy="90" r="2" fill="url(#grad)" stroke="none" opacity="0.4"/>
      </g>""",
    },
    {
        "slug": "moonshotai-kimi-k2.5",
        "title": "Kimi K2.5 — Great Commission Benchmark Review",
        "company": "moonshot ai",
        "version": "K2.5",
        "model_label": "Kimi",
        "score": "56.0",
        "primary": "#7E57C2",
        "bg": "#0e0a18",
        "glow_rgb": "126,87,194",
        "text_light": "#dcd4f0",
        "version_font": "'Space Grotesk', sans-serif",
        "version_size": "86px",
        "font_import": "Space+Grotesk:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="5" stroke-linecap="round">
        <!-- Crescent moon for Moonshot AI — slightly different -->
        <path d="M 128,58 A 55,55 0 1,1 128,142 A 40,40 0 1,0 128,58" fill="url(#grad)" stroke="none" opacity="0.25"/>
        <path d="M 128,58 A 55,55 0 1,1 128,142 A 40,40 0 1,0 128,58" fill="none"/>
        <circle cx="150" cy="68" r="3.5" fill="url(#grad)" stroke="none" opacity="0.5"/>
        <circle cx="160" cy="88" r="2" fill="url(#grad)" stroke="none" opacity="0.35"/>
        <circle cx="152" cy="52" r="1.5" fill="url(#grad)" stroke="none" opacity="0.25"/>
      </g>""",
    },
    {
        "slug": "openai-gpt-4o-mini",
        "title": "GPT-4o Mini — Great Commission Benchmark Review",
        "company": "openai",
        "version": "4o",
        "model_label": "GPT Mini",
        "score": "84.7",
        "primary": "#10a37f",
        "bg": "#0d0d0d",
        "glow_rgb": "16,163,127",
        "text_light": "#e0e0e0",
        "version_font": "'Space Mono', monospace",
        "version_size": "96px",
        "font_import": "Space+Mono:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="100,18 172,56 172,132 100,170 28,132 28,56"/>
        <line x1="100" y1="18" x2="100" y2="76"/>
        <line x1="172" y1="56" x2="120" y2="86"/>
        <line x1="172" y1="132" x2="120" y2="102"/>
        <line x1="100" y1="170" x2="100" y2="112"/>
        <line x1="28" y1="132" x2="80" y2="102"/>
        <line x1="28" y1="56" x2="80" y2="86"/>
        <polygon points="100,76 120,86 120,102 100,112 80,102 80,86"/>
      </g>""",
    },
    {
        "slug": "openai-gpt-5-mini",
        "title": "GPT-5 Mini — Great Commission Benchmark Review",
        "company": "openai",
        "version": "5",
        "model_label": "GPT Mini",
        "score": "70.7",
        "primary": "#10a37f",
        "bg": "#0d0d0d",
        "glow_rgb": "16,163,127",
        "text_light": "#e0e0e0",
        "version_font": "'Space Mono', monospace",
        "version_size": "108px",
        "font_import": "Space+Mono:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="100,18 172,56 172,132 100,170 28,132 28,56"/>
        <line x1="100" y1="18" x2="100" y2="76"/>
        <line x1="172" y1="56" x2="120" y2="86"/>
        <line x1="172" y1="132" x2="120" y2="102"/>
        <line x1="100" y1="170" x2="100" y2="112"/>
        <line x1="28" y1="132" x2="80" y2="102"/>
        <line x1="28" y1="56" x2="80" y2="86"/>
        <polygon points="100,76 120,86 120,102 100,112 80,102 80,86"/>
      </g>""",
    },
    {
        "slug": "openai-gpt-5.2-codex",
        "title": "GPT-5.2 Codex — Great Commission Benchmark Review",
        "company": "openai",
        "version": "5.2",
        "model_label": "GPT Codex",
        "score": "46.0",
        "primary": "#10a37f",
        "bg": "#0d0d0d",
        "glow_rgb": "16,163,127",
        "text_light": "#e0e0e0",
        "version_font": "'Space Mono', monospace",
        "version_size": "96px",
        "font_import": "Space+Mono:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="100,18 172,56 172,132 100,170 28,132 28,56"/>
        <line x1="100" y1="18" x2="100" y2="76"/>
        <line x1="172" y1="56" x2="120" y2="86"/>
        <line x1="172" y1="132" x2="120" y2="102"/>
        <line x1="100" y1="170" x2="100" y2="112"/>
        <line x1="28" y1="132" x2="80" y2="102"/>
        <line x1="28" y1="56" x2="80" y2="86"/>
        <polygon points="100,76 120,86 120,102 100,112 80,102 80,86"/>
      </g>""",
    },
    {
        "slug": "openai-gpt-oss-120b",
        "title": "GPT OSS 120B — Great Commission Benchmark Review",
        "company": "openai",
        "version": "120B",
        "model_label": "GPT · Open Source",
        "score": "32.0",
        "primary": "#10a37f",
        "bg": "#0d0d0d",
        "glow_rgb": "16,163,127",
        "text_light": "#e0e0e0",
        "version_font": "'Space Mono', monospace",
        "version_size": "82px",
        "font_import": "Space+Mono:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="100,18 172,56 172,132 100,170 28,132 28,56"/>
        <line x1="100" y1="18" x2="100" y2="76"/>
        <line x1="172" y1="56" x2="120" y2="86"/>
        <line x1="172" y1="132" x2="120" y2="102"/>
        <line x1="100" y1="170" x2="100" y2="112"/>
        <line x1="28" y1="132" x2="80" y2="102"/>
        <line x1="28" y1="56" x2="80" y2="86"/>
        <polygon points="100,76 120,86 120,102 100,112 80,102 80,86"/>
      </g>""",
    },
    {
        "slug": "qwen-qwen3-coder-next",
        "title": "Qwen3 Coder Next — Great Commission Benchmark Review",
        "company": "alibaba · qwen",
        "version": "Q3",
        "model_label": "Qwen · Coder Next",
        "score": "38.7",
        "primary": "#615EFF",
        "bg": "#0a0a16",
        "glow_rgb": "97,94,255",
        "text_light": "#d8d8f0",
        "version_font": "'Outfit', sans-serif",
        "version_size": "96px",
        "font_import": "Outfit:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="5" stroke-linecap="round">
        <!-- Stylized Q for Qwen -->
        <circle cx="96" cy="95" r="52" opacity="0.6"/>
        <line x1="130" y1="128" x2="158" y2="160" stroke-width="7" opacity="0.7"/>
        <!-- Inner accent -->
        <circle cx="96" cy="95" r="22" opacity="0.3" fill="url(#grad)" stroke="none"/>
      </g>""",
    },
    {
        "slug": "x-ai-grok-4.1-fast",
        "title": "Grok 4.1 Fast — Great Commission Benchmark Review",
        "company": "xAI",
        "version": "4.1",
        "model_label": "Grok · Fast",
        "score": "90.3",
        "primary": "#E8E8E8",
        "bg": "#050505",
        "glow_rgb": "200,200,200",
        "text_light": "#e8e8e8",
        "version_font": "'Inter', sans-serif",
        "version_size": "96px",
        "font_import": "Inter:wght@400;700;900",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="8" stroke-linecap="round">
        <!-- Bold geometric X for xAI -->
        <line x1="58" y1="58" x2="142" y2="142"/>
        <line x1="142" y1="58" x2="58" y2="142"/>
        <!-- Subtle arc accent -->
        <path d="M 70,40 A 75,75 0 0,1 160,130" stroke-width="2" opacity="0.2"/>
      </g>""",
    },
    {
        "slug": "z-ai-glm-4.7",
        "title": "GLM-4.7 — Great Commission Benchmark Review",
        "company": "zhipu ai",
        "version": "4.7",
        "model_label": "GLM",
        "score": "83.7",
        "primary": "#2196F3",
        "bg": "#080c14",
        "glow_rgb": "33,150,243",
        "text_light": "#d4e4f0",
        "version_font": "'Crimson Pro', serif",
        "version_size": "100px",
        "font_import": "Crimson+Pro:wght@400;700",
        "logo_svg": """
      <g fill="none" stroke="url(#grad)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
        <!-- Diamond/gem facets for Zhipu AI -->
        <polygon points="100,30 155,100 100,170 45,100" opacity="0.5"/>
        <polygon points="100,30 130,75 100,100 70,75" fill="url(#grad)" stroke="none" opacity="0.15"/>
        <line x1="100" y1="30" x2="100" y2="170" opacity="0.3"/>
        <line x1="45" y1="100" x2="155" y2="100" opacity="0.3"/>
        <line x1="70" y1="75" x2="130" y2="75" opacity="0.2"/>
        <line x1="70" y1="125" x2="130" y2="125" opacity="0.2"/>
        <!-- Top facet highlight -->
        <polygon points="100,30 130,75 100,100 70,75" fill="url(#grad)" stroke="none" opacity="0.08"/>
      </g>""",
    },
]

# ── HTML template ──────────────────────────────────────────────────
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family={font_import}&display=swap');

  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #111;
    font-family: 'DM Sans', sans-serif;
  }}

  .header {{
    width: 800px;
    height: 250px;
    background: {bg};
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
  }}

  .header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
    z-index: 0;
  }}

  .header::after {{
    content: '';
    position: absolute;
    left: 30px;
    top: 50%;
    transform: translateY(-50%);
    width: 260px;
    height: 260px;
    background: radial-gradient(circle, rgba({glow_rgb},0.1) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
  }}

  .logo-zone {{
    position: relative;
    width: 220px;
    height: 250px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
  }}

  .logo-mark {{
    width: 140px;
    height: 140px;
    opacity: 0.15;
  }}

  .logo-wordmark {{
    position: absolute;
    bottom: 28px;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'DM Sans', sans-serif;
    font-weight: 400;
    font-size: 13px;
    letter-spacing: 0.14em;
    text-transform: lowercase;
    color: {primary};
    opacity: 0.6;
    white-space: nowrap;
  }}

  .divider {{
    width: 1px;
    height: 140px;
    background: linear-gradient(to bottom, transparent, rgba({glow_rgb},0.25), transparent);
    flex-shrink: 0;
    z-index: 2;
  }}

  .content {{
    flex: 1;
    padding: 0 36px;
    display: flex;
    align-items: center;
    gap: 28px;
    z-index: 2;
  }}

  .version-block {{
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }}

  .version-number {{
    font-family: {version_font};
    font-size: {version_size};
    font-weight: 700;
    line-height: 0.85;
    color: {primary};
    letter-spacing: -0.04em;
    position: relative;
  }}

  .version-number::after {{
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba({glow_rgb},0.3), transparent);
  }}

  .model-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba({glow_rgb},0.5);
    margin-top: 10px;
    white-space: nowrap;
  }}

  .text-block {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  .benchmark-title {{
    font-family: 'DM Sans', sans-serif;
    font-size: 15.5px;
    font-weight: 500;
    color: {text_light};
    letter-spacing: 0.01em;
    line-height: 1.35;
  }}

  .benchmark-title span {{
    color: rgba({glow_rgb},0.85);
  }}

  .subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
  }}

  .score-badge {{
    display: inline-flex;
    align-items: baseline;
    gap: 4px;
    margin-top: 4px;
    padding: 5px 14px;
    background: rgba({glow_rgb},0.08);
    border: 1px solid rgba({glow_rgb},0.18);
    border-radius: 4px;
    align-self: flex-start;
  }}

  .score-value {{
    font-family: {version_font};
    font-size: 20px;
    font-weight: 700;
    color: {primary};
    line-height: 1;
  }}

  .score-total {{
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: rgba({glow_rgb},0.45);
    font-weight: 400;
  }}

  .score-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba({glow_rgb},0.35);
    margin-left: 8px;
  }}

  .bottom-line {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(to right, {primary}, rgba({glow_rgb},0.15) 60%, transparent);
    z-index: 3;
  }}

  .editorial-tag {{
    position: absolute;
    top: 16px;
    right: 20px;
    font-family: 'DM Sans', sans-serif;
    font-size: 8.5px;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.18);
    z-index: 3;
  }}
</style>
</head>
<body>

<div class="header">

  <div class="logo-zone">
    <svg class="logo-mark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{primary}"/>
          <stop offset="100%" stop-color="{primary_dark}"/>
        </linearGradient>
      </defs>
      {logo_svg}
    </svg>
    <span class="logo-wordmark">{company}</span>
  </div>

  <div class="divider"></div>

  <div class="content">
    <div class="version-block">
      <div class="version-number">{version}</div>
      <div class="model-label">{model_label}</div>
    </div>

    <div class="text-block">
      <div class="benchmark-title"><span>Great Commission</span> Benchmark Review</div>
      <div class="subtitle">Strategic AI Assessment for Ministry Leaders</div>
      <div class="score-badge">
        <span class="score-value">{score}</span>
        <span class="score-total">/ 100</span>
        <span class="score-label">overall score</span>
      </div>
    </div>
  </div>

  <div class="bottom-line"></div>
  <div class="editorial-tag">Editorial Review</div>

</div>

</body>
</html>"""


def darken_hex(hex_color: str, factor: float = 0.75) -> str:
    """Darken a hex color by a factor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_html_files(base_dir: str):
    """Generate all HTML header files."""
    generated = []
    for model in MODELS:
        html_path = os.path.join(base_dir, f"article-{model['slug']}-header.html")
        primary_dark = darken_hex(model["primary"])

        html = TEMPLATE.format(
            title=model["title"],
            font_import=model["font_import"],
            bg=model["bg"],
            glow_rgb=model["glow_rgb"],
            primary=model["primary"],
            primary_dark=primary_dark,
            text_light=model["text_light"],
            version_font=model["version_font"],
            version_size=model["version_size"],
            logo_svg=model["logo_svg"],
            company=model["company"],
            version=model["version"],
            model_label=model["model_label"],
            score=model["score"],
        )

        with open(html_path, "w") as f:
            f.write(html)
        generated.append(html_path)
        print(f"  HTML: {os.path.basename(html_path)}")

    return generated


def render_pngs(html_files: list, base_dir: str):
    """Render all HTML files to PNG using Playwright + system Chrome."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright")
        sys.exit(1)

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_path):
        print(f"ERROR: Chrome not found at {chrome_path}")
        sys.exit(1)

    print("\nRendering PNGs with Playwright + Chrome...")
    p = sync_playwright().start()
    browser = p.chromium.launch(executable_path=chrome_path)
    page = browser.new_page(viewport={"width": 800, "height": 600})

    rendered = []
    for html_path in html_files:
        png_path = html_path.replace(".html", ".png")
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        # Wait for fonts to load
        page.wait_for_timeout(1500)
        header = page.locator(".header")
        header.screenshot(path=png_path)
        size_kb = os.path.getsize(png_path) / 1024
        rendered.append(png_path)
        print(f"  PNG: {os.path.basename(png_path)} ({size_kb:.0f}KB)")

    browser.close()
    p.stop()
    return rendered


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating 11 header HTML files...")
    html_files = generate_html_files(base_dir)
    print(f"\nGenerated {len(html_files)} HTML files.")

    print("\nRendering to PNG...")
    png_files = render_pngs(html_files, base_dir)
    print(f"\nDone! Generated {len(png_files)} PNG files.")


if __name__ == "__main__":
    main()
