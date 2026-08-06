"""
gen_skills.py — Animated skill grid SVG.

Categorized skills rendered as elegant tag clouds.
No boring badge walls. Each category has its own visual block.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, line_el,
    group_open, group_close, _esc, staggered
)

W = 820

SKILL_GROUPS = [
    {
        "label": "AI / ML",
        "skills": ["LangChain", "LangGraph", "MCP", "OpenAI API", "LLMs", "RAG", "Agents", "ML"],
    },
    {
        "label": "Backend",
        "skills": ["Python", "FastAPI", "REST API", "SQLite", "Docker", "Linux", "Git"],
    },
    {
        "label": "Frontend",
        "skills": ["React", "TypeScript", "JavaScript", "Vite", "Tailwind CSS", "HTML/CSS"],
    },
    {
        "label": "Tools & DevOps",
        "skills": ["GitHub Actions", "Git", "VS Code", "Postman", "Docker Compose"],
    },
]

PILL_H    = 26
PILL_PAD  = 12
PILL_GAP  = 8
ROW_GAP   = 10
GROUP_GAP = 24
GROUP_TOP = 8
LABEL_H   = 20


def skill_pill(x: int, y: int, text: str, is_ai: bool = False) -> tuple[str, int]:
    """Returns (svg_str, pill_width)."""
    # ~7px per char at size 11
    w = int(len(text) * 7.0) + PILL_PAD * 2
    fill   = COLORS["accent_bg"] if is_ai else COLORS["bg3"]
    stroke = COLORS["accent"] if is_ai else COLORS["border"]
    tc     = COLORS["accent_hi"] if is_ai else COLORS["text_sec"]

    svg = (
        rect_el(x, y, w, PILL_H, fill=fill, rx=RADIUS["pill"], stroke=stroke, sw=1) +
        text_el(x + PILL_PAD, y + 17, text, size=11, color=tc, weight="500")
    )
    return svg, w


def make_skills() -> str:
    # Pre-calculate total height
    rows_per_group = []
    for grp in SKILL_GROUPS:
        # Estimate rows needed
        cx = 0
        rows = 1
        for sk in grp["skills"]:
            w = int(len(sk) * 7.0) + PILL_PAD * 2
            if cx + w > W - 4:
                rows += 1
                cx = 0
            cx += w + PILL_GAP
        rows_per_group.append(rows)

    total_h = GROUP_TOP
    for rows in rows_per_group:
        total_h += LABEL_H + ROW_GAP + rows * (PILL_H + ROW_GAP) + GROUP_GAP
    total_h += 10

    out = svg_open(W, total_h)

    y_cursor = GROUP_TOP
    for gi, grp in enumerate(SKILL_GROUPS):
        is_ai = gi == 0
        g_delay = staggered(gi, 0.0, 0.15)

        out += group_open(cls="a-up", delay=g_delay)

        # Group label
        out += text_el(0, y_cursor + LABEL_H - 4, grp["label"],
                       size=10, color=COLORS["accent_hi"] if is_ai else COLORS["dim"],
                       weight="600", spacing=0.12)

        y_cursor += LABEL_H + ROW_GAP

        # Wrap pills
        cx = 0
        cy = y_cursor
        for si, sk in enumerate(grp["skills"]):
            pill_svg, pw = skill_pill(cx, cy, sk, is_ai=is_ai)
            if cx + pw > W - 4:
                cx = 0
                cy += PILL_H + ROW_GAP
            pill_svg, pw = skill_pill(cx, cy, sk, is_ai=is_ai)
            out += pill_svg
            cx += pw + PILL_GAP

        row_count = rows_per_group[gi]
        y_cursor = cy + PILL_H + GROUP_GAP

        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "skills.svg"
    p.write_text(make_skills(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
