"""
gen_timeline.py — Animated career timeline SVG.

Stripe-style vertical timeline with glowing nodes for active roles.
Reflects Fawadullah Imraj's genuine journey:
- Quantum AI (CEO & Co-Founder)
- Monkey Doo (Founder & AI Engineer)
- University of Peshawar (BS Artificial Intelligence)
- Nebula X Cosmos (Entrepreneurial Initiative)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, staggered
)

W = 820

TIMELINE = [
    {
        "year":    "2024 – Present",
        "role":    "Chief Executive Officer & Co-Founder",
        "org":     "Quantum AI",
        "type":    "leadership",
        "active":  True,
        "points":  [
            "Leading technical vision, AI automation architecture, and client engineering",
            "Spearheading multi-agent pipelines and enterprise software systems",
            "Production deployments at quantumaitech.vercel.app",
        ],
    },
    {
        "year":    "2023 – Present",
        "role":    "Founder & Lead AI Engineer",
        "org":     "Monkey Doo",
        "type":    "work",
        "active":  True,
        "points":  [
            "Building custom offline-first desktop and retail shop management software",
            "Engineering automated inventory, billing, and reporting workflows",
            "Direct product ownership and client software consulting",
        ],
    },
    {
        "year":    "2022 – Present",
        "role":    "BS Artificial Intelligence",
        "org":     "University of Peshawar",
        "type":    "education",
        "active":  True,
        "points":  [
            "Core focus: Machine Learning, Agentic Architectures, Algorithms & System Design",
            "Active in university incubation developing Mechanical Engineering AI Copilot",
            "HEC / DLSEI / Coursera academic program coordination",
        ],
    },
    {
        "year":    "2023",
        "role":    "Entrepreneurial Initiative",
        "org":     "Nebula X Cosmos",
        "type":    "milestone",
        "active":  False,
        "points":  [
            "Early venture exploration in autonomous digital systems and technical solutions",
            "Architected foundational concepts for multi-service automation platforms",
        ],
    },
]

NODE_X    = 32
LINE_X    = NODE_X
CONTENT_X = 70
ITEM_H    = 130
DOT_R     = 7
LINE_COL  = COLORS["border"]


def timeline_node(y: int, active: bool) -> str:
    """Glowing circle for active, simple for past."""
    out = ""
    if active:
        # Outer pulse ring
        out += (
            f'<circle cx="{NODE_X}" cy="{y}" r="11" fill="none" '
            f'stroke="{COLORS["accent"]}" stroke-width="1.5" opacity="0.4" class="a-pulse"/>\n'
        )
        # Inner solid dot
        out += circle_el(NODE_X, y, 5, fill=COLORS["accent"])
    else:
        out += circle_el(NODE_X, y, 4, fill=COLORS["border2"])
    return out


def make_timeline() -> str:
    total_h = len(TIMELINE) * ITEM_H + 20
    out = svg_open(W, total_h)

    # ── Vertical connecting line ──────────────────────────────
    last_y = (len(TIMELINE) - 1) * ITEM_H + 30
    out += line_el(LINE_X, 30, LINE_X, last_y, stroke=LINE_COL, sw=1.5)

    for i, item in enumerate(TIMELINE):
        y = i * ITEM_H + 30
        delay = staggered(i, 0.0, 0.1)

        out += group_open(cls="a-up", delay=delay)

        # Node dot
        out += timeline_node(y, item["active"])

        # Year badge
        y_c = COLORS["accent"] if item["active"] else COLORS["dim"]
        out += text_el(CONTENT_X, y - 6, item["year"].upper(),
                       size=9, color=y_c, weight="600", spacing=0.08)

        # Role & Org
        out += text_el(CONTENT_X, y + 14, item["role"],
                       size=14, color=COLORS["text_hi"], weight="600")

        # Org tag
        org_c = COLORS["accent_hi"] if item["active"] else COLORS["text_sec"]
        out += text_el(CONTENT_X + len(item["role"]) * 8.5 + 12, y + 14,
                       f"·  {item['org']}",
                       size=12, color=org_c, weight="400")

        # Bullet points
        for bi, pt in enumerate(item["points"]):
            by = y + 36 + bi * 20
            out += circle_el(CONTENT_X + 2, by - 3, 2, fill=COLORS["dim"])
            out += text_el(CONTENT_X + 12, by, pt,
                           size=11, color=COLORS["text_sec"], weight="400")

        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "timeline.svg"
    p.write_text(make_timeline(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
