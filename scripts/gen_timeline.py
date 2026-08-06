"""
gen_timeline.py — Animated career timeline SVG.

Stripe-style vertical timeline with glowing nodes for active roles.
Education, experience, achievements — tells a story.
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
        "year":    "2024 – Now",
        "role":    "AI Engineer & Full-Stack Developer",
        "org":     "Monkey Doo",
        "type":    "work",
        "active":  True,
        "points":  [
            "Building multi-agent AI systems with LangGraph & MCP",
            "FastAPI microservices architecture",
            "React frontends with real-time AI features",
        ],
    },
    {
        "year":    "2022 – Now",
        "role":    "BS Artificial Intelligence",
        "org":     "University of Peshawar",
        "type":    "education",
        "active":  True,
        "points":  [
            "Machine Learning, Deep Learning, Neural Networks",
            "Software Engineering & System Design",
            "Research in AI agent architectures",
        ],
    },
    {
        "year":    "2023",
        "role":    "Full-Stack Developer",
        "org":     "Independent Projects",
        "type":    "project",
        "active":  False,
        "points":  [
            "Shop Management System (React + FastAPI + SQLite)",
            "YDP Official Website (production)",
            "PDF-to-Excel AI extraction pipeline",
        ],
    },
    {
        "year":    "2021",
        "role":    "Self-Taught Developer",
        "org":     "Open Source",
        "type":    "milestone",
        "active":  False,
        "points":  [
            "First production web application",
            "Began Python & JavaScript journey",
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
        # Outer glow ring
        out += circle_el(NODE_X, y, DOT_R + 5, fill=COLORS["accent"], opacity=0.15)
        out += circle_el(NODE_X, y, DOT_R + 2, fill=COLORS["accent"], opacity=0.25)
        # Inner solid dot
        out += circle_el(NODE_X, y, DOT_R, fill=COLORS["accent"], cls="a-glow")
    else:
        out += circle_el(NODE_X, y, DOT_R - 2, fill=COLORS["muted"])
        out += circle_el(NODE_X, y, DOT_R - 4, fill=COLORS["bg2"])
    return out


def make_timeline() -> str:
    H = len(TIMELINE) * ITEM_H + 40
    out = svg_open(W, H)

    for i, item in enumerate(TIMELINE):
        y0    = i * ITEM_H + 30
        delay = staggered(i, 0.0, 0.15)
        mid_y = y0 + DOT_R

        # Connector line to next item
        if i < len(TIMELINE) - 1:
            next_y = (i + 1) * ITEM_H + 30
            out += line_el(LINE_X, mid_y + DOT_R, LINE_X, next_y - DOT_R,
                           stroke=LINE_COL, sw=1)

        # Node
        out += timeline_node(mid_y, item["active"])

        # Content group
        out += group_open(cls="a-right", delay=delay)

        # Year badge
        year_c = COLORS["accent"] if item["active"] else COLORS["dim"]
        out += text_el(CONTENT_X, y0 + 12, item["year"],
                       size=10, color=year_c, weight="600", spacing=0.08)

        # Role
        out += text_el(CONTENT_X, y0 + 30, item["role"],
                       size=15, color=COLORS["text_hi"], weight="600")

        # Organisation
        org_c = COLORS["accent_hi"] if item["active"] else COLORS["text_sec"]
        out += text_el(CONTENT_X, y0 + 48, item["org"],
                       size=11, color=org_c, weight="500")

        # Bullet points
        for bi, pt in enumerate(item["points"]):
            bullet_y = y0 + 68 + bi * 18
            out += circle_el(CONTENT_X + 4, bullet_y - 4, 2,
                             fill=COLORS["border2"])
            out += text_el(CONTENT_X + 14, bullet_y, pt,
                           size=11, color=COLORS["dim"])

        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "timeline.svg"
    p.write_text(make_timeline(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
