"""
gen_headings.py — Generate section heading SVGs.

Each heading is: lowercase monospace label + hairline rule to right edge.
Fonts embedded if fonts/heading.b64 exists.
No external dependencies.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import ASSETS, FONTS, COLORS, _esc, font_face

W = 800
H = 30

HEADINGS = [
    ("hd-about",    "about"),
    ("hd-tech",     "tech stack"),
    ("hd-focus",    "current focus"),
    ("hd-projects", "projects"),
    ("hd-stats",    "github statistics"),
    ("hd-activity", "contribution activity"),
    ("hd-connect",  "connect"),
]


def make_heading_svg(text: str) -> str:
    """Generate a heading SVG: label + hairline rule."""
    ff = font_face("heading")

    # Estimate text width: ~7.5px per char at font-size 12
    char_w = 7.5
    text_w  = len(text) * char_w
    rule_x  = int(text_w) + 16

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
        f'<style>\n'
        f'@font-face{{\n'
        f'  font-family:"JB";\n'
        f'  src:url("data:font/woff2;base64,FONT_PLACEHOLDER") format("woff2");\n'
        f'}}\n'
        f'</style>\n'
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>\n'
        # accent dot
        f'<rect x="0" y="10" width="3" height="12" fill="{COLORS["accent"]}" rx="1"/>\n'
        # label
        f'<text x="10" y="21" '
        f'font-family="\\"JB\\",\\"JetBrains Mono\\",\\"Courier New\\",Courier,monospace" '
        f'font-size="12" fill="{COLORS["text"]}" '
        f'letter-spacing="0.08em" '
        f'dominant-baseline="auto">{_esc(text)}</text>\n'
        # hairline rule
        f'<line x1="{rule_x}" y1="16" x2="{W}" y2="16" '
        f'stroke="{COLORS["border"]}" stroke-width="1"/>\n'
        f'</svg>\n'
    )


def make_heading_svg_clean(text: str, b64: str | None = None) -> str:
    """Generate heading SVG, optionally embedding font."""
    if b64:
        face = (
            f'@font-face{{'
            f'font-family:"JB";'
            f'src:url("data:font/woff2;base64,{b64}") format("woff2");'
            f'}}'
        )
    else:
        face = (
            '@font-face{'
            'font-family:"JB";'
            'src:local("JetBrains Mono"),local("Courier New");'
            '}'
        )

    # Use uppercase for a more architectural, premium feel
    label_text = text.upper()
    
    char_w  = 7.74  
    fs      = 11
    # Wide tracking: extra spacing per char
    letter_spacing = 0.2
    text_w  = int(len(label_text) * char_w * (fs / 12.9) * (1 + letter_spacing)) + 12
    rule_x  = text_w + 12

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>',
        f'{face}',
        f'@keyframes fadeRight {{',
        f'  from {{ opacity: 0; transform: translateX(-4px); }}',
        f'  to {{ opacity: 1; transform: translateX(0); }}',
        f'}}',
        f'g.animate-in {{ animation: fadeRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }}',
        f'</style>',
        f'<defs>',
        f'  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">',
        f'    <stop offset="0%" stop-color="{COLORS["border"]}" stop-opacity="1"/>',
        f'    <stop offset="100%" stop-color="{COLORS["bg"]}" stop-opacity="1"/>',
        f'  </linearGradient>',
        f'</defs>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<g class="animate-in">',
        # left accent dot instead of bar
        f'<circle cx="2" cy="15.5" r="2" fill="{COLORS["accent"]}"/>',
        # label
        (
            f'<text x="12" y="20" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="{fs}" fill="{COLORS["text_hi"]}" font-weight="600" '
            f'letter-spacing="{letter_spacing}em">{_esc(label_text)}</text>'
        ),
        # gradient hairline rule
        f'<line x1="{rule_x}" y1="15.5" x2="{W}" y2="15.5" stroke="url(#fade)" stroke-width="1"/>',
        f'</g>',
        '</svg>',
    ]
    return "\n".join(lines) + "\n"



def run() -> None:
    ASSETS.mkdir(exist_ok=True)

    # Load font subset if available
    b64_path = FONTS / "heading.b64"
    b64 = b64_path.read_text(encoding="ascii").strip() if b64_path.exists() else None

    for name, text in HEADINGS:
        svg = make_heading_svg_clean(text, b64=b64)
        out = ASSETS / f"{name}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"  wrote {out.name}")

    print(f"Done — {len(HEADINGS)} heading SVGs.")


if __name__ == "__main__":
    run()
