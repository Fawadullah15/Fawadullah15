"""
gen_skills.py — Animated skill grid SVG.

Categorized competencies rendered as clean, high-density pill groups.
Focuses strictly on verified skills: AI Engineering, Agentic Systems,
Backend Architecture, Full-Stack, and DevOps/Pipelines.
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
        "label": "AI & Agentic Systems",
        "skills": ["LangChain", "LangGraph", "Model Context Protocol (MCP)", "RAG Architecture", "Multi-Agent Systems", "Deterministic Tool Calling", "OpenAI API", "Hugging Face"],
    },
    {
        "label": "Backend Engineering & Automation",
        "skills": ["Python", "FastAPI", "RESTful APIs", "Workflow Automation", "SQLite", "PostgreSQL", "Docker", "Linux Shell"],
    },
    {
        "label": "Full-Stack Development",
        "skills": ["React", "Next.js", "TypeScript", "JavaScript", "Tailwind CSS", "HTML5/CSS3", "Vite"],
    },
    {
        "label": "Architecture & Engineering Tooling",
        "skills": ["System Design", "Git & GitHub", "GitHub Actions CI/CD", "Postman", "API Integration", "CAD Formula Integration"],
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

    curr_y = GROUP_TOP
    pill_idx = 0

    for g_idx, grp in enumerate(SKILL_GROUPS):
        delay = staggered(g_idx, 0.0, 0.08)
        out += group_open(cls="a-up", delay=delay)

        # Section label
        out += text_el(0, curr_y + 14, grp["label"].upper(),
                       size=10, color=COLORS["dim"], weight="600", spacing=0.08)

        # Subtle separator
        out += line_el(0, curr_y + 20, W, curr_y + 20,
                       stroke=COLORS["border"], opacity=0.4)

        curr_y += LABEL_H + ROW_GAP

        # Pills layout
        cx = 0
        cy = curr_y
        is_ai_grp = ("AI" in grp["label"])

        for sk in grp["skills"]:
            w = int(len(sk) * 7.0) + PILL_PAD * 2
            if cx + w > W:
                cx = 0
                cy += PILL_H + ROW_GAP

            p_svg, pw = skill_pill(cx, cy, sk, is_ai=is_ai_grp)
            out += p_svg
            cx += pw + PILL_GAP
            pill_idx += 1

        curr_y = cy + PILL_H + GROUP_GAP
        out += group_close()

    out += svg_close()
    return out


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / "skills.svg"
    p.write_text(make_skills(), encoding="utf-8")
    print(f"  wrote {p.name}  ({p.stat().st_size:,} bytes)")
