"""
gen_projects.py — Premium product-card SVGs for featured repositories.

Auto-fetches public repos, ranks them by impact score, and generates
Apple-style product cards: typographic cover, description, tech tags, metrics.
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

# Hand-curated priority for the showcase (auto-fallback if not found)
PRIORITY = [
    "advance-innovators-school",
    "shop-management",
    "pdf-to-excel",
    "ydp-website",
    "deepfakelive",
    "fawadullah-monkeytalkie",
    "eden-school-system",
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
    indexed = {r["name"].lower(): r for r in repos if not r.get("fork")}
    chosen  = []
    for name in PRIORITY:
        r = indexed.get(name.lower())
        if r:
            chosen.append(r)
        if len(chosen) >= n:
            break
    if len(chosen) < n:
        rest = sorted(
            [r for r in repos if not r.get("fork") and r["name"].lower() not in
             {c["name"].lower() for c in chosen}],
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


def wrap_text(s: str, max_len: int = 85) -> list[str]:
    words, lines, line = s.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 <= max_len:
            line = (line + " " + w).strip()
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


# ── Card layout ───────────────────────────────────────────────────────────────
COVER_H = 80
META_H  = 140
CARD_H  = COVER_H + META_H
CARD_GAP = 16


def make_cover(repo: dict, x: int, y: int, w: int) -> str:
    """Typographic cover — looks like an editorial magazine cover."""
    name = repo["name"].upper().replace("-", " ")
    lang = (repo.get("primaryLanguage") or {}).get("name", "")

    out = ""
    # Cover background with subtle gradient
    out += (
        f'<defs>'
        f'  <linearGradient id="cov{x}" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">'
        f'    <stop offset="0%" stop-color="{COLORS["bg3"]}"/>'
        f'    <stop offset="100%" stop-color="{COLORS["bg2"]}"/>'
        f'  </linearGradient>'
        f'</defs>'
    )
    out += rect_el(x, y, w, COVER_H, fill=f"url(#cov{x})", rx=0)

    # Large typographic name in the cover area
    name_size = 22 if len(name) < 18 else (16 if len(name) < 28 else 13)
    out += text_el(x + 20, y + COVER_H // 2 + name_size // 3,
                   name, size=name_size,
                   color=COLORS["border2"], weight="800", spacing=0.06)

    # Language dot in cover
    if lang:
        out += circle_el(x + w - 24, y + COVER_H - 18, 5, fill=COLORS["accent"], opacity=0.6)
        out += text_el(x + w - 16, y + COVER_H - 14, lang,
                       size=9, color=COLORS["dim"])

    # Accent line at bottom of cover
    out += rect_el(x, y + COVER_H - 2, w, 2, fill=COLORS["accent"], rx=0, opacity=0.3)
    return out


def card_svg(repo: dict, cx: int, cy: int, cw: int) -> str:
    name   = repo.get("name", "unknown")
    desc   = repo.get("description") or "No description."
    stars  = repo.get("stargazers_count", 0)
    forks  = repo.get("forks_count", 0)
    pushed = fmt_date(repo.get("pushed_at"))
    url    = repo.get("html_url", "#")

    out = group_open(cls="a-up")

    # Card shell
    out += rect_el(cx, cy, cw, CARD_H, fill=COLORS["bg2"],
                   rx=RADIUS["lg"], stroke=COLORS["border"], sw=1)

    # Cover
    out += make_cover(repo, cx, cy, cw)

    # Description area
    meta_y = cy + COVER_H + 16
    out += text_el(cx + 16, meta_y, name,
                   size=13, color=COLORS["text_hi"], weight="600")

    desc_lines = wrap_text(desc, max_len=40 if cw < 420 else 82)
    for li, dl in enumerate(desc_lines[:2]):
        out += text_el(cx + 16, meta_y + 22 + li * 16,
                       dl, size=11, color=COLORS["text_sec"])

    # Metrics footer
    fy = cy + CARD_H - 20
    out += text_el(cx + 16, fy, f"★ {stars}",
                   size=10, color=COLORS["text_sec"])
    out += text_el(cx + 60, fy, f"⑂ {forks}",
                   size=10, color=COLORS["dim"])
    out += text_el(cx + cw - 16, fy, pushed,
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


# ── Placeholder (offline / no token) ──────────────────────────────────────────
PLACEHOLDER_REPOS = [
    {"name": "advance-innovators-school", "description": "Full-stack school management platform with AI features.", "stargazers_count": 5, "forks_count": 1, "pushed_at": "2024-06-01", "html_url": "#", "primaryLanguage": {"name": "Python"}, "fork": False},
    {"name": "shop-management",           "description": "Point-of-sale & inventory system built with React + FastAPI.", "stargazers_count": 8, "forks_count": 2, "pushed_at": "2024-07-12", "html_url": "#", "primaryLanguage": {"name": "TypeScript"}, "fork": False},
    {"name": "pdf-to-excel",              "description": "AI-powered PDF extraction pipeline exporting structured data.", "stargazers_count": 3, "forks_count": 0, "pushed_at": "2024-04-22", "html_url": "#", "primaryLanguage": {"name": "Python"}, "fork": False},
    {"name": "ydp-website",               "description": "Production-grade organisation website with CMS.", "stargazers_count": 2, "forks_count": 0, "pushed_at": "2024-03-15", "html_url": "#", "primaryLanguage": {"name": "HTML"}, "fork": False},
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
