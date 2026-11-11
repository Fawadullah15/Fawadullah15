"""
gen_projects.py — Premium product-card SVGs for featured repositories.

Auto-fetches public repos, ranks them by impact score, and generates
Apple-style product cards: typographic cover, description, tech tags, metrics.
Features prioritized real projects:
- mech-copilot
- Quantum_AI
- Jarvis
- Shop-Management-System
- Paper-to-Prep
- OmniRoute
"""

import sys, os
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, staggered, rest_get
)

W = 820

# Hand-curated priority for the showcase (matched case-insensitively)
PRIORITY = [
    "mech-copilot",
    "quantum_ai",
    "jarvis",
    "shop-management-system",
    "paper-to-prep",
    "omniroute",
    "advance-innovators-school",
    "medbillservices",
    "ydp-website",
    "fawadullah-portfolio",
]

# Monochrome accent shades for language dots (premium, not rainbow)
LANG_SHADES = [
    COLORS["accent_hi"], COLORS["text_hi"], COLORS["text_sec"],
    COLORS["dim"],       COLORS["muted"],   COLORS["border2"],
]


def score(repo: dict) -> float:
    stars  = repo.get("stargazers_count", 0)
    forks  = repo.get("forks_count", 0)
    pushed = repo.get("pushed_at", "")
    s      = stars * 10 + forks * 5
    if pushed:
        try:
            dt      = datetime.strptime(pushed[:10], "%Y-%m-%d")
            days    = (datetime.utcnow() - dt).days
            s      += max(0, 60 - days)
        except Exception:
            pass
    return s


def select_repos(repos: list, n: int = 4) -> list:
    indexed = {r["name"].lower().replace("_", "-"): r for r in repos if not r.get("fork")}
    # Also index raw names
    for r in repos:
        if not r.get("fork"):
            indexed[r["name"].lower()] = r

    chosen  = []
    for name in PRIORITY:
        norm_name = name.lower()
        r = indexed.get(norm_name) or indexed.get(norm_name.replace("_", "-"))
        if r and r not in chosen:
            chosen.append(r)
        if len(chosen) >= n:
            break

    if len(chosen) < n:
        rest = sorted(
            [r for r in repos if not r.get("fork") and r not in chosen],
            key=score, reverse=True
        )
        chosen.extend(rest[:n - len(chosen)])
    return chosen[:n]


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%b %Y")
    except Exception:
        return iso[:10]


CARD_H = 148
CARD_GAP = 14


def card_svg(repo: dict, cx: int, cy: int, cw: int) -> str:
    name   = repo.get("name", "Untitled")
    desc   = repo.get("description") or "Production engineering and intelligent software system."
    stars  = repo.get("stargazers_count", 0)
    forks  = repo.get("forks_count", 0)
    lang   = (repo.get("primaryLanguage") or {}).get("name") or repo.get("language") or "Python"
    pushed = fmt_date(repo.get("pushed_at"))

    # Truncate description cleanly
    if len(desc) > 85:
        desc = desc[:82].rstrip() + "…"

    out = group_open(cls="a-up")

    # Card background
    out += rect_el(cx, cy, cw, CARD_H,
                   fill=COLORS["bg2"], rx=RADIUS["lg"],
                   stroke=COLORS["border"], sw=1)

    # Accent top border (1px)
    out += rect_el(cx, cy, cw, 1,
                   fill=COLORS["accent"], rx=0, opacity=0.3)

    # Title
    out += text_el(cx + 20, cy + 34, name,
                   size=15, color=COLORS["text_hi"], weight="600")

    # Description (two lines max)
    out += text_el(cx + 20, cy + 62, desc,
                   size=11, color=COLORS["text_sec"], weight="400")

    # Footer divider
    fy = cy + CARD_H - 36
    out += line_el(cx + 20, fy, cx + cw - 20, fy,
                   stroke=COLORS["border"], opacity=0.4)

    # Language pill
    ly = cy + CARD_H - 18
    out += circle_el(cx + 24, ly - 3, 3.5, fill=COLORS["accent"])
    out += text_el(cx + 34, ly, lang,
                   size=10, color=COLORS["text_sec"], weight="500")

    # Metrics on the right
    mx = cx + cw - 120
    # Stars
    out += text_el(mx, ly, f"★ {stars}",
                   size=10, color=COLORS["dim"], weight="400")
    # Forks
    out += text_el(mx + 45, ly, f"⑂ {forks}",
                   size=10, color=COLORS["dim"], weight="400")

    # Pushed date
    out += text_el(cx + cw - 16, cy + 34, pushed,
                   size=9, color=COLORS["muted"], anchor="end")

    out += group_close()
    return out


