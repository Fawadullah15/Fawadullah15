"""
gen_contact.py — Premium contact / connect SVG.

Minimal, elegant contact section with icon-label pairs.
Feels like the footer of a premium portfolio site.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, staggered
)

W, H = 820, 120

LINKS = [
    ("GitHub",   "github.com/Fawadullah15",         "GH"),
    ("Email",    "fawadullah9911@gmail.com",          "✉"),
    ("Location", "Pakistan  ·  Open to Remote / Japan", "◎"),
]


def icon_badge(x: int, y: int, glyph: str, size: int = 14) -> str:
    """A circle badge with a glyph inside."""
    r = 16
    out  = circle_el(x, y, r, fill=COLORS["bg3"])
    out += rect_el(x - r, y - r, r * 2, r * 2,
                   fill="none", stroke=COLORS["border"], rx=r, sw=1)
    out += text_el(x, y + 5, glyph, size=size, color=COLORS["text_sec"],
                   anchor="middle", weight="500")
    return out


def make_contact() -> str:
    out = svg_open(W, H)

    # Divider top
    out += line_el(20, 1, W - 20, 1, stroke=COLORS["border"], opacity=0.6)

    item_w = W // len(LINKS)
    for i, (label, value, glyph) in enumerate(LINKS):
        x = i * item_w + item_w // 2
        delay = staggered(i, 0.0, 0.08)

        out += group_open(cls="a-up", delay=delay)
        # Icon
        out += icon_badge(x, 44, glyph)
        # Label
        out += text_el(x, 76, label.upper(),
                       size=9, color=COLORS["dim"], anchor="middle", spacing=0.1)
        # Value
        out += text_el(x, 94, value,
                       size=10, color=COLORS["text_sec"], anchor="middle")
        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "contact.svg"
    p.write_text(make_contact(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
