"""
gen_building.py — "Currently Building" section SVG.

A premium, editorial showcase of active projects / research areas.
Feels like an AI startup's "What we're working on" page.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, TYPE, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, staggered
)

W = 820

# ── Data ──────────────────────────────────────────────────────────────────────
PROJECTS = [
    {
        "name":    "Multi-Agent AI System",
        "status":  "active",
        "tag":     "LangGraph  ·  MCP  ·  FastAPI",
        "desc":    "Orchestrated agent networks with persistent memory, tool use, and autonomous task decomposition.",
        "pct":     72,
    },
    {
        "name":    "AI SaaS Platform",
        "status":  "building",
        "tag":     "React  ·  FastAPI  ·  SQLite",
        "desc":    "Production-grade SaaS with LLM-powered features, billing, and multi-tenant architecture.",
        "pct":     45,
    },
    {
        "name":    "Open Source AI Tooling",
        "status":  "research",
        "tag":     "Python  ·  LangChain  ·  MCP",
        "desc":    "Reusable primitives and composable agents for the open source AI engineering community.",
        "pct":     30,
    },
]

STATUS_COLORS = {
    "active":   COLORS["accent"],
    "building": "#F59E0B",
    "research": COLORS["text_sec"],
}

STATUS_LABELS = {
    "active":   "Active",
    "building": "In Progress",
    "research": "Research",
}

# Card dimensions
CARD_W  = 820
CARD_H  = 110
CARD_GAP = 12


def progress_bar(x: int, y: int, pct: int, w: int = 200, delay: float = 0.0) -> str:
    bar_h   = 3
    filled  = int(w * pct / 100)
    track_c = COLORS["bg3"]
    fill_c  = COLORS["accent"]
    out = ""
    # Track
    out += rect_el(x, y, w, bar_h, fill=track_c, rx=2)
    # Fill — animated grow
    out += (
        f'<rect x="{x}" y="{y}" width="{filled}" height="{bar_h}" '
        f'rx="2" fill="{fill_c}" '
        f'style="animation:grow 1s cubic-bezier(0.16,1,0.3,1) {delay:.2f}s forwards;'
        f'transform:scaleX(0);transform-origin:{x}px center;"/>\n'
    )
    return out


def make_building() -> str:
    H = len(PROJECTS) * (CARD_H + CARD_GAP) + 20
    out = svg_open(W, H)

    for i, p in enumerate(PROJECTS):
        y0    = i * (CARD_H + CARD_GAP) + 10
        delay = staggered(i, 0.0, 0.12)
        sc    = STATUS_COLORS.get(p["status"], COLORS["dim"])
        sl    = STATUS_LABELS.get(p["status"], p["status"])

        # Card
        out += group_open(cls="a-up", delay=delay)

        # Card background with subtle accent-tinted left border
        out += rect_el(0, y0, CARD_W, CARD_H, fill=COLORS["bg2"],
                       rx=RADIUS["lg"], stroke=COLORS["border"], sw=1)
        # Left accent stripe
        out += rect_el(0, y0, 3, CARD_H, fill=COLORS["accent"], rx=0)

        # Status pill (top-right)
        pill_w = 90
        out += rect_el(CARD_W - pill_w - 20, y0 + 16, pill_w, 22,
                       fill=COLORS["bg3"], rx=RADIUS["pill"],
                       stroke=sc, sw=1)
        out += circle_el(CARD_W - pill_w - 6, y0 + 27, 4, fill=sc)
        out += text_el(CARD_W - pill_w + 2, y0 + 30, sl,
                       size=9, color=sc, weight="500")

        # Project name
        out += text_el(20, y0 + 30, p["name"],
                       size=15, color=COLORS["text_hi"], weight="600")

        # Tech tag
        out += text_el(20, y0 + 50, p["tag"],
                       size=10, color=COLORS["accent_hi"], weight="500", spacing=0.04)

        # Description
        out += text_el(20, y0 + 70, p["desc"],
                       size=11, color=COLORS["text_sec"])

        # Progress bar + percentage
        bar_w = 160
        bar_y = y0 + 90
        out += progress_bar(20, bar_y, p["pct"], w=bar_w, delay=delay + 0.3)
        out += text_el(20 + bar_w + 10, bar_y + 8, f"{p['pct']}%",
                       size=9, color=COLORS["dim"], weight="500")

        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "building.svg"
    p.write_text(make_building(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
