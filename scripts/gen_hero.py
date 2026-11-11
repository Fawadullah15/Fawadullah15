"""
gen_hero.py — Cinematic hero banner SVG.

Full-width dark canvas with:
  - Large name typography with accent gradient shimmer
  - Animated status indicator ("● Building Quantum AI & Mech Copilot")
  - Subtle glowing mesh background
  - Role tags with stagger animations
  - Location and university credentials
  - Elegant divider
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, TYPE, RADIUS, EASING,
    svg_open, svg_close, text_el, rect_el, circle_el,
    line_el, group_open, group_close, _esc,
    accent_gradient_h, fade_right_gradient, staggered
)

W, H = 820, 340


def mesh_bg() -> str:
    """Subtle radial glow — creates depth without noise."""
    return (
        '<defs>'
        '<radialGradient id="meshGlow" cx="30%" cy="40%" r="60%" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0%" stop-color="{COLORS["accent"]}" stop-opacity="0.06"/>'
        f'<stop offset="100%" stop-color="{COLORS["bg"]}" stop-opacity="0"/>'
        '</radialGradient>'
        '<radialGradient id="meshGlow2" cx="80%" cy="70%" r="40%" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0%" stop-color="{COLORS["accent_hi"]}" stop-opacity="0.04"/>'
        f'<stop offset="100%" stop-color="{COLORS["bg"]}" stop-opacity="0"/>'
        '</radialGradient>'
        f'{accent_gradient_h("nameGrad")}'
        '</defs>'
        # Mesh glows
        f'<rect width="{W}" height="{H}" fill="url(#meshGlow)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#meshGlow2)"/>'
    )


def status_pill(x: int, y: int) -> str:
    """Animated 'Building' status badge."""
    pill_text = "Building Quantum AI · Mech Copilot"
    w_pill = 240
    return (
        group_open(cls="a-in", delay=0.1) +
        # Pill background
        f'<rect x="{x}" y="{y}" width="{w_pill}" height="26" rx="13" '
        f'fill="{COLORS["accent_bg"]}" stroke="{COLORS["accent"]}" stroke-width="1" opacity="0.9"/>\n'
        # Pulsing dot
        f'<circle cx="{x+16}" cy="{y+13}" r="4" fill="{COLORS["accent"]}" class="a-pulse"/>\n'
        # Text
        + text_el(x+28, y+17, pill_text,
                  size=10, color=COLORS["accent_hi"], weight="500") +
        group_close()
    )


def role_tags(x: int, y: int) -> str:
    """Authoritative role identifiers — staggered fade."""
    roles = ["AI Engineer", "Automation Engineer", "CEO & Co-Founder", "Multi-Agent Systems"]
    out = ""
    cx = x
    for i, role in enumerate(roles):
        delay = staggered(i, 0.5, 0.08)
        pad_x, pad_y = 12, 6
        w_est = int(len(role) * 7.2) + pad_x * 2
        out += group_open(cls="a-up", delay=delay)
        out += rect_el(cx, y, w_est, 28, fill=COLORS["bg3"],
                       rx=RADIUS["md"], stroke=COLORS["border2"], sw=1)
        out += text_el(cx + pad_x, y + 17, role,
                       size=11, color=COLORS["text_sec"], weight="500")
        out += group_close()
        cx += w_est + 8
    return out


def make_hero() -> str:
    out = svg_open(W, H)
    out += mesh_bg()

    # ── Left border accent line ──────────────────────────────
    out += rect_el(0, 0, 3, H, fill=COLORS["accent"], rx=0)

    # ── Status pill ─────────────────────────────────────────
    out += status_pill(32, 36)

    # ── Name — massive cinematic type ───────────────────────
    out += group_open(cls="a-up", delay=0.2)
    # Shadow for depth
    out += text_el(32, 148, "FAWADULLAH",
                   size=72, color=COLORS["bg3"], weight="800", opacity=0.6)
    out += text_el(30, 146, "FAWADULLAH",
                   size=72, color="url(#nameGrad)", weight="800")
    out += group_close()

    out += group_open(cls="a-up", delay=0.3)
    out += text_el(30, 210, "IMRAJ",
                   size=72, color=COLORS["text_hi"], weight="800", spacing=0.04)
    out += group_close()

    # ── Mission line ─────────────────────────────────────────
    out += group_open(cls="a-up", delay=0.4)
    out += text_el(30, 252,
                   "Architecting agentic AI systems, workflow automation, and intelligent engineering platforms.",
                   size=13, color=COLORS["text_sec"], weight="400")
    out += group_close()

    # ── Role tags ────────────────────────────────────────────
    out += role_tags(30, 274)

    # ── Bottom hairline ──────────────────────────────────────
    out += line_el(30, H - 1, W - 30, H - 1,
                   stroke=COLORS["border"], sw=1, opacity=0.6)

    # ── Location tag ─────────────────────────────────────────
    out += group_open(cls="a-in", delay=0.7)
    out += text_el(W - 30, 54, "Peshawar, Pakistan  ·  University of Peshawar",
                   size=10, color=COLORS["dim"], anchor="end", weight="400")
    out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "hero.svg"
    p.write_text(make_hero(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
