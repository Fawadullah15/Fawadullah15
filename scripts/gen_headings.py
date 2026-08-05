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

    char_w  = 7.74  # JetBrains Mono advance at font-size 12.9
    fs      = 12
    text_w  = int(len(text) * char_w * (fs / 12.9)) + 16
    rule_x  = text_w + 8

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{face}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        # left accent bar
        f'<rect x="0" y="9" width="2" height="13" fill="{COLORS["accent"]}" rx="1"/>',
        # label
        (
            f'<text x="9" y="21" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="{fs}" fill="{COLORS["dim"]}" '
            f'letter-spacing="0.06em">{_esc(text)}</text>'
        ),
        # hairline rule
        f'<line x1="{rule_x}" y1="16" x2="{W - 1}" y2="16" stroke="{COLORS["border"]}" stroke-width="1"/>',
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
