"""
gen_building.py — "Currently Building" section SVG.

A premium, editorial showcase of active projects / flagship systems.
Features Mechanical Engineering Copilot, Quantum AI Enterprise Systems,
and Autonomous Agentic Pipelines.
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
        "name":    "Mechanical Engineering Copilot",
        "status":  "active",
        "tag":     "Python  ·  LangChain  ·  RAG  ·  CAD Calculations",
        "desc":    "AI-powered copilot connecting LLM reasoning with deterministic engineering math, formulas, and CAD design validation.",
        "pct":     78,
    },
    {
        "name":    "Quantum AI Enterprise Automation",
        "status":  "active",
        "tag":     "Multi-Agent Workflows  ·  FastAPI  ·  Next.js",
        "desc":    "Autonomous multi-agent workflows, client business automation, and intelligent ERP/campus management platforms.",
        "pct":     68,
    },
    {
        "name":    "Agentic Tooling & MCP Protocols",
        "status":  "building",
        "tag":     "LangGraph  ·  MCP  ·  FastAPI  ·  Tool Calling",
        "desc":    "Structured multi-agent orchestration with persistent memory, Model Context Protocol servers, and automated pipelines.",
        "pct":     55,
    },
]

STATUS_COLORS = {
    "active":   COLORS["accent"],
    "building": "#F59E0B",
    "research": COLORS["text_sec"],
}

STATUS_LABELS = {
    "active":   "Active Development",
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
    out += rect_el(x, y, w, bar_h, fill=track_c, rx=2)
    out += (
        f'<rect x="{x}" y="{y}" width="{filled}" height="{bar_h}" '
        f'rx="2" fill="{fill_c}" '
        f'style="animation:grow 1s cubic-bezier(0.16,1,0.3,1) {delay:.2f}s forwards;'
        f'transform:scaleX(0);transform-origin:{x}px center;"/>\n'
    )
    return out


def make_building() -> str:
    total_h = len(PROJECTS) * CARD_H + (len(PROJECTS) - 1) * CARD_GAP

    out = svg_open(W, total_h)

    for i, p in enumerate(PROJECTS):
        y = i * (CARD_H + CARD_GAP)
        delay = staggered(i, 0.0, 0.1)

        out += group_open(cls="a-up", delay=delay)

        # Card base
        out += rect_el(0, y, CARD_W, CARD_H,
                       fill=COLORS["bg2"], rx=RADIUS["lg"],
                       stroke=COLORS["border"], sw=1)

        # Status indicator
        sc = STATUS_COLORS[p["status"]]
        sl = STATUS_LABELS[p["status"]]
        out += circle_el(28, y + 26, 4, fill=sc)
        out += text_el(38, y + 29, sl.upper(),
                       size=9, color=sc, weight="500", spacing=0.08)

        # Tech stack pill on right
        out += text_el(CARD_W - 24, y + 29, p["tag"],
                       size=10, color=COLORS["text_sec"], anchor="end", weight="400")

        # Project name
        out += text_el(28, y + 54, p["name"],
                       size=15, color=COLORS["text_hi"], weight="600")

        # Description
        out += text_el(28, y + 74, p["desc"],
                       size=11, color=COLORS["text_sec"], weight="400")

        # Progress bar
        out += text_el(28, y + 97, f"{p['pct']}% Complete",
                       size=9, color=COLORS["dim"], weight="400")
        out += progress_bar(110, y + 92, p["pct"], w=180, delay=delay + 0.3)

        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "building.svg"
    p.write_text(make_building(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
