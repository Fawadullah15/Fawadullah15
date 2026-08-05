"""
gen_placeholder_projects.py
────────────────────────────
Generate a placeholder projects.svg using hardcoded known repos
so the README renders on the first push without a GitHub token.

These will be overwritten by gen_projects.py on the first Action run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import ASSETS, COLORS, _esc, font_face

# Known repos hardcoded from inspection of Fawadullah15's profile
KNOWN_REPOS = [
    {
        "name": "advance-innovators-school",
        "description": "Modern school management system with AI features and real-time dashboards",
        "language": "TypeScript",
        "stargazers_count": 0,
        "forks_count": 0,
        "pushed_at": "2026-03-20T12:48:11Z",
        "html_url": "https://github.com/Fawadullah15/advance-innovators-school",
        "fork": False,
    },
    {
        "name": "deepfakelive",
        "description": "Real-time deepfake video processing pipeline using Python and computer vision",
        "language": "Python",
        "stargazers_count": 1,
        "forks_count": 0,
        "pushed_at": "2025-07-13T11:28:05Z",
        "html_url": "https://github.com/Fawadullah15/deepfakelive",
        "fork": False,
    },
    {
        "name": "eden-school-system",
        "description": "Responsive school website built with HTML, CSS, and JavaScript",
        "language": "HTML",
        "stargazers_count": 1,
        "forks_count": 0,
        "pushed_at": "2025-06-22T11:48:55Z",
        "html_url": "https://github.com/Fawadullah15/eden-school-system",
        "fork": False,
    },
    {
        "name": "fawadullah-monkeytalkie",
        "description": "Collaboration project for Monkey Talkie — deployed on Vercel",
        "language": "HTML",
        "stargazers_count": 0,
        "forks_count": 0,
        "pushed_at": "2025-08-05T06:00:59Z",
        "html_url": "https://github.com/Fawadullah15/fawadullah-monkeytalkie",
        "fork": False,
    },
]

MONO_SHADES = [
    "#ffffff", "#e4e4e7", "#a1a1aa", "#71717a", "#52525b", "#3f3f46", "#27272a", "#18181b"
]

def lang_color(name: str) -> str:
    # Hash the name to pick a consistent monochrome shade
    idx = sum(ord(c) for c in name) % len(MONO_SHADES)
    return MONO_SHADES[idx]


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n-1] + "…"


def fmt_date(iso: str) -> str:
    from datetime import datetime
    try:
        d = datetime.strptime(iso[:10], "%Y-%m-%d")
        return d.strftime("%b %Y")
    except Exception:
        return iso[:10]


W, H    = 800, 320
CARD_W  = 370
CARD_H  = 134
GAP     = 20
MARGIN  = 20

POSITIONS = [
    (MARGIN, 20),
    (MARGIN + CARD_W + GAP, 20),
    (MARGIN, 20 + CARD_H + GAP),
    (MARGIN + CARD_W + GAP, 20 + CARD_H + GAP),
]


def card_svg(repo: dict, cx: int, cy: int) -> list[str]:
    name   = repo["name"]
    desc   = truncate(repo.get("description") or "no description", 72)
    lang   = repo.get("language") or "—"
    stars  = repo.get("stargazers_count", 0)
    forks  = repo.get("forks_count", 0)
    pushed = fmt_date(repo.get("pushed_at", ""))
    lcolor = lang_color(lang)

    lines = []
    
    # Staggered animation delay
    delay = 0.1 * (cx // CARD_W + cy // CARD_H)
    lines.append(f'<g class="animate-in" style="animation-delay: {delay}s">')
    
    lines.append(
        f'<rect x="{cx}" y="{cy}" width="{CARD_W}" height="{CARD_H}" fill="{COLORS["bg2"]}" rx="6" stroke="{COLORS["border"]}" stroke-width="1"/>'
    )

    px = cx + 16
    lines.append(
        f'<text x="{px}" y="{cy+22}" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="13" fill="{COLORS["text_hi"]}" font-weight="600">{_esc(name)}</text>'
    )

    # Description word-wrap
    words = desc.split()
    text_lines: list[str] = [""]
    for word in words:
        if len(text_lines[-1]) + len(word) + 1 <= 44:
            text_lines[-1] = (text_lines[-1] + " " + word).strip()
        else:
            if len(text_lines) < 2:
                text_lines.append(word)
            else:
                text_lines[-1] = text_lines[-1][:-1] + "…"
                break

    for li, ln in enumerate(text_lines[:2]):
        lines.append(
            f'<text x="{px}" y="{cy+40+li*16}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="10.5" fill="{COLORS["dim"]}">{_esc(ln)}</text>'
        )

    by = cy + CARD_H - 16
    lines += [
        f'<circle cx="{px+4}" cy="{by}" r="4" fill="{lcolor}"/>',
        f'<text x="{px+14}" y="{by+4}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="10" fill="{COLORS["dim"]}">{_esc(lang)}</text>',
        f'<text x="{px+90}" y="{by+4}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="10" fill="{COLORS["dim"]}">★ {stars}</text>',
        f'<text x="{px+140}" y="{by+4}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="10" fill="{COLORS["dim"]}">⑂ {forks}</text>',
        f'<text x="{cx+CARD_W-16}" y="{by+4}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["muted"]}" text-anchor="end">{_esc(pushed)}</text>',
    ]
    lines.append('</g>')
    return lines


def run() -> None:
    ASSETS.mkdir(exist_ok=True)
    svg_h = 20 + CARD_H * 2 + GAP + 16
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{svg_h}" viewBox="0 0 {W} {svg_h}">',
        f'<style>{font_face("data")}',
        f'@keyframes fadeUp {{',
        f'  from {{ opacity: 0; transform: translateY(4px); }}',
        f'  to {{ opacity: 1; transform: translateY(0); }}',
        f'}}',
        f'g.animate-in {{ animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }}',
        f'</style>',
        f'<rect width="{W}" height="{svg_h}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{svg_h}" fill="{COLORS["border"]}" rx="0"/>',
    ]

    for i, repo in enumerate(KNOWN_REPOS):
        cx, cy = POSITIONS[i]
        out.extend(card_svg(repo, cx, cy))

    out.append('</svg>')
    svg = "\n".join(out) + "\n"
    path = ASSETS / "projects.svg"
    path.write_text(svg, encoding="utf-8")
    print(f"  wrote projects.svg ({len(svg):,} bytes)")
    print("Done.")


if __name__ == "__main__":
    run()
