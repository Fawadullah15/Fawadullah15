"""
gen_headings.py — Premium section heading SVGs.

Design: UPPERCASE label + left accent glyph + gradient fade rule.
All headings share identical visual DNA — one design system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, FONTS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, fade_right_gradient, font_face
)

W, H = 820, 36

HEADINGS = [
    ("hd-about",    "about me"),
    ("hd-building", "currently building"),
    ("hd-tech",     "tech stack"),
    ("hd-projects", "selected work"),
    ("hd-stats",    "github analytics"),
    ("hd-activity", "contribution activity"),
    ("hd-connect",  "let's connect"),
]


def make_heading(text: str, b64: str | None = None) -> str:
    label = text.upper()

    if b64:
        ff = f'@font-face{{font-family:"JB";src:url("data:font/woff2;base64,{b64}") format("woff2");}}'
    else:
        ff = '@font-face{font-family:"JB";src:local("JetBrains Mono"),local("Courier New");}'

    # Letter-spacing 0.18em; estimate rendered width
    fs      = 10
    ls      = 0.18
    char_w  = 6.6 * (1 + ls)
    text_px = int(len(label) * char_w) + 20
    rule_x  = text_px + 16

    style = f"""
{ff}
@font-face{{font-family:"JB";src:local("JetBrains Mono"),local("Courier New");}}
*{{font-family:"JB","JetBrains Mono","Courier New",Courier,monospace;}}
@keyframes slideRight{{
  from{{opacity:0;transform:translateX(-6px);}}
  to{{opacity:1;transform:translateX(0);}}
}}
@keyframes grow{{
  from{{transform:scaleX(0);transform-origin:left;}}
  to{{transform:scaleX(1);transform-origin:left;}}
}}
.a-right{{animation:slideRight 0.7s cubic-bezier(0.16,1,0.3,1) forwards;opacity:0;}}
.a-grow{{animation:grow 0.9s cubic-bezier(0.16,1,0.3,1) 0.1s forwards;transform:scaleX(0);transform-origin:left;}}
""".strip()

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{style}</style>',
        f'<defs>',
        # Gradient fade for the rule line
        f'  <linearGradient id="ruleF" x1="0" y1="0" x2="1" y2="0">',
        f'    <stop offset="0%" stop-color="{COLORS["border2"]}" stop-opacity="1"/>',
        f'    <stop offset="75%" stop-color="{COLORS["border"]}" stop-opacity="0.4"/>',
        f'    <stop offset="100%" stop-color="{COLORS["bg"]}" stop-opacity="0"/>',
        f'  </linearGradient>',
        # Accent gradient for left bar
        f'  <linearGradient id="accV" x1="0" y1="0" x2="0" y2="1">',
        f'    <stop offset="0%" stop-color="{COLORS["accent"]}"/>',
        f'    <stop offset="100%" stop-color="{COLORS["accent_lo"]}"/>',
        f'  </linearGradient>',
        f'</defs>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',

        # Animated label group
        f'<g class="a-right">',
        # Left accent bar (premium vertical stripe)
        f'  <rect x="0" y="8" width="2" height="20" rx="1" fill="url(#accV)"/>',
        # Label text
        f'  <text x="12" y="{H//2 + 4}" font-size="{fs}" fill="{COLORS["accent_hi"]}" '
        f'  font-weight="600" letter-spacing="{ls}em">{_esc(label)}</text>',
        f'</g>',

        # Animated hairline rule
        f'<line x1="{rule_x}" y1="{H//2}" x2="{W-1}" y2="{H//2}" '
        f'stroke="url(#ruleF)" stroke-width="1" class="a-grow"/>',

        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def run() -> None:
    ASSETS.mkdir(exist_ok=True)
    b64_path = FONTS / "heading.b64"
    b64 = b64_path.read_text(encoding="ascii").strip() if b64_path.exists() else None

    for name, text in HEADINGS:
        svg = make_heading(text, b64=b64)
        out = ASSETS / f"{name}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"  wrote {out.name}")

    print(f"Done — {len(HEADINGS)} heading SVGs.")


if __name__ == "__main__":
    run()