def gen_projects(repos: list) -> str:
    selected = select_repos(repos, n=4)

    # 2-column × 2-row grid
    COL_GAP = 16
    COL_W   = (W - COL_GAP) // 2
    total_h = CARD_H * 2 + CARD_GAP + 10

    out = svg_open(W, total_h)

    positions = [
        (0,              0),
        (COL_W + COL_GAP, 0),
        (0,              CARD_H + CARD_GAP),
        (COL_W + COL_GAP, CARD_H + CARD_GAP),
    ]

    for i, repo in enumerate(selected):
        cx, cy = positions[i]
        out += group_open(cls="a-up", delay=staggered(i, 0.0, 0.1))
        out += card_svg(repo, cx, cy, COL_W).replace(
            group_open(cls="a-up"), ""
        ).replace(group_close(), "", 1)
        out += group_close()

    out += svg_close()
    return out


# ── Authoritative Curated Repos (offline / default) ──────────────────────────
PLACEHOLDER_REPOS = [
    {
        "name": "mech-copilot",
        "description": "AI copilot connecting LLM reasoning with deterministic CAD & mechanical engineering calculations.",
        "stargazers_count": 12,
        "forks_count": 3,
        "pushed_at": "2024-11-10",
        "html_url": "https://github.com/Fawadullah15/mech-copilot",
        "primaryLanguage": {"name": "Python"},
        "fork": False
    },
    {
        "name": "Quantum_AI",
        "description": "Enterprise AI systems, autonomous agentic workflows, and institutional automation architectures.",
        "stargazers_count": 8,
        "forks_count": 2,
        "pushed_at": "2024-10-25",
        "html_url": "https://github.com/Fawadullah15/Quantum_AI",
        "primaryLanguage": {"name": "TypeScript"},
        "fork": False
    },
    {
        "name": "Jarvis",
        "description": "Autonomous desktop and system AI assistant powered by local tool calling and agentic workflows.",
        "stargazers_count": 6,
        "forks_count": 1,
        "pushed_at": "2024-09-18",
        "html_url": "https://github.com/Fawadullah15/Jarvis",
        "primaryLanguage": {"name": "Python"},
        "fork": False
    },
    {
        "name": "Shop-Management-System",
        "description": "Production offline-first desktop management, POS, inventory control, and financial reporting system.",
        "stargazers_count": 9,
        "forks_count": 2,
        "pushed_at": "2024-08-30",
        "html_url": "https://github.com/Fawadullah15/Shop-Management-System",
        "primaryLanguage": {"name": "JavaScript"},
        "fork": False
    },
]


def run() -> None:
    login = os.environ.get("GH_LOGIN", "Fawadullah15")
    ASSETS.mkdir(exist_ok=True)

    try:
        repos = rest_get(f"/users/{login}/repos?per_page=100&type=public")
        if not isinstance(repos, list):
            raise ValueError("Unexpected API response")
        print(f"  {len(repos)} public repos fetched.")
    except Exception as e:
        print(f"  API unavailable ({e}) — using placeholder data.")
        repos = PLACEHOLDER_REPOS

    svg = gen_projects(repos)
    out = ASSETS / "projects.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  wrote {out.name}  ({len(svg):,} bytes)")
    print("Done.")


if __name__ == "__main__":
    run()
