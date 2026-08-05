"""
gen_projects.py — Generate project cards SVG.

Reads public repos from GitHub REST API, selects the best ones, and draws
a 2×2 grid of project cards.

Output: assets/projects.svg  (800 × 320)

Standard library only.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from utils import ASSETS, COLORS, _esc, font_face, rest_get

# ─────────────────────────────────────────────────────────────────────────────
# Fetch & select
# ─────────────────────────────────────────────────────────────────────────────

# Hand-curated ordering: repos that best represent the work
PRIORITY = [
    "advance-innovators-school",
    "deepfakelive",
    "eden-school-system",
    "fawadullah-monkeytalkie",
    "shop-management",
    "pdf-to-excel",
    "ydp-website",
    "fawadullah-portfolio",
]


def select_repos(repos: list[dict], n: int = 4) -> list[dict]:
    """
    Select the best n repos to showcase.
    Priority: PRIORITY list first, then stars desc, then recency.
    Skip forks and empty repos.
    """
    indexed: dict[str, dict] = {r["name"].lower(): r for r in repos}
    chosen = []

    for name in PRIORITY:
        if name.lower() in indexed:
            r = indexed[name.lower()]
            if not r["fork"]:
                chosen.append(r)
        if len(chosen) >= n:
            break

    if len(chosen) < n:
        # Fill remaining from starred/recent
        remaining = sorted(
            [r for r in repos if r["name"].lower() not in {c["name"].lower() for c in chosen}
             and not r["fork"]],
            key=lambda r: (-r["stargazers_count"], r["pushed_at"]),
            reverse=False,
        )
        chosen.extend(remaining[:n - len(chosen)])

    return chosen[:n]


def get_lang_display(repo: dict) -> str:
    lang = repo.get("language") or "—"
    return lang


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        d = datetime.strptime(iso[:10], "%Y-%m-%d")
        return d.strftime("%b %Y")
    except Exception:
        return iso[:10]


def truncate(s: str, n: int) -> str:
    if not s:
        return "no description"
    return s if len(s) <= n else s[:n - 1] + "…"


# ─────────────────────────────────────────────────────────────────────────────
# Language colors (matches gen_stats.py)
# ─────────────────────────────────────────────────────────────────────────────

LANG_COLORS = {
    "Python":       "#3776ab",
    "TypeScript":   "#3178c6",
    "JavaScript":   "#f7df1e",
    "HTML":         "#e44d26",
    "CSS":          "#1572b6",
    "Rust":         "#dea584",
    "Go":           "#00add8",
}


def lang_color(name: str) -> str:
    return LANG_COLORS.get(name, COLORS["dim"])


# ─────────────────────────────────────────────────────────────────────────────
# SVG card builder
# ─────────────────────────────────────────────────────────────────────────────

W, H    = 800, 320
CARD_W  = 370
CARD_H  = 134
GAP     = 20
MARGIN  = 20


def card_svg(repo: dict, cx: int, cy: int) -> list[str]:
    """Generate SVG elements for one project card at position (cx, cy)."""
    name  = repo["name"]
    desc  = truncate(repo.get("description") or "", 72)
    lang  = get_lang_display(repo)
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    pushed = fmt_date(repo.get("pushed_at"))
    url   = repo.get("html_url", "")
    lcolor = lang_color(lang)

    lines = []
    # Card background
    lines.append(
        f'<rect x="{cx}" y="{cy}" width="{CARD_W}" height="{CARD_H}" '
        f'fill="{COLORS["bg2"]}" rx="6" '
        f'stroke="{COLORS["border"]}" stroke-width="1"/>'
    )
    # Top accent bar
    lines.append(
        f'<rect x="{cx}" y="{cy}" width="{CARD_W}" height="2" '
        f'fill="{COLORS["accent"]}" rx="2"/>'
    )

    px = cx + 16
    # Repo name
    lines.append(
        f'<text x="{px}" y="{cy + 22}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="13" fill="{COLORS["text_hi"]}" font-weight="600">'
        f'{_esc(name)}</text>'
    )

    # Description (may wrap — split into max 2 lines of 42 chars)
    words = desc.split()
    lines_text: list[str] = [""]
    for word in words:
        if len(lines_text[-1]) + len(word) + 1 <= 44:
            lines_text[-1] = (lines_text[-1] + " " + word).strip()
        else:
            if len(lines_text) < 2:
                lines_text.append(word)
            else:
                lines_text[-1] = lines_text[-1][:-1] + "…"
                break

    for li, line_text in enumerate(lines_text[:2]):
        lines.append(
            f'<text x="{px}" y="{cy + 40 + li * 16}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="10.5" fill="{COLORS["dim"]}">{_esc(line_text)}</text>'
        )

    # Bottom row: language dot + name
    by = cy + CARD_H - 16
    lines.append(
        f'<circle cx="{px + 4}" cy="{by}" r="4" fill="{lcolor}"/>'
    )
    lines.append(
        f'<text x="{px + 14}" y="{by + 4}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="10" fill="{COLORS["dim"]}">{_esc(lang)}</text>'
    )

    # Stars
    star_x = px + 90
    lines.append(
        f'<text x="{star_x}" y="{by + 4}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="10" fill="{COLORS["dim"]}">★ {stars}</text>'
    )

    # Forks
    fork_x = star_x + 50
    lines.append(
        f'<text x="{fork_x}" y="{by + 4}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="10" fill="{COLORS["dim"]}">⑂ {forks}</text>'
    )

    # Last pushed
    pushed_x = cx + CARD_W - 16
    lines.append(
        f'<text x="{pushed_x}" y="{by + 4}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["muted"]}" text-anchor="end">{_esc(pushed)}</text>'
    )

    return lines


def gen_projects(repos: list[dict]) -> str:
    selected = select_repos(repos, n=4)

    # 2×2 layout positions
    positions = [
        (MARGIN,                   20),
        (MARGIN + CARD_W + GAP,    20),
        (MARGIN,                   20 + CARD_H + GAP),
        (MARGIN + CARD_W + GAP,    20 + CARD_H + GAP),
    ]

    svg_h = 20 + CARD_H * 2 + GAP + 16

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{svg_h}" viewBox="0 0 {W} {svg_h}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{svg_h}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{svg_h}" fill="{COLORS["accent"]}" rx="0"/>',
    ]

    for i, repo in enumerate(selected):
        cx, cy = positions[i]
        out.extend(card_svg(repo, cx, cy))

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run() -> None:
    login = os.environ.get("GH_LOGIN", "Fawadullah15")
    ASSETS.mkdir(exist_ok=True)

    print(f"  Fetching repos for @{login}...")
    repos = rest_get(f"/users/{login}/repos?per_page=100&type=public")
    if not isinstance(repos, list):
        raise RuntimeError(f"Unexpected API response: {repos}")

    print(f"  Found {len(repos)} public repos.")

    svg = gen_projects(repos)
    out = ASSETS / "projects.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  Wrote {out} ({len(svg):,} bytes)")
    print("Done.")


if __name__ == "__main__":
    run()
